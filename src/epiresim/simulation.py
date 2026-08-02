"""Fragment resampling and phenotype assignment."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ._random import RandomSource, random_integer
from .exceptions import SamplingError
from .types import PenetranceModel, SimulationConfig


def _matlab_round_positive(values: float | NDArray[np.float64]) -> NDArray[np.int64]:
    return np.floor(np.asarray(values) + 0.5).astype(np.int64)


def generate_breakpoints(
    snp_count: int,
    rng: RandomSource,
) -> NDArray[np.int64]:
    """Generate MATLAB-style one-based fragment breakpoints."""

    count = int(_matlab_round_positive(float(rng.random()) * snp_count))
    if count == 0:
        return np.empty(0, dtype=np.int64)
    breaks = _matlab_round_positive(rng.random(count) * snp_count)
    return np.unique(breaks[(breaks > 0) & (breaks <= snp_count)])


def splice_fragments(
    reference: NDArray[np.integer],
    breakpoints: NDArray[np.int64],
    rng: RandomSource,
    mode: str,
) -> NDArray[np.int8]:
    """Splice contiguous SNP fragments from independently selected donors."""

    row_count, snp_count = reference.shape
    if row_count < 2 and mode == "compatibility":
        raise SamplingError("Compatibility resampling requires at least two controls.")
    if row_count < 1:
        raise SamplingError("Resampling requires at least one control.")

    if mode == "compatibility":
        donor = int(_matlab_round_positive(float(rng.random()) * (row_count - 2)))
        donor_upper = row_count - 1
    else:
        donor = random_integer(rng, 0, row_count)
        donor_upper = row_count

    output = np.empty(snp_count, dtype=np.int8)
    break_set = set(int(value) for value in breakpoints)
    for one_based_column in range(1, snp_count + 1):
        if one_based_column in break_set:
            if mode == "compatibility":
                new_donor = 0
                for _ in range(100_000):
                    new_donor = int(
                        _matlab_round_positive(float(rng.random()) * (row_count - 1))
                    )
                    if new_donor != 0:
                        break
                if new_donor == 0:
                    raise SamplingError(
                        "Compatibility donor selection exceeded its safety limit."
                    )
                donor = new_donor - 1
            else:
                donor = random_integer(rng, 0, donor_upper)
        output[one_based_column - 1] = reference[donor, one_based_column - 1]
    return output


def assign_phenotype(
    genotypes: NDArray[np.integer],
    model: PenetranceModel,
    rng: RandomSource,
) -> int:
    """Draw a binary phenotype from the penetrance indexed by causal genotypes."""

    index = 0
    for locus in model.loci:
        index = index * 3 + int(genotypes[locus]) - 1
    probability = float(model.penetrance[index])
    return int(float(rng.random()) <= probability)


def _draw_candidate(
    controls: NDArray[np.integer],
    model: PenetranceModel,
    rng: RandomSource,
    mode: str,
) -> tuple[NDArray[np.int8], int]:
    breakpoints = generate_breakpoints(controls.shape[1], rng)
    genotype = splice_fragments(controls, breakpoints, rng, mode)
    return genotype, assign_phenotype(genotype, model, rng)


def _simulate_strict(
    controls: NDArray[np.integer],
    model: PenetranceModel,
    config: SimulationConfig,
    rng: RandomSource,
) -> tuple[NDArray[np.int8], int]:
    rows: list[NDArray[np.int8]] = []
    case_count = 0
    control_count = 0
    attempts = 0
    while case_count < config.case_count or control_count < config.control_count:
        attempts += 1
        if attempts > config.max_sampling_attempts:
            raise SamplingError(
                "Strict resampling could not satisfy case/control quotas within "
                f"{config.max_sampling_attempts} attempts."
            )
        genotype, status = _draw_candidate(controls, model, rng, "strict")
        if status == 1 and case_count < config.case_count:
            rows.append(np.concatenate((genotype, np.array([1], dtype=np.int8))))
            case_count += 1
        elif status == 0 and control_count < config.control_count:
            rows.append(np.concatenate((genotype, np.array([0], dtype=np.int8))))
            control_count += 1
    return np.vstack(rows), attempts


def _simulate_compatibility(
    controls: NDArray[np.integer],
    model: PenetranceModel,
    config: SimulationConfig,
    rng: RandomSource,
) -> tuple[NDArray[np.int8], int]:
    target_rows = config.case_count + config.control_count
    matrix = np.zeros((target_rows, controls.shape[1] + 1), dtype=np.int8)
    allocated_rows = 0
    current_index = 0
    case_count = 0
    control_count = 0
    attempts = 0

    while current_index < target_rows:
        attempts += 1
        if attempts > config.max_sampling_attempts:
            raise SamplingError(
                "Compatibility resampling exceeded its safety limit while reproducing "
                "the MATLAB quota loop."
            )
        current_index += 1
        if current_index < 1:
            raise SamplingError(
                "The MATLAB-compatible quota rollback reached an invalid row index."
            )
        allocated_rows = max(allocated_rows, current_index)
        genotype, status = _draw_candidate(controls, model, rng, "compatibility")
        matrix[current_index - 1, :-1] = genotype

        if status == 1:
            if case_count < config.case_count:
                matrix[allocated_rows - 1, -1] = 1
                case_count += 1
            else:
                current_index -= 2
        elif control_count < config.control_count:
            matrix[allocated_rows - 1, -1] = 0
            control_count += 1
        else:
            current_index -= 1

    return matrix[:allocated_rows], attempts


def simulate_dataset(
    controls: NDArray[np.integer],
    model: PenetranceModel,
    config: SimulationConfig,
    rng: RandomSource,
) -> tuple[NDArray[np.int8], int]:
    """Generate one matrix using the selected compatibility or strict sampler."""

    if config.mode == "compatibility":
        return _simulate_compatibility(controls, model, config, rng)
    return _simulate_strict(controls, model, config, rng)
