"""Build, validate, inspect, and convert EpiReSIM reference bundles."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any, TextIO, cast

import numpy as np
from numpy.typing import NDArray
from scipy import io as scipy_io

from .exceptions import InputValidationError, OutputCollisionError

REFERENCE_FORMAT = "epiresim-reference"
REFERENCE_FORMAT_VERSION = 1
GENOTYPE_FILE = "genotypes.npy"
VARIANT_FILE = "variants.tsv"
SAMPLE_FILE = "samples.tsv"
MANIFEST_FILE = "manifest.json"
GENOTYPE_ENCODING = "counted-allele-dosage-0-1-2"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _open_text(path: Path) -> TextIO:
    if path.name.endswith((".gz", ".bgz")):
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def _write_tsv(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def _read_tsv(path: Path) -> tuple[list[str], list[list[str]]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.reader(stream, delimiter="\t")
            header = next(reader)
            return header, [row for row in reader]
    except (OSError, StopIteration, UnicodeError, csv.Error) as error:
        raise InputValidationError(
            f"Unable to read reference metadata file: {path.name}"
        ) from error


def _prepare_output(output: Path) -> None:
    if output.exists():
        raise OutputCollisionError(f"Reference output already exists: {output}")
    output.mkdir(parents=True)


def _write_bundle(
    output: Path,
    genotypes: NDArray[np.int8],
    variants: Sequence[Mapping[str, object]],
    samples: Sequence[Mapping[str, object]],
    *,
    genome_build: str,
    source: Mapping[str, object],
    filters: Mapping[str, object],
) -> Path:
    _prepare_output(output)
    genotype_path = output / GENOTYPE_FILE
    variant_path = output / VARIANT_FILE
    sample_path = output / SAMPLE_FILE

    np.save(genotype_path, genotypes, allow_pickle=False)
    _write_tsv(
        variant_path,
        (
            "chrom",
            "position",
            "id",
            "ref",
            "alt",
            "counted_allele",
            "counted_allele_frequency",
            "source_alt_flipped",
        ),
        (
            (
                item["chrom"],
                item["position"],
                item["id"],
                item["ref"],
                item["alt"],
                item["counted_allele"],
                f"{float(cast(Any, item['counted_allele_frequency'])):.17g}",
                str(bool(item["flipped"])).lower(),
            )
            for item in variants
        ),
    )
    _write_tsv(
        sample_path,
        ("sample_id", "population"),
        ((item["sample_id"], item.get("population", "")) for item in samples),
    )

    manifest: dict[str, object] = {
        "format": REFERENCE_FORMAT,
        "format_version": REFERENCE_FORMAT_VERSION,
        "genotype_encoding": GENOTYPE_ENCODING,
        "genome_build": genome_build,
        "sample_count": int(genotypes.shape[0]),
        "variant_count": int(genotypes.shape[1]),
        "created_utc": datetime.now(UTC).isoformat(),
        "source": dict(source),
        "filters": dict(filters),
        "files": {
            GENOTYPE_FILE: {"sha256": _sha256(genotype_path)},
            VARIANT_FILE: {"sha256": _sha256(variant_path)},
            SAMPLE_FILE: {"sha256": _sha256(sample_path)},
        },
    }
    (output / MANIFEST_FILE).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    validate_reference_bundle(output)
    return output


def _load_sample_metadata(
    path: Path,
    sample_column: str,
    population_column: str,
) -> dict[str, str]:
    try:
        with _open_text(path) as stream:
            reader = csv.DictReader(stream, delimiter="\t")
            if reader.fieldnames is None or sample_column not in reader.fieldnames:
                raise InputValidationError(
                    f"Sample metadata must contain column {sample_column!r}."
                )
            if population_column not in reader.fieldnames:
                raise InputValidationError(
                    f"Sample metadata must contain column {population_column!r}."
                )
            result: dict[str, str] = {}
            for row in reader:
                sample_id = cast(str, row[sample_column])
                if not sample_id:
                    raise InputValidationError("Sample metadata contains an empty sample ID.")
                if sample_id in result:
                    raise InputValidationError(
                        f"Sample metadata contains duplicate ID {sample_id!r}."
                    )
                result[sample_id] = cast(str, row[population_column])
            return result
    except (OSError, UnicodeError, csv.Error) as error:
        raise InputValidationError(f"Unable to read sample metadata: {path}") from error


def _load_sample_ids(path: Path) -> set[str]:
    try:
        with _open_text(path) as stream:
            return {
                line.strip().split()[0]
                for line in stream
                if line.strip() and not line.startswith("#")
            }
    except (OSError, UnicodeError) as error:
        raise InputValidationError(f"Unable to read sample list: {path}") from error


def build_reference_from_vcf(
    vcf_path: str | Path,
    output: str | Path,
    *,
    genome_build: str,
    chromosome: str | None = None,
    sample_file: str | Path | None = None,
    sample_metadata: str | Path | None = None,
    population: str | None = None,
    sample_column: str = "sample",
    population_column: str = "population",
    min_maf: float = 0.0,
    include_filtered: bool = False,
    source_name: str | None = None,
    source_url: str | None = None,
    source_release: str | None = None,
) -> Path:
    """Build a one-chromosome native reference bundle from hard-call VCF genotypes."""

    source_path = Path(vcf_path)
    output_path = Path(output)
    if not source_path.is_file():
        raise InputValidationError(f"VCF input does not exist: {source_path}")
    if not genome_build.strip():
        raise InputValidationError("Genome build must be recorded for VCF references.")
    if not 0.0 <= min_maf <= 0.5:
        raise InputValidationError("Minimum MAF must be in the interval [0, 0.5].")
    if population is not None and sample_metadata is None:
        raise InputValidationError("Population selection requires sample metadata.")

    populations = (
        _load_sample_metadata(Path(sample_metadata), sample_column, population_column)
        if sample_metadata is not None
        else {}
    )
    requested_samples = _load_sample_ids(Path(sample_file)) if sample_file is not None else None

    header_samples: list[str] | None = None
    selected_indices: list[int] = []
    selected_samples: list[str] = []
    genotype_columns: list[NDArray[np.int8]] = []
    variants: list[dict[str, object]] = []
    observed_chromosome: str | None = None
    last_position: int | None = None
    skipped = {"filtered": 0, "non_biallelic_snp": 0, "missing_or_non_diploid": 0, "maf": 0}

    try:
        with _open_text(source_path) as stream:
            for raw_line in stream:
                if raw_line.startswith("##"):
                    continue
                if raw_line.startswith("#CHROM"):
                    fields = raw_line.rstrip("\n\r").split("\t")
                    header_samples = fields[9:]
                    for index, sample_id in enumerate(header_samples):
                        if requested_samples is not None and sample_id not in requested_samples:
                            continue
                        if population is not None and populations.get(sample_id) != population:
                            continue
                        selected_indices.append(index)
                        selected_samples.append(sample_id)
                    if requested_samples is not None:
                        missing_samples = requested_samples.difference(header_samples)
                        if missing_samples:
                            raise InputValidationError(
                                f"Requested sample IDs absent from the VCF: {len(missing_samples)}"
                            )
                    if not selected_samples:
                        raise InputValidationError(
                            "No VCF samples matched the requested selection."
                        )
                    continue
                if raw_line.startswith("#") or not raw_line.strip():
                    continue
                if header_samples is None:
                    raise InputValidationError("VCF header line '#CHROM' was not found.")
                fields = raw_line.rstrip("\n\r").split("\t")
                if len(fields) < 9 + len(header_samples):
                    raise InputValidationError(
                        "VCF record has fewer sample fields than its header."
                    )
                (
                    chrom,
                    position,
                    identifier,
                    ref,
                    alt,
                    _qual,
                    filter_value,
                    _info,
                    format_value,
                ) = fields[:9]
                if chromosome is not None and chrom != chromosome:
                    continue
                if observed_chromosome is None:
                    observed_chromosome = chrom
                elif chrom != observed_chromosome:
                    raise InputValidationError(
                        "A native reference bundle must contain exactly one chromosome; "
                        "select one with --chromosome."
                    )
                numeric_position = int(position)
                if last_position is not None and numeric_position <= last_position:
                    raise InputValidationError(
                        "VCF variants must have strictly increasing positions within "
                        "the chromosome."
                    )
                last_position = numeric_position
                if not include_filtered and filter_value not in {"PASS", "."}:
                    skipped["filtered"] += 1
                    continue
                if ref.upper() not in {"A", "C", "G", "T"} or alt.upper() not in {
                    "A",
                    "C",
                    "G",
                    "T",
                }:
                    skipped["non_biallelic_snp"] += 1
                    continue
                format_fields = format_value.split(":")
                if "GT" not in format_fields:
                    raise InputValidationError("VCF records must contain the FORMAT/GT field.")
                gt_index = format_fields.index("GT")
                dosages = np.empty(len(selected_indices), dtype=np.int8)
                valid = True
                for output_index, input_index in enumerate(selected_indices):
                    sample_fields = fields[9 + input_index].split(":")
                    if gt_index >= len(sample_fields):
                        valid = False
                        break
                    alleles = sample_fields[gt_index].replace("|", "/").split("/")
                    if len(alleles) != 2 or any(allele not in {"0", "1"} for allele in alleles):
                        valid = False
                        break
                    dosages[output_index] = sum(allele == "1" for allele in alleles)
                if not valid:
                    skipped["missing_or_non_diploid"] += 1
                    continue
                alt_frequency = float(np.sum(dosages)) / (2.0 * len(dosages))
                flipped = alt_frequency > 0.5
                maf = 1.0 - alt_frequency if flipped else alt_frequency
                if maf < min_maf:
                    skipped["maf"] += 1
                    continue
                if flipped:
                    dosages = np.asarray(2 - dosages, dtype=np.int8)
                genotype_columns.append(dosages)
                variants.append(
                    {
                        "chrom": chrom,
                        "position": numeric_position,
                        "id": identifier,
                        "ref": ref,
                        "alt": alt,
                        "counted_allele": ref if flipped else alt,
                        "counted_allele_frequency": maf,
                        "flipped": flipped,
                    }
                )
    except (OSError, UnicodeError, ValueError) as error:
        raise InputValidationError(f"Unable to parse VCF input: {source_path}") from error

    if header_samples is None:
        raise InputValidationError("VCF header line '#CHROM' was not found.")
    if not genotype_columns:
        raise InputValidationError("No eligible biallelic, complete diploid SNPs remained.")
    matrix = np.column_stack(genotype_columns).astype(np.int8, copy=False)
    sample_rows = [
        {"sample_id": sample_id, "population": populations.get(sample_id, "")}
        for sample_id in selected_samples
    ]
    source: dict[str, object] = {
        "kind": "vcf",
        "sha256": _sha256(source_path),
    }
    if source_name is not None:
        source["name"] = source_name
    if source_url is not None:
        source["url"] = source_url
    if source_release is not None:
        source["release"] = source_release
    return _write_bundle(
        output_path,
        matrix,
        variants,
        sample_rows,
        genome_build=genome_build,
        source=source,
        filters={
            "chromosome": observed_chromosome,
            "population": population,
            "minimum_maf": min_maf,
            "include_filtered": include_filtered,
            "missing_genotypes": "exclude_variant",
            "skipped_variant_counts": skipped,
        },
    )


def _cell_scalar(value: object) -> object:
    current = value
    while isinstance(current, np.ndarray) and current.size == 1:
        current = current.reshape(-1)[0]
    return current


def import_mat_reference(
    mat_path: str | Path,
    output: str | Path,
    *,
    genome_build: str = "unknown",
) -> Path:
    """Convert legacy MATLAB ``pts`` and ``SampleInfo`` variables to a native bundle."""

    source_path = Path(mat_path)
    if not source_path.is_file():
        raise InputValidationError(f"MATLAB input does not exist: {source_path}")
    try:
        content = scipy_io.loadmat(source_path)
    except (OSError, ValueError, NotImplementedError) as error:
        raise InputValidationError(f"Unable to read MATLAB v5 reference: {source_path}") from error
    if "pts" not in content or "SampleInfo" not in content:
        raise InputValidationError("MATLAB reference must contain 'pts' and 'SampleInfo'.")
    genotypes = np.asarray(content["pts"])
    sample_info = np.asarray(content["SampleInfo"], dtype=object)
    if genotypes.ndim != 2 or genotypes.shape[0] == 0 or genotypes.shape[1] == 0:
        raise InputValidationError("MATLAB 'pts' must be a non-empty two-dimensional matrix.")
    if not np.issubdtype(genotypes.dtype, np.number) or not np.all(np.isfinite(genotypes)):
        raise InputValidationError("MATLAB 'pts' must contain finite numeric genotype codes.")
    if np.any((genotypes < 1) | (genotypes > 3) | (genotypes != np.floor(genotypes))):
        raise InputValidationError("MATLAB 'pts' genotype codes must be integers 1, 2, or 3.")
    if (
        sample_info.ndim != 2
        or sample_info.shape[0] != genotypes.shape[0]
        or sample_info.shape[1] < 5
    ):
        raise InputValidationError("MATLAB 'SampleInfo' dimensions do not match 'pts'.")
    try:
        numeric_labels = [
            float(cast(Any, _cell_scalar(item))) for item in sample_info[:, 4]
        ]
    except (TypeError, ValueError) as error:
        raise InputValidationError("MATLAB 'SampleInfo' contains invalid class labels.") from error
    if any(not np.isfinite(label) or not label.is_integer() for label in numeric_labels):
        raise InputValidationError("MATLAB 'SampleInfo' contains invalid class labels.")
    labels = np.asarray(numeric_labels, dtype=np.int64)
    control_indices = np.flatnonzero(labels == 2)
    if control_indices.size == 0:
        raise InputValidationError("MATLAB reference contains no control samples with label 2.")
    controls = np.asarray(genotypes[control_indices] - 1, dtype=np.int8)

    sample_rows = [
        {"sample_id": f"sample_{index + 1}", "population": ""}
        for index in range(controls.shape[0])
    ]
    variants: list[dict[str, object]] = []
    for column in range(controls.shape[1]):
        maf = float(np.sum(controls[:, column])) / (2.0 * controls.shape[0])
        variants.append(
            {
                "chrom": "unknown",
                "position": column + 1,
                "id": f"variant_{column + 1}",
                "ref": ".",
                "alt": ".",
                "counted_allele": ".",
                "counted_allele_frequency": maf,
                "flipped": False,
            }
        )
    return _write_bundle(
        Path(output),
        controls,
        variants,
        sample_rows,
        genome_build=genome_build,
        source={
            "kind": "matlab-v5",
            "sha256": _sha256(source_path),
            "control_label": 2,
        },
        filters={"sample_selection": "legacy control label 2"},
    )


def _read_manifest(path: Path) -> dict[str, Any]:
    try:
        content = json.loads((path / MANIFEST_FILE).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InputValidationError("Reference manifest is missing or invalid JSON.") from error
    if not isinstance(content, dict):
        raise InputValidationError("Reference manifest must be a JSON object.")
    return cast(dict[str, Any], content)


def validate_reference_bundle(path: str | Path) -> dict[str, Any]:
    """Validate bundle schema, checksums, metadata dimensions, and genotype codes."""

    bundle = Path(path)
    if not bundle.is_dir():
        raise InputValidationError(f"Native reference bundle does not exist: {bundle}")
    manifest = _read_manifest(bundle)
    if manifest.get("format") != REFERENCE_FORMAT:
        raise InputValidationError("Unrecognized native reference format.")
    if manifest.get("format_version") != REFERENCE_FORMAT_VERSION:
        raise InputValidationError(
            f"Unsupported native reference format version: {manifest.get('format_version')!r}"
        )
    if manifest.get("genotype_encoding") != GENOTYPE_ENCODING:
        raise InputValidationError("Unsupported native reference genotype encoding.")
    if not isinstance(manifest.get("genome_build"), str) or not manifest["genome_build"]:
        raise InputValidationError("Reference manifest must record a genome build.")
    if not isinstance(manifest.get("source"), dict):
        raise InputValidationError("Reference manifest source metadata is invalid.")
    if not isinstance(manifest.get("filters"), dict):
        raise InputValidationError("Reference manifest filter metadata is invalid.")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise InputValidationError("Reference manifest does not contain file checksums.")
    for filename in (GENOTYPE_FILE, VARIANT_FILE, SAMPLE_FILE):
        item = files.get(filename)
        component = bundle / filename
        if not component.is_file() or not isinstance(item, dict):
            raise InputValidationError(f"Reference component is missing: {filename}")
        if item.get("sha256") != _sha256(component):
            raise InputValidationError(f"Reference checksum mismatch: {filename}")
    try:
        genotypes = np.load(bundle / GENOTYPE_FILE, allow_pickle=False, mmap_mode="r")
    except (OSError, ValueError) as error:
        raise InputValidationError("Unable to read native genotype matrix.") from error
    if genotypes.ndim != 2 or genotypes.shape[0] == 0 or genotypes.shape[1] == 0:
        raise InputValidationError("Native genotype matrix must be non-empty and two-dimensional.")
    if genotypes.dtype != np.int8 or np.any((genotypes < 0) | (genotypes > 2)):
        raise InputValidationError("Native genotypes must be int8 minor-allele dosages 0, 1, or 2.")
    variant_header, variant_rows = _read_tsv(bundle / VARIANT_FILE)
    sample_header, sample_rows = _read_tsv(bundle / SAMPLE_FILE)
    if variant_header != [
        "chrom",
        "position",
        "id",
        "ref",
        "alt",
        "counted_allele",
        "counted_allele_frequency",
        "source_alt_flipped",
    ]:
        raise InputValidationError("Native variant metadata header is invalid.")
    if sample_header != ["sample_id", "population"]:
        raise InputValidationError("Native sample metadata header is invalid.")
    if len(variant_rows) != genotypes.shape[1] or len(sample_rows) != genotypes.shape[0]:
        raise InputValidationError("Native metadata dimensions do not match the genotype matrix.")
    if (
        manifest.get("sample_count") != genotypes.shape[0]
        or manifest.get("variant_count") != genotypes.shape[1]
    ):
        raise InputValidationError("Native manifest dimensions do not match the genotype matrix.")
    if any(len(row) != len(variant_header) for row in variant_rows):
        raise InputValidationError("Native variant metadata rows have invalid widths.")
    if any(len(row) != len(sample_header) for row in sample_rows):
        raise InputValidationError("Native sample metadata rows have invalid widths.")
    chromosomes = {row[0] for row in variant_rows}
    if len(chromosomes) != 1:
        raise InputValidationError(
            "Native reference variants must belong to exactly one chromosome."
        )
    if len({row[0] for row in sample_rows}) != len(sample_rows):
        raise InputValidationError("Native sample IDs must be unique.")
    try:
        positions = [int(row[1]) for row in variant_rows]
        mafs = [float(row[6]) for row in variant_rows]
    except ValueError as error:
        raise InputValidationError(
            "Native variant positions or counted-allele frequencies are invalid."
        ) from error
    if any(right <= left for left, right in pairwise(positions)):
        raise InputValidationError("Native variant positions must be strictly increasing.")
    if any(not 0.0 <= maf <= 1.0 for maf in mafs):
        raise InputValidationError(
            "Native counted-allele frequencies must be in the interval [0, 1]."
        )
    if any(row[7] not in {"true", "false"} for row in variant_rows):
        raise InputValidationError("Native variant flip flags must be true or false.")
    return manifest


def load_native_reference_arrays(
    path: str | Path,
) -> tuple[NDArray[np.int8], NDArray[np.object_], list[list[str]], dict[str, Any]]:
    """Return validated native dosages, sample metadata, variants, and manifest."""

    bundle = Path(path)
    manifest = validate_reference_bundle(bundle)
    genotypes = np.asarray(np.load(bundle / GENOTYPE_FILE, allow_pickle=False), dtype=np.int8)
    _sample_header, sample_rows = _read_tsv(bundle / SAMPLE_FILE)
    _variant_header, variant_rows = _read_tsv(bundle / VARIANT_FILE)
    return genotypes, np.asarray(sample_rows, dtype=object), variant_rows, manifest


def inspect_reference_bundle(path: str | Path) -> dict[str, Any]:
    """Return a concise, JSON-serializable description of a validated bundle."""

    manifest = validate_reference_bundle(path)
    return {
        "format": manifest["format"],
        "format_version": manifest["format_version"],
        "genome_build": manifest["genome_build"],
        "sample_count": manifest["sample_count"],
        "variant_count": manifest["variant_count"],
        "source": manifest["source"],
        "filters": manifest["filters"],
    }


def export_mat_reference(path: str | Path, output: str | Path) -> Path:
    """Export a native reference bundle to the legacy MATLAB v5 schema."""

    output_path = Path(output)
    if output_path.exists():
        raise OutputCollisionError(f"MATLAB reference output already exists: {output_path}")
    dosages, samples, variants, _manifest = load_native_reference_arrays(path)
    sample_info = np.empty((dosages.shape[0], 6), dtype=object)
    for index, sample in enumerate(samples):
        sample_info[index] = [sample[0], sample[1], index + 1, "", 2, ""]
    snp_info = np.asarray(variants, dtype=object)
    scipy_io.savemat(
        output_path,
        {
            "pts": np.asarray(dosages + 1, dtype=np.int8),
            "SampleInfo": sample_info,
            "SNPInfo": snp_info,
        },
        format="5",
    )
    return output_path
