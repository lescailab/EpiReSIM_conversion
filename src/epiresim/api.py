"""High-level public API."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from .io import (
    control_mafs,
    load_reference,
    preflight_outputs,
    select_model_loci,
    write_matrix,
    write_model_log,
)
from .simulation import simulate_dataset
from .solvers import solve_penetrance
from .types import PenetranceModel, ReferenceData, SimulationConfig, SimulationResult


def _reference_diagnostics(
    controls: np.ndarray,
    loci: tuple[int, ...],
    model: PenetranceModel,
) -> dict[str, float]:
    hwe_deviation = 0.0
    for locus, maf in zip(loci, model.mafs, strict=True):
        observed = np.bincount(controls[:, locus], minlength=4)[1:4] / controls.shape[0]
        expected = np.array([(1.0 - maf) ** 2, 2.0 * maf * (1.0 - maf), maf**2])
        hwe_deviation = max(hwe_deviation, float(np.max(np.abs(observed - expected))))

    max_correlation = 0.0
    if len(loci) > 1:
        selected = np.asarray(controls[:, loci], dtype=np.float64)
        correlations = np.asarray(np.corrcoef(selected, rowvar=False), dtype=np.float64)
        if correlations.ndim == 2:
            off_diagonal = correlations[~np.eye(len(loci), dtype=bool)]
            finite = off_diagonal[np.isfinite(off_diagonal)]
            if finite.size:
                max_correlation = float(np.max(np.abs(finite)))
    return {
        "max_hwe_frequency_deviation": hwe_deviation,
        "max_abs_causal_locus_correlation": max_correlation,
    }


def simulate(
    reference: ReferenceData | np.ndarray,
    model: PenetranceModel,
    config: SimulationConfig,
    rng: np.random.Generator,
) -> tuple[np.ndarray, int]:
    """Generate one simulated dataset from a validated control matrix."""

    controls = (
        reference.control_genotypes if isinstance(reference, ReferenceData) else reference
    )
    return simulate_dataset(controls, model, config, rng)


def run(config: SimulationConfig) -> SimulationResult:
    """Run the complete load, solve, simulate, and write workflow."""

    rng = np.random.default_rng(config.seed)
    preflight_outputs(config)
    reference = load_reference(config.reference_path, config, rng)
    observed_mafs = control_mafs(reference.control_genotypes)
    loci = select_model_loci(
        observed_mafs,
        config.mafs,
        config.mode,
        rng,
        config.max_maf_search_steps,
    )
    achieved_mafs = observed_mafs[np.asarray(loci)]
    model = solve_penetrance(
        achieved_mafs,
        config.prevalence,
        config.heritability,
        config.mode,
    )
    model = replace(model, loci=loci)
    diagnostics = _reference_diagnostics(reference.control_genotypes, loci, model)

    matrices: list[np.ndarray] = []
    total_attempts = 0
    for replicate in range(1, config.replicates + 1):
        matrix, attempts = simulate(
            reference.control_genotypes,
            model,
            config,
            rng,
        )
        matrices.append(matrix)
        total_attempts += attempts
        for output_format in config.output_formats:
            write_matrix(
                matrix,
                config.output_dir
                / f"{config.output_prefix}_{replicate}.{output_format}",
                output_format,
                config.mode,
            )
    write_model_log(model, config.output_dir)
    diagnostics["sampling_attempts"] = float(total_attempts)

    return SimulationResult(
        matrices=tuple(matrices),
        model=model,
        reference=reference,
        diagnostics=diagnostics,
    )
