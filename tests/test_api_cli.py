from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from epiresim import run
from epiresim.cli import main
from epiresim.types import SimulationConfig


def _config(reference: Path, output_dir: Path) -> SimulationConfig:
    return SimulationConfig(
        reference_path=reference,
        case_count=6,
        control_count=6,
        snp_count=16,
        mafs=(0.15, 0.3),
        prevalence=0.5,
        heritability=0.02,
        order=2,
        replicates=2,
        output_prefix="cohort_a",
        output_formats=("mat", "txt"),
        seed=37,
        output_dir=output_dir,
        mode="strict",
        max_sampling_attempts=50_000,
    )


@pytest.mark.integration
def test_end_to_end_api_is_reproducible(reference_mat: Path, tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first = run(_config(reference_mat, first_dir))
    second = run(_config(reference_mat, second_dir))

    assert len(first.matrices) == 2
    for first_matrix, second_matrix in zip(first.matrices, second.matrices, strict=True):
        np.testing.assert_array_equal(first_matrix, second_matrix)
        assert first_matrix.shape == (12, 17)
    assert (first_dir / "cohort_a_1.mat").is_file()
    assert (first_dir / "cohort_a_2.txt").is_file()
    assert (first_dir / "log.txt").is_file()
    np.testing.assert_array_equal(
        loadmat(first_dir / "cohort_a_1.mat")["SNP"], first.matrices[0]
    )


@pytest.mark.integration
def test_cli_runs_complete_simulation(reference_mat: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "cli"
    exit_code = main(
        [
            "simulate",
            str(reference_mat),
            "--cases",
            "3",
            "--controls",
            "3",
            "--snps",
            "15",
            "--maf",
            "0.15",
            "0.30",
            "--prevalence",
            "0.5",
            "--order",
            "2",
            "--replicates",
            "1",
            "--prefix",
            "simulation",
            "--format",
            "mat",
            "--seed",
            "19",
            "--output-dir",
            str(output_dir),
            "--mode",
            "strict",
        ]
    )
    assert exit_code == 0
    assert (output_dir / "simulation_1.mat").is_file()
