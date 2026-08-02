from __future__ import annotations

import gzip
import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat, savemat

from epiresim import run
from epiresim.cli import main
from epiresim.exceptions import InputValidationError
from epiresim.reference import (
    build_reference_from_vcf,
    export_mat_reference,
    import_mat_reference,
    inspect_reference_bundle,
    load_native_reference_arrays,
    validate_reference_bundle,
)
from epiresim.types import SimulationConfig


def _config(reference: Path, output_dir: Path, mode: str) -> SimulationConfig:
    return SimulationConfig(
        reference_path=reference,
        case_count=6,
        control_count=6,
        snp_count=24,
        mafs=(0.2, 0.3),
        prevalence=0.2,
        heritability=None,
        order=2,
        replicates=2,
        output_prefix="simulation",
        output_formats=("txt",),
        seed=11,
        output_dir=output_dir,
        mode=mode,  # type: ignore[arg-type]
        max_sampling_attempts=50_000,
    )


@pytest.mark.parametrize("mode", ["compatibility", "strict"])
@pytest.mark.integration
def test_imported_mat_bundle_produces_exact_simulations(
    reference_mat: Path, tmp_path: Path, mode: str
) -> None:
    native_path = import_mat_reference(reference_mat, tmp_path / "reference.epiref")

    legacy = run(_config(reference_mat, tmp_path / "legacy", mode))
    native = run(_config(native_path, tmp_path / "native", mode))

    assert legacy.model.loci == native.model.loci
    np.testing.assert_array_equal(legacy.model.mafs, native.model.mafs)
    np.testing.assert_allclose(legacy.model.penetrance, native.model.penetrance, rtol=0, atol=0)
    for legacy_matrix, native_matrix in zip(legacy.matrices, native.matrices, strict=True):
        np.testing.assert_array_equal(legacy_matrix, native_matrix)


def test_mat_export_round_trip_preserves_control_dosages(
    reference_mat: Path, tmp_path: Path
) -> None:
    native_path = import_mat_reference(reference_mat, tmp_path / "reference.epiref")
    exported = export_mat_reference(native_path, tmp_path / "exported.mat")
    dosages, _samples, _variants, _manifest = load_native_reference_arrays(native_path)

    content = loadmat(exported)
    np.testing.assert_array_equal(content["pts"], dosages + 1)
    labels = np.asarray(
        [int(np.asarray(item).reshape(-1)[0]) for item in content["SampleInfo"][:, 4]]
    )
    np.testing.assert_array_equal(labels, np.full(dosages.shape[0], 2))


def test_vcf_builder_selects_population_and_reorients_minor_allele(tmp_path: Path) -> None:
    vcf = tmp_path / "panel.vcf"
    vcf.write_text(
        "##fileformat=VCFv4.3\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ts1\ts2\ts3\n"
        "1\t10\tv1\tA\tG\t.\tPASS\t.\tGT\t0/1\t0/0\t1/1\n"
        "1\t20\tv2\tC\tT\t.\tPASS\t.\tGT\t1|1\t1|0\t0|0\n"
        "1\t30\tv3\tG\tA\t.\tLowQual\t.\tGT\t0/0\t0/1\t0/1\n"
        "1\t40\tv4\tG\tC\t.\tPASS\t.\tGT\t./.\t0/1\t0/1\n",
        encoding="utf-8",
    )
    metadata = tmp_path / "samples.tsv"
    metadata.write_text("sample\tpopulation\ns1\tpop_a\ns2\tpop_a\ns3\tpop_b\n", encoding="utf-8")

    output = build_reference_from_vcf(
        vcf,
        tmp_path / "panel.epiref",
        genome_build="build_x",
        chromosome="1",
        sample_metadata=metadata,
        population="pop_a",
        min_maf=0.1,
        source_name="reference_panel",
        source_release="release_1",
    )

    dosages, samples, variants, manifest = load_native_reference_arrays(output)
    np.testing.assert_array_equal(dosages, np.array([[1, 0], [0, 1]], dtype=np.int8))
    assert samples[:, 0].tolist() == ["s1", "s2"]
    assert variants[1][5] == "C"
    assert variants[1][7] == "true"
    assert manifest["filters"]["skipped_variant_counts"] == {
        "filtered": 1,
        "maf": 0,
        "missing_or_non_diploid": 1,
        "non_biallelic_snp": 0,
    }
    assert inspect_reference_bundle(output)["source"]["name"] == "reference_panel"


def test_vcf_gz_builder_reads_compressed_input(tmp_path: Path) -> None:
    vcf = tmp_path / "panel.vcf.gz"
    with gzip.open(vcf, "wt", encoding="utf-8") as stream:
        stream.write(
            "##fileformat=VCFv4.3\n"
            "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ts1\ts2\n"
            "1\t10\tv1\tA\tG\t.\tPASS\t.\tGT\t0/1\t0/0\n"
        )

    output = build_reference_from_vcf(
        vcf,
        tmp_path / "panel.epiref",
        genome_build="build_x",
        chromosome="1",
    )

    dosages, _samples, _variants, _manifest = load_native_reference_arrays(output)
    np.testing.assert_array_equal(dosages, np.array([[1], [0]], dtype=np.int8))


def test_bundle_checksum_detects_component_changes(reference_mat: Path, tmp_path: Path) -> None:
    native_path = import_mat_reference(reference_mat, tmp_path / "reference.epiref")
    variants = native_path / "variants.tsv"
    variants.write_text(variants.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(InputValidationError, match="checksum mismatch"):
        validate_reference_bundle(native_path)


def test_manifest_is_versioned_and_does_not_store_input_path(
    reference_mat: Path, tmp_path: Path
) -> None:
    native_path = import_mat_reference(reference_mat, tmp_path / "reference.epiref")
    manifest_text = (native_path / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)

    assert manifest["format"] == "epiresim-reference"
    assert manifest["format_version"] == 1
    assert str(reference_mat) not in manifest_text


def test_mat_import_preserves_legacy_counted_allele_frequency_above_half(
    tmp_path: Path,
) -> None:
    path = tmp_path / "legacy.mat"
    sample_info = np.empty((2, 5), dtype=object)
    sample_info[0] = ["sample_1", "", 1, "", 2]
    sample_info[1] = ["sample_2", "", 2, "", 2]
    savemat(
        path,
        {
            "pts": np.array([[3], [2]], dtype=np.int8),
            "SampleInfo": sample_info,
        },
    )

    native_path = import_mat_reference(path, tmp_path / "reference.epiref")
    dosages, _samples, variants, _manifest = load_native_reference_arrays(native_path)

    np.testing.assert_array_equal(dosages, np.array([[2], [1]], dtype=np.int8))
    assert float(variants[0][6]) == 0.75


def test_native_config_can_be_reused_with_separate_outputs(
    reference_mat: Path, tmp_path: Path
) -> None:
    native_path = import_mat_reference(reference_mat, tmp_path / "reference.epiref")
    config = _config(native_path, tmp_path / "first", "strict")
    first = run(config)
    second = run(replace(config, output_dir=tmp_path / "second"))
    np.testing.assert_array_equal(first.matrices[0], second.matrices[0])


def test_reference_cli_import_inspect_validate_and_export(
    reference_mat: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    native_path = tmp_path / "reference.epiref"
    exported_path = tmp_path / "exported.mat"

    assert main(["reference", "import-mat", str(reference_mat), "--output", str(native_path)]) == 0
    assert main(["reference", "validate", str(native_path)]) == 0
    assert main(["reference", "inspect", str(native_path)]) == 0
    assert main(
        ["reference", "export-mat", str(native_path), "--output", str(exported_path)]
    ) == 0

    output = capsys.readouterr().out
    assert '"format": "epiresim-reference"' in output
    assert exported_path.is_file()
