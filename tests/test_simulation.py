from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from epiresim import solve_penetrance
from epiresim.exceptions import SamplingError
from epiresim.simulation import (
    assign_phenotype,
    generate_breakpoints,
    simulate_dataset,
    splice_fragments,
)
from epiresim.types import SimulationConfig


def _config(tmp_path: Path, *, cases: int = 8, controls: int = 8) -> SimulationConfig:
    return SimulationConfig(
        reference_path=tmp_path / "reference.mat",
        case_count=cases,
        control_count=controls,
        snp_count=10,
        mafs=(0.2, 0.3),
        prevalence=0.5,
        heritability=None,
        order=2,
        replicates=1,
        output_prefix="simulation",
        output_formats=("mat",),
        seed=99,
        output_dir=tmp_path,
        mode="strict",
        max_sampling_attempts=20_000,
    )


def test_breakpoints_are_sorted_unique_and_in_range() -> None:
    observed = generate_breakpoints(100, np.random.default_rng(10))
    assert np.all(observed[1:] > observed[:-1])
    assert np.all((observed >= 1) & (observed <= 100))


def test_strict_splicing_can_use_last_reference_row() -> None:
    reference = np.vstack(
        [
            np.full(20, 1, dtype=np.int8),
            np.full(20, 2, dtype=np.int8),
            np.full(20, 3, dtype=np.int8),
        ]
    )
    observed_values: set[int] = set()
    rng = np.random.default_rng(2)
    for _ in range(100):
        observed_values.update(splice_fragments(reference, np.array([], dtype=int), rng, "strict"))
    assert observed_values == {1, 2, 3}


def test_phenotype_index_uses_last_locus_fastest() -> None:
    penetrance = np.zeros(9)
    penetrance[5] = 1.0  # genotype codes (2, 3)
    model = replace(
        solve_penetrance([0.2, 0.3], 0.2, mode="strict"),
        penetrance=penetrance,
        loci=(0, 1),
    )
    assert assign_phenotype(np.array([2, 3]), model, np.random.default_rng(1)) == 1
    assert assign_phenotype(np.array([3, 2]), model, np.random.default_rng(1)) == 0


def test_strict_simulation_has_exact_quotas(tmp_path: Path) -> None:
    rng = np.random.default_rng(123)
    controls = rng.choice(np.array([1, 2, 3], dtype=np.int8), size=(100, 10))
    model = replace(
        solve_penetrance([0.2, 0.3], 0.5, mode="strict"),
        penetrance=np.full(9, 0.5),
        loci=(1, 7),
    )
    matrix, attempts = simulate_dataset(controls, model, _config(tmp_path), rng)
    assert matrix.shape == (16, 11)
    assert np.count_nonzero(matrix[:, -1] == 1) == 8
    assert np.count_nonzero(matrix[:, -1] == 0) == 8
    assert attempts >= 16


def test_impossible_sampling_quota_hits_safety_limit(tmp_path: Path) -> None:
    rng = np.random.default_rng(9)
    controls = np.ones((10, 10), dtype=np.int8)
    model = replace(
        solve_penetrance([0.2, 0.3], 0.5, mode="strict"),
        penetrance=np.zeros(9),
        loci=(0, 1),
    )
    config = replace(_config(tmp_path, cases=1, controls=0), max_sampling_attempts=10)
    with pytest.raises(SamplingError, match="quotas"):
        simulate_dataset(controls, model, config, rng)
