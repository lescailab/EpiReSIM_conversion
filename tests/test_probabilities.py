from __future__ import annotations

from itertools import product

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from epiresim import genotype_probabilities
from epiresim.exceptions import InputValidationError
from epiresim.probabilities import (
    genotype_combinations,
    legacy_constraint_matrix,
    marginal_constraint_matrix,
)


def test_two_locus_probability_order_matches_matlab() -> None:
    observed = genotype_probabilities([0.2, 0.3])
    locus_a = [0.64, 0.32, 0.04]
    locus_b = [0.49, 0.42, 0.09]
    expected = np.array([a * b for a in locus_a for b in locus_b])
    np.testing.assert_allclose(observed, expected, rtol=0.0, atol=1e-15)


@given(
    st.lists(
        st.floats(min_value=0.01, max_value=0.5, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=5,
    )
)
def test_joint_probabilities_are_valid(mafs: list[float]) -> None:
    observed = genotype_probabilities(mafs)
    assert np.all(observed >= 0.0)
    assert observed.shape == (3 ** len(mafs),)
    assert abs(float(observed.sum()) - 1.0) <= 1e-12


def test_generic_constraint_rows_are_conditional_probabilities() -> None:
    matrix, weights = marginal_constraint_matrix([0.2, 0.3])
    combinations = genotype_combinations(2)
    assert matrix.shape == (7, 9)
    np.testing.assert_allclose(matrix.sum(axis=1), np.ones(7), atol=1e-15)
    np.testing.assert_allclose(matrix[-1], weights, atol=0.0)
    for locus, genotype in product(range(2), range(3)):
        row = matrix[locus * 3 + genotype]
        assert np.all(row[combinations[:, locus] != genotype] == 0.0)


@pytest.mark.parametrize("order", [2, 3, 5])
def test_legacy_and_generic_constraints_match_except_known_order_four(order: int) -> None:
    mafs = np.linspace(0.1, 0.4, order)
    legacy, _ = legacy_constraint_matrix(mafs)
    generic, _ = marginal_constraint_matrix(mafs)
    np.testing.assert_allclose(legacy, generic, rtol=0.0, atol=1e-15)


def test_order_four_preserves_legacy_fourth_locus_index_map() -> None:
    legacy, _ = legacy_constraint_matrix([0.1, 0.2, 0.3, 0.4])
    generic, _ = marginal_constraint_matrix([0.1, 0.2, 0.3, 0.4])
    np.testing.assert_allclose(legacy[:9], generic[:9], rtol=0.0, atol=1e-15)
    assert not np.allclose(legacy[9:12], generic[9:12])


@pytest.mark.parametrize("bad_mafs", [[], [0.0, 0.2], [0.2, 0.51], [np.nan, 0.2]])
def test_invalid_mafs_fail_loudly(bad_mafs: list[float]) -> None:
    with pytest.raises(InputValidationError):
        genotype_probabilities(bad_mafs)
