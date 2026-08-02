"""Compatibility and strict penetrance solvers."""

from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy import linalg, optimize

from .exceptions import InfeasibleModelError, InputValidationError
from .probabilities import (
    legacy_constraint_matrix,
    marginal_constraint_matrix,
    model_statistics,
)
from .types import Mode, PenetranceModel

FloatArray = NDArray[np.float64]

STRICT_LINEAR_TOLERANCE = 1e-8
STRICT_HERITABILITY_TOLERANCE = 1e-6


def _gauss_seidel_normal_step(
    jacobian: FloatArray,
    residual: FloatArray,
    *,
    tolerance: float = 1e-4,
    max_iterations: int = 100_000,
) -> FloatArray:
    normal_matrix = jacobian.T @ jacobian
    normal_rhs = jacobian.T @ (-residual)
    lower = np.tril(normal_matrix)
    upper = np.triu(normal_matrix, 1)
    try:
        lower_inverse = linalg.inv(lower)
        iteration_matrix = -lower_inverse @ upper
        intercept = lower_inverse @ normal_rhs
    except linalg.LinAlgError as error:
        raise InfeasibleModelError(
            "Compatibility Newton step produced a singular Gauss-Seidel system."
        ) from error

    step = np.zeros(jacobian.shape[1], dtype=np.float64)
    for _ in range(max_iterations):
        candidate = iteration_matrix @ step + intercept
        if np.max(np.abs(candidate - step)) < tolerance:
            # MATLAB's pre_seidel checks the candidate before assigning it to x,
            # so the converged result is the previous iterate rather than tmp.
            return cast(FloatArray, step)
        if not np.all(np.isfinite(candidate)):
            raise InfeasibleModelError(
                "Compatibility Gauss-Seidel iteration produced non-finite values."
            )
        step = candidate
    raise InfeasibleModelError(
        "Compatibility Gauss-Seidel iteration exceeded its safety limit."
    )


def _compatibility_solution(
    mafs: FloatArray,
    prevalence: float,
    heritability: float | None,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    matrix, weights = legacy_constraint_matrix(mafs)
    target = np.full(matrix.shape[0], prevalence, dtype=np.float64)

    if heritability is None:
        solution, _, _, _ = linalg.lstsq(matrix, target, lapack_driver="gelsy")
    else:
        solution = np.zeros(weights.size, dtype=np.float64)
        step_tolerance, residual_tolerance = {
            2: (0.01, 0.05),
            3: (0.05, 0.05),
            4: (0.03, 0.03),
            5: (0.05, 0.05),
        }[mafs.size]
        target_variance = heritability * prevalence * (1.0 - prevalence)

        for _ in range(10):
            linear_residual = matrix @ solution - target
            variance_residual = float(
                weights @ np.square(solution - prevalence) - target_variance
            )
            residual = np.concatenate((linear_residual, [variance_residual]))
            variance_jacobian = 2.0 * weights * (solution - prevalence)
            jacobian = np.vstack((matrix, variance_jacobian))
            step = _gauss_seidel_normal_step(jacobian, residual)
            solution = solution + step

            new_linear = matrix @ solution - target
            new_variance = float(
                weights @ np.square(solution - prevalence) - target_variance
            )
            new_residual = np.concatenate((new_linear, [new_variance]))
            if np.linalg.norm(step) < step_tolerance or np.linalg.norm(
                new_residual
            ) < residual_tolerance:
                break

    solution = np.asarray(solution, dtype=np.float64)
    solution[solution < 0.0] = 0.0
    return solution, matrix, weights


def _strict_linear_solution(
    matrix: FloatArray,
    target: FloatArray,
) -> FloatArray:
    result = optimize.lsq_linear(
        matrix,
        target,
        bounds=(0.0, 1.0),
        method="trf",
        tol=1e-12,
        lsq_solver="exact",
        max_iter=1_000,
    )
    residual = matrix @ result.x - target
    if not result.success or np.max(np.abs(residual)) > STRICT_LINEAR_TOLERANCE:
        raise InfeasibleModelError(
            "No bounded penetrance table satisfies the prevalence and "
            "no-marginal-effect constraints."
        )
    return np.asarray(result.x, dtype=np.float64)


def _strict_starts(
    matrix: FloatArray,
    linear_solution: FloatArray,
    prevalence: float,
) -> list[FloatArray]:
    starts = [np.clip(linear_solution, 1e-12, 1.0 - 1e-12)]
    constant = np.full(linear_solution.shape, prevalence, dtype=np.float64)
    starts.append(np.clip(constant, 1e-12, 1.0 - 1e-12))

    null_basis = linalg.null_space(matrix)
    for column in range(min(null_basis.shape[1], 6)):
        direction = null_basis[:, column]
        for sign in (-1.0, 1.0):
            signed = sign * direction
            positive = signed > 0
            negative = signed < 0
            limits: list[float] = []
            if np.any(positive):
                limits.append(float(np.min((1.0 - prevalence) / signed[positive])))
            if np.any(negative):
                limits.append(float(np.min((0.0 - prevalence) / signed[negative])))
            if limits:
                scale = 0.8 * min(limits)
                candidate = constant + scale * signed
                starts.append(np.clip(candidate, 1e-12, 1.0 - 1e-12))
    return starts


def _strict_nonlinear_solution(
    matrix: FloatArray,
    weights: FloatArray,
    target: FloatArray,
    prevalence: float,
    heritability: float,
    linear_solution: FloatArray,
) -> FloatArray:
    target_variance = heritability * prevalence * (1.0 - prevalence)

    def residual(values: FloatArray) -> FloatArray:
        variance = float(weights @ np.square(values - prevalence))
        return np.concatenate((matrix @ values - target, [variance - target_variance]))

    def jacobian(values: FloatArray) -> FloatArray:
        return np.vstack((matrix, 2.0 * weights * (values - prevalence)))

    candidates: list[tuple[float, float, FloatArray]] = []
    for start in _strict_starts(matrix, linear_solution, prevalence):
        result = optimize.least_squares(
            residual,
            start,
            jac=jacobian,
            bounds=(0.0, 1.0),
            method="trf",
            ftol=1e-13,
            xtol=1e-13,
            gtol=1e-13,
            max_nfev=20_000,
        )
        candidate_residual = residual(result.x)
        max_linear = float(np.max(np.abs(candidate_residual[:-1])))
        variance_error = float(abs(candidate_residual[-1]))
        score = max(
            max_linear / STRICT_LINEAR_TOLERANCE,
            variance_error
            / (STRICT_HERITABILITY_TOLERANCE * prevalence * (1.0 - prevalence)),
        )
        candidates.append((score, float(np.linalg.norm(result.x)), result.x.copy()))

    score, _, solution = min(candidates, key=lambda item: (item[0], item[1]))
    if score > 1.0:
        raise InfeasibleModelError(
            "No bounded penetrance table satisfies the requested heritability, "
            "prevalence, and no-marginal-effect constraints."
        )
    return np.asarray(solution, dtype=np.float64)


def solve_penetrance(
    mafs: ArrayLike,
    prevalence: float,
    heritability: float | None = None,
    mode: Mode = "compatibility",
) -> PenetranceModel:
    """Solve an EpiReSIM penetrance model from MAF and disease constraints."""

    maf_array = np.asarray(mafs, dtype=np.float64)
    if maf_array.ndim != 1 or maf_array.size not in {2, 3, 4, 5}:
        raise InputValidationError("MAFs must define a supported order from 2 through 5.")
    if not 0.0 < prevalence < 1.0:
        raise InputValidationError("Prevalence must be in the interval (0, 1).")
    if heritability is not None and not 0.0 < heritability <= 1.0:
        raise InputValidationError("Heritability must be in the interval (0, 1].")
    if mode not in {"compatibility", "strict"}:
        raise InputValidationError("Mode must be 'compatibility' or 'strict'.")

    if mode == "compatibility":
        solution, matrix, weights = _compatibility_solution(
            maf_array, prevalence, heritability
        )
    else:
        matrix, weights = marginal_constraint_matrix(maf_array)
        target = np.full(matrix.shape[0], prevalence, dtype=np.float64)
        linear_solution = _strict_linear_solution(matrix, target)
        solution = (
            linear_solution
            if heritability is None
            else _strict_nonlinear_solution(
                matrix,
                weights,
                target,
                prevalence,
                heritability,
                linear_solution,
            )
        )

    achieved_prevalence, achieved_heritability, marginals = model_statistics(
        solution, weights, matrix
    )
    marginal_error = float(np.max(np.abs(marginals - achieved_prevalence)))
    diagnostics = {
        "constraint_rank": float(np.linalg.matrix_rank(matrix)),
        "max_marginal_error": marginal_error,
        "prevalence_error": abs(achieved_prevalence - prevalence),
        "penetrance_min": float(solution.min()),
        "penetrance_max": float(solution.max()),
    }
    if heritability is not None:
        diagnostics["heritability_error"] = abs(achieved_heritability - heritability)

    if mode == "compatibility":
        if (
            abs(achieved_prevalence - float(marginals.min())) >= 0.05
            or abs(achieved_prevalence - float(marginals.max())) >= 0.05
        ):
            raise InfeasibleModelError(
                "The compatibility solver failed the MATLAB marginal-effect check."
            )
    else:
        if np.any((solution < 0.0) | (solution > 1.0)):
            raise InfeasibleModelError("Strict solver returned invalid penetrance values.")
        if diagnostics["prevalence_error"] > STRICT_LINEAR_TOLERANCE:
            raise InfeasibleModelError("Strict solver failed the prevalence tolerance.")
        if marginal_error > STRICT_LINEAR_TOLERANCE:
            raise InfeasibleModelError("Strict solver failed the marginal-effect tolerance.")
        if (
            heritability is not None
            and diagnostics["heritability_error"] > STRICT_HERITABILITY_TOLERANCE
        ):
            raise InfeasibleModelError("Strict solver failed the heritability tolerance.")

    return PenetranceModel(
        mafs=maf_array,
        penetrance=solution,
        prevalence=achieved_prevalence,
        heritability=achieved_heritability,
        order=maf_array.size,
        mode=mode,
        diagnostics=diagnostics,
    )
