"""Reference-data loading and compatibility output writing."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray
from scipy import io as scipy_io

from ._random import RandomSource, matlab_randperm_one, random_integer
from .exceptions import InputValidationError, OutputCollisionError
from .types import PenetranceModel, ReferenceData, SimulationConfig


def _matlab_round_positive(value: float | NDArray[np.float64]) -> Any:
    return np.floor(np.asarray(value) + 0.5).astype(np.int64)


def _cell_scalar(value: object) -> object:
    current = value
    while isinstance(current, np.ndarray) and current.size == 1:
        current = current.reshape(-1)[0]
    return current


def _extract_labels(sample_info: NDArray[np.object_], row_count: int) -> NDArray[np.int64]:
    if sample_info.ndim != 2 or sample_info.shape[0] != row_count or sample_info.shape[1] < 5:
        raise InputValidationError(
            "MATLAB variable 'SampleInfo' must have one row per sample and at least five columns."
        )
    labels = np.empty(row_count, dtype=np.int64)
    for row in range(row_count):
        raw = _cell_scalar(sample_info[row, 4])
        try:
            numeric = float(cast(Any, raw))
        except (TypeError, ValueError) as error:
            raise InputValidationError(
                f"SampleInfo row {row + 1} has a non-numeric class label."
            ) from error
        if not math.isfinite(numeric) or not numeric.is_integer():
            raise InputValidationError(
                f"SampleInfo row {row + 1} has an invalid class label."
            )
        labels[row] = int(numeric)
    return labels


def load_reference(
    path: str | Path,
    config: SimulationConfig,
    rng: RandomSource,
) -> ReferenceData:
    """Load and validate the MATLAB reference dataset used for resampling."""

    reference_path = Path(path)
    if not reference_path.is_file():
        raise InputValidationError(f"Reference MATLAB file does not exist: {reference_path}")
    try:
        content = scipy_io.loadmat(reference_path)
    except (OSError, ValueError, NotImplementedError) as error:
        raise InputValidationError(
            f"Unable to read MATLAB v5 reference file: {reference_path}"
        ) from error

    if "pts" not in content or "SampleInfo" not in content:
        raise InputValidationError(
            "Reference file must contain MATLAB variables 'pts' and 'SampleInfo'."
        )
    genotypes = np.asarray(content["pts"])
    if genotypes.ndim != 2 or genotypes.shape[0] == 0 or genotypes.shape[1] == 0:
        raise InputValidationError("'pts' must be a non-empty two-dimensional matrix.")
    if not np.issubdtype(genotypes.dtype, np.number):
        raise InputValidationError("'pts' must contain numeric genotype codes.")
    if not np.all(np.isfinite(genotypes)):
        raise InputValidationError("'pts' contains non-finite genotype values.")
    if np.any((genotypes < 1) | (genotypes > 3) | (genotypes != np.floor(genotypes))):
        raise InputValidationError("'pts' genotype codes must be integers 1, 2, or 3.")
    if config.snp_count > genotypes.shape[1]:
        raise InputValidationError(
            f"Requested {config.snp_count} SNPs from only {genotypes.shape[1]} columns."
        )

    labels = _extract_labels(np.asarray(content["SampleInfo"], dtype=object), genotypes.shape[0])
    available_starts = genotypes.shape[1] - config.snp_count
    if config.mode == "compatibility":
        matlab_span = genotypes.shape[1] - config.snp_count - 1
        if matlab_span < 1:
            raise InputValidationError(
                "Compatibility mode requires at least two more columns than the requested window."
            )
        matlab_start = int(_matlab_round_positive(float(rng.random()) * matlab_span))
        if matlab_start < 1:
            raise InputValidationError(
                "The legacy random window selected MATLAB index zero; retry with another seed."
            )
        window_start = matlab_start - 1
    else:
        window_start = random_integer(rng, 0, available_starts + 1)

    selected = np.asarray(
        genotypes[:, window_start : window_start + config.snp_count], dtype=np.int8
    )
    controls = np.asarray(selected[labels == 2], dtype=np.int8)
    if controls.shape[0] == 0:
        raise InputValidationError("Reference data contains no samples with control label 2.")

    metadata: NDArray[np.object_] | None = None
    if "SNPInfo" in content:
        raw_metadata = np.asarray(content["SNPInfo"], dtype=object)
        if raw_metadata.ndim == 2 and raw_metadata.shape[0] == genotypes.shape[1]:
            metadata = raw_metadata[window_start : window_start + config.snp_count].copy()

    return ReferenceData(
        genotypes=selected,
        labels=labels,
        control_genotypes=controls,
        variant_metadata=metadata,
        name=reference_path.stem,
        window_start=window_start,
    )


def control_mafs(control_genotypes: NDArray[np.integer]) -> NDArray[np.float64]:
    """Calculate minor-allele frequencies for genotype codes 1/2/3."""

    if control_genotypes.ndim != 2 or control_genotypes.shape[0] == 0:
        raise InputValidationError("Control genotype matrix must be non-empty and 2D.")
    heterozygotes = np.count_nonzero(control_genotypes == 2, axis=0)
    minor_homozygotes = np.count_nonzero(control_genotypes == 3, axis=0)
    return np.asarray(
        (heterozygotes + 2.0 * minor_homozygotes)
        / (2.0 * control_genotypes.shape[0]),
        dtype=np.float64,
    )


def select_model_loci(
    mafs: NDArray[np.float64],
    targets: tuple[float, ...],
    mode: str,
    rng: RandomSource,
    max_steps: int,
) -> tuple[int, ...]:
    """Select causal loci by widening the requested MAF tolerance in 0.01 steps."""

    selected: list[int] = []
    for target in targets:
        candidates = np.empty(0, dtype=np.int64)
        for step in range(1, max_steps + 1):
            tolerance = 0.01 * step
            candidates = np.flatnonzero(
                (mafs >= target - tolerance) & (mafs <= target + tolerance)
            )
            if mode == "strict" and selected:
                candidates = candidates[~np.isin(candidates, selected)]
            if candidates.size:
                break
        if candidates.size == 0:
            raise InputValidationError(
                f"No eligible locus found near target MAF {target:.6f}."
            )
        candidate_index = (
            matlab_randperm_one(rng, int(candidates.size))
            if mode == "compatibility"
            else random_integer(rng, 0, int(candidates.size))
        )
        choice = int(candidates[candidate_index])
        selected.append(choice)

    if mode == "strict" and len(set(selected)) != len(selected):
        raise InputValidationError("Strict mode requires distinct causal loci.")
    return tuple(selected)


def planned_output_paths(config: SimulationConfig) -> tuple[Path, ...]:
    paths: list[Path] = []
    for replicate in range(1, config.replicates + 1):
        for output_format in config.output_formats:
            paths.append(
                config.output_dir / f"{config.output_prefix}_{replicate}.{output_format}"
            )
    paths.append(config.output_dir / "log.txt")
    return tuple(paths)


def preflight_outputs(config: SimulationConfig) -> None:
    """Create the output directory and protect strict-mode outputs from overwrites."""

    config.output_dir.mkdir(parents=True, exist_ok=True)
    if config.mode == "strict":
        collisions = [path for path in planned_output_paths(config) if path.exists()]
        if collisions:
            rendered = ", ".join(str(path) for path in collisions)
            raise OutputCollisionError(f"Strict mode refuses to overwrite: {rendered}")


def write_matrix(
    matrix: NDArray[np.integer],
    path: Path,
    output_format: str,
    mode: str,
) -> None:
    """Write one simulated matrix in a legacy-compatible format."""

    if output_format == "mat":
        matrix_dtype = np.float64 if mode == "compatibility" else np.int8
        scipy_io.savemat(
            path,
            {"SNP": np.asarray(matrix, dtype=matrix_dtype)},
            format="5",
            do_compression=mode == "compatibility",
            oned_as="row",
        )
        return

    file_mode = "a" if mode == "compatibility" else "x"
    with path.open(file_mode, encoding="utf-8", newline="\n") as stream:
        for row in matrix:
            stream.write("".join(f"{int(value)}\t" for value in row))
            stream.write("\n")


def format_model_log(model: PenetranceModel) -> str:
    """Format the MATLAB-compatible model information log."""

    lines = [
        f"order:{model.order}",
        "",
        "MAF:" + "".join(f"{value:.6f}\t" for value in model.mafs),
        "",
        "loci:" + "".join(f"{locus + 1:d}\t" for locus in model.loci),
        "",
        "Penetrance:",
    ]
    for index in range(0, model.penetrance.size, 3):
        lines.append(
            "".join(f"{value:.6f}\t" for value in model.penetrance[index : index + 3])
        )
        if (index + 3) % 9 == 0:
            lines.append("")
    lines.extend(
        [
            "",
            f"Prevalence:{model.prevalence:.6f}",
            "",
            f"Heritability:{model.heritability:.6f}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_model_log(model: PenetranceModel, output_dir: Path) -> Path:
    path = output_dir / "log.txt"
    path.write_text(format_model_log(model), encoding="utf-8", newline="\n")
    return path
