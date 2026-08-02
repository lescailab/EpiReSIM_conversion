from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from epiresim import SimulationConfig, genotype_probabilities, run, solve_penetrance
from epiresim.exceptions import InputValidationError

GOLDEN_DIRECTORY = Path(__file__).parents[1] / "golden"
MANIFEST = GOLDEN_DIRECTORY / "manifest.json"


@pytest.mark.compatibility
def test_matlab_golden_manifest_and_checksums() -> None:
    assert MANIFEST.exists(), "The required MATLAB golden manifest is missing."
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["reference_commit"] == "16adb481b5b0223a5d97622e4df61ed6fc5b0c93"
    assert manifest["matlab_release"]
    assert manifest["symbolic_math_toolbox_version"]
    assert manifest["cases"]
    for relative_path, expected in manifest["sha256"].items():
        digest = hashlib.sha256((GOLDEN_DIRECTORY / relative_path).read_bytes()).hexdigest()
        assert digest == expected


@pytest.mark.compatibility
@pytest.mark.parametrize("case_id", [
    "o2_prevalence",
    "o2_heritability",
    "o3_prevalence",
    "o3_heritability",
    "o4_prevalence",
    "o4_heritability",
    "o5_prevalence",
    "o5_heritability",
])
def test_deterministic_matlab_golden(case_id: str) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    case = manifest["deterministic_cases"][case_id]
    golden = loadmat(GOLDEN_DIRECTORY / case["path"], squeeze_me=True)
    mafs = np.asarray(case["mafs"], dtype=np.float64)
    probabilities = genotype_probabilities(mafs)
    np.testing.assert_allclose(
        probabilities,
        np.atleast_1d(golden["genotype_probabilities"]),
        rtol=0.0,
        atol=case["probability_tolerance"],
    )
    expected_status = str(np.asarray(golden["status"]).squeeze())
    try:
        model = solve_penetrance(
            mafs,
            case["prevalence"],
            case["heritability"],
            mode="compatibility",
        )
    except Exception:
        assert expected_status == "error"
        return
    assert expected_status == "success"
    np.testing.assert_allclose(
        model.penetrance,
        np.atleast_1d(golden["penetrance"]),
        rtol=0.0,
        atol=case["penetrance_tolerance"],
    )


@pytest.mark.compatibility
@pytest.mark.parametrize("case_id", [
    "o2_prevalence",
    "o2_heritability",
    "o3_prevalence",
    "o3_heritability",
    "o4_prevalence",
    "o4_heritability",
    "o5_prevalence",
    "o5_heritability",
    "compact_o2_prevalence",
])
def test_end_to_end_matlab_golden(case_id: str, tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    case = manifest["cases"][case_id]
    output_directory = tmp_path / case_id
    config = SimulationConfig(
        reference_path=GOLDEN_DIRECTORY / case["reference"],
        case_count=case["case_count"],
        control_count=case["control_count"],
        snp_count=case["snp_count"],
        mafs=tuple(case["mafs"]),
        prevalence=case["prevalence"],
        heritability=case["heritability"],
        order=len(case["mafs"]),
        replicates=case["replicates"],
        output_prefix="simulation",
        output_formats=("mat", "txt"),
        seed=case["seed"],
        output_dir=output_directory,
        mode="compatibility",
        max_sampling_attempts=1_000_000,
    )
    run(config)

    golden_directory = GOLDEN_DIRECTORY / case["output_directory"]
    for replicate in range(1, case["replicates"] + 1):
        expected = loadmat(
            golden_directory / f"simulation_{replicate}.mat", mat_dtype=True
        )["SNP"]
        observed = loadmat(
            output_directory / f"simulation_{replicate}.mat", mat_dtype=True
        )["SNP"]
        assert observed.dtype == expected.dtype
        np.testing.assert_array_equal(observed, expected)
        assert (output_directory / f"simulation_{replicate}.txt").read_bytes() == (
            golden_directory / f"simulation_{replicate}.txt"
        ).read_bytes()
    assert (output_directory / "log.txt").read_bytes() == (
        golden_directory / "log.txt"
    ).read_bytes()


@pytest.mark.compatibility
@pytest.mark.parametrize("case_id", ["missing_variables", "insufficient_columns"])
def test_expected_failure_golden(case_id: str, tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    case = manifest["failure_cases"][case_id]
    config = SimulationConfig(
        reference_path=GOLDEN_DIRECTORY / case["reference"],
        case_count=1,
        control_count=1,
        snp_count=case["snp_count"],
        mafs=(0.2, 0.3),
        prevalence=0.2,
        heritability=None,
        order=2,
        replicates=1,
        output_prefix="failure",
        output_formats=("mat",),
        seed=101,
        output_dir=tmp_path / case_id,
        mode="compatibility",
    )
    with pytest.raises(InputValidationError):
        run(config)
