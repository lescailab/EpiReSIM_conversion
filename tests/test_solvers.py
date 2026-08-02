from __future__ import annotations

import numpy as np
import pytest
from scipy.optimize._numdiff import approx_derivative

from epiresim import solve_penetrance
from epiresim.exceptions import InfeasibleModelError, InputValidationError
from epiresim.probabilities import marginal_constraint_matrix
from epiresim.solvers import _gauss_seidel_normal_step


@pytest.mark.parametrize(
    ("mafs", "heritability"),
    [
        ([0.2, 0.3], 0.05),
        ([0.1, 0.2, 0.3], 0.05),
        ([0.1, 0.2, 0.3, 0.4], 0.05),
        ([0.1, 0.15, 0.2, 0.25, 0.3], 0.02),
    ],
)
def test_strict_solver_satisfies_bounded_constraints(
    mafs: list[float], heritability: float
) -> None:
    model = solve_penetrance(mafs, 0.2, heritability, mode="strict")
    assert np.all(model.penetrance >= 0.0)
    assert np.all(model.penetrance <= 1.0)
    assert model.diagnostics["max_marginal_error"] <= 1e-8
    assert model.diagnostics["prevalence_error"] <= 1e-8
    assert model.diagnostics["heritability_error"] <= 1e-6


def test_strict_analytic_variance_jacobian_matches_finite_difference() -> None:
    mafs = np.array([0.2, 0.3])
    prevalence = 0.2
    matrix, weights = marginal_constraint_matrix(mafs)
    values = np.linspace(0.1, 0.3, 9)

    def residual(candidate: np.ndarray) -> np.ndarray:
        return np.concatenate(
            (
                matrix @ candidate - prevalence,
                [weights @ np.square(candidate - prevalence) - 0.01],
            )
        )

    analytic = np.vstack((matrix, 2.0 * weights * (values - prevalence)))
    numeric = approx_derivative(residual, values, method="3-point")
    np.testing.assert_allclose(analytic, numeric, rtol=1e-7, atol=1e-9)


def test_compatibility_gauss_seidel_returns_matlab_previous_iterate() -> None:
    jacobian = np.array([[1.0, 0.0], [1.0, 1.0]])
    residual = np.array([-1.0, 0.0])

    observed = _gauss_seidel_normal_step(
        jacobian,
        residual,
        tolerance=0.1,
        max_iterations=10,
    )

    np.testing.assert_array_equal(observed, np.array([0.875, -0.875]))


def test_compatibility_prevalence_solver_preserves_legacy_shape() -> None:
    model = solve_penetrance([0.1, 0.2, 0.3], 0.3, mode="compatibility")
    assert model.penetrance.shape == (27,)
    assert np.all(model.penetrance >= 0.0)
    assert model.diagnostics["max_marginal_error"] < 0.05


def test_invalid_solver_configuration_is_rejected() -> None:
    with pytest.raises(InputValidationError):
        solve_penetrance([0.2], 0.2, mode="strict")
    with pytest.raises(InputValidationError):
        solve_penetrance([0.2, 0.3], 1.0, mode="strict")
    with pytest.raises(InputValidationError):
        solve_penetrance([0.2, 0.3], 0.2, 0.0, mode="strict")


def test_infeasible_high_heritability_is_rejected() -> None:
    with pytest.raises(InfeasibleModelError):
        solve_penetrance([0.01, 0.01], 0.01, 1.0, mode="strict")
