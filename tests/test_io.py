from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat, savemat, whosmat

from epiresim._random import compatibility_random_state, matlab_randperm_one
from epiresim.exceptions import InputValidationError, OutputCollisionError
from epiresim.io import (
    control_mafs,
    format_model_log,
    load_reference,
    preflight_outputs,
    select_model_loci,
    write_matrix,
)
from epiresim.solvers import solve_penetrance
from epiresim.types import SimulationConfig


def _config(reference: Path, output_dir: Path, mode: str = "strict") -> SimulationConfig:
    return SimulationConfig(
        reference_path=reference,
        case_count=4,
        control_count=4,
        snp_count=12,
        mafs=(0.2, 0.3),
        prevalence=0.3,
        heritability=None,
        order=2,
        replicates=1,
        output_prefix="simulation",
        output_formats=("mat", "txt"),
        seed=44,
        output_dir=output_dir,
        mode=mode,  # type: ignore[arg-type]
    )


def test_load_reference_extracts_controls_and_window(
    reference_mat: Path, tmp_path: Path
) -> None:
    config = _config(reference_mat, tmp_path)
    reference = load_reference(reference_mat, config, np.random.default_rng(44))
    assert reference.genotypes.shape == (240, 12)
    assert reference.control_genotypes.shape == (200, 12)
    assert reference.labels.shape == (240,)
    assert reference.variant_metadata is not None
    assert np.all(np.isin(reference.genotypes, [1, 2, 3]))


def test_control_maf_formula() -> None:
    controls = np.array([[1, 2], [2, 3], [3, 3]], dtype=np.int8)
    observed = control_mafs(controls)
    np.testing.assert_allclose(observed, [0.5, 5.0 / 6.0])


def test_strict_locus_selection_is_unique() -> None:
    mafs = np.array([0.2, 0.2, 0.3])
    loci = select_model_loci(
        mafs, (0.2, 0.2), "strict", np.random.default_rng(2), 10
    )
    assert len(set(loci)) == 2


def test_matlab_twister_and_randperm_one_match_recorded_oracle_sequence() -> None:
    rng = compatibility_random_state(11)

    assert float(rng.random()) == 0.1802696888767692
    assert matlab_randperm_one(rng, 2) == 0
    assert float(rng.random()) == 0.7249339291921478


def test_matlab_seed_zero_matches_factory_twister_sequence() -> None:
    rng = compatibility_random_state(0)

    np.testing.assert_array_equal(
        rng.random(3),
        np.array([0.8147236863931789, 0.9057919370756192, 0.12698681629350606]),
    )


def test_missing_matlab_variables_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "invalid.mat"
    savemat(path, {"wrong": np.ones((2, 2))})
    with pytest.raises(InputValidationError, match=r"pts.*SampleInfo"):
        load_reference(path, _config(path, tmp_path), np.random.default_rng(1))


def test_invalid_genotype_code_is_rejected(reference_mat: Path, tmp_path: Path) -> None:
    content = loadmat(reference_mat)
    content["pts"][0, 0] = 4
    path = tmp_path / "invalid_code.mat"
    savemat(
        path,
        {
            "pts": content["pts"],
            "SampleInfo": content["SampleInfo"],
            "SNPInfo": content["SNPInfo"],
        },
    )
    with pytest.raises(InputValidationError, match="1, 2, or 3"):
        load_reference(path, _config(path, tmp_path), np.random.default_rng(1))


def test_strict_output_collision_is_rejected(reference_mat: Path, tmp_path: Path) -> None:
    config = _config(reference_mat, tmp_path)
    (tmp_path / "simulation_1.mat").touch()
    with pytest.raises(OutputCollisionError):
        preflight_outputs(config)


def test_matrix_writers_preserve_legacy_schema(tmp_path: Path) -> None:
    matrix = np.array([[1, 2, 3, 0], [3, 2, 1, 1]], dtype=np.int8)
    mat_path = tmp_path / "result.mat"
    txt_path = tmp_path / "result.txt"
    write_matrix(matrix, mat_path, "mat", "strict")
    write_matrix(matrix, txt_path, "txt", "strict")
    loaded = loadmat(mat_path)
    assert set(key for key in loaded if not key.startswith("__")) == {"SNP"}
    np.testing.assert_array_equal(loaded["SNP"], matrix)
    assert txt_path.read_text() == "1\t2\t3\t0\t\n3\t2\t1\t1\t\n"


def test_compatibility_mat_writer_matches_matlab_dtype_and_compression(
    tmp_path: Path,
) -> None:
    matrix = np.array([[1, 2, 3, 0], [3, 2, 1, 1]], dtype=np.int8)
    path = tmp_path / "result.mat"

    write_matrix(matrix, path, "mat", "compatibility")

    assert whosmat(path) == [("SNP", (2, 4), "double")]
    assert int.from_bytes(path.read_bytes()[128:132], byteorder="little") == 15
    np.testing.assert_array_equal(loadmat(path, mat_dtype=True)["SNP"], matrix)


def test_model_log_uses_matlab_indexing_and_six_decimals() -> None:
    model = solve_penetrance([0.2, 0.3], 0.2, mode="strict")
    from dataclasses import replace

    rendered = format_model_log(replace(model, loci=(0, 4)))
    assert "order:2\n" in rendered
    assert "MAF:0.200000\t0.300000\t" in rendered
    assert "loci:1\t5\t" in rendered
    assert "Prevalence:0.200000" in rendered
