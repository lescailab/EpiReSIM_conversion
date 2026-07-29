from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from epiresim.probabilities import marginal_constraint_matrix, model_statistics

MODEL_DIRECTORY = Path(__file__).parents[1] / "8 eNME Models"


def _parse_model(path: Path) -> tuple[np.ndarray, np.ndarray, float, float]:
    text = path.read_text(encoding="utf-8")
    maf_match = re.search(r"MAF:(.*?)loci:", text, flags=re.DOTALL)
    penetrance_match = re.search(r"Penetrance:(.*?)Prevalence:", text, flags=re.DOTALL)
    prevalence_match = re.search(r"Prevalence:([0-9.]+)", text)
    heritability_match = re.search(r"Heritability:([0-9.]+)", text)
    assert maf_match and penetrance_match and prevalence_match and heritability_match
    return (
        np.array([float(value) for value in maf_match.group(1).split()]),
        np.array([float(value) for value in penetrance_match.group(1).split()]),
        float(prevalence_match.group(1)),
        float(heritability_match.group(1)),
    )


@pytest.mark.parametrize("path", sorted(MODEL_DIRECTORY.glob("Model*.txt")))
def test_published_model_statistics_recompute_with_documented_precision(path: Path) -> None:
    mafs, penetrance, expected_prevalence, expected_heritability = _parse_model(path)
    matrix, weights = marginal_constraint_matrix(mafs)
    prevalence, heritability, marginals = model_statistics(penetrance, weights, matrix)

    # The source tables publish MAFs and penetrances to six decimals. The resulting
    # rounding error is largest for the fourth-order examples.
    assert abs(prevalence - expected_prevalence) <= 6e-4
    assert abs(heritability - expected_heritability) <= 6e-3
    assert np.max(np.abs(marginals - prevalence)) < 0.05
