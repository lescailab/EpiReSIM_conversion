"""Genotype probability and constraint construction."""

from __future__ import annotations

from itertools import product

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .exceptions import InputValidationError

FloatArray = NDArray[np.float64]


def genotype_probabilities(mafs: ArrayLike) -> FloatArray:
    """Return joint genotype probabilities in MATLAB-compatible lexicographic order."""

    maf_array = np.asarray(mafs, dtype=np.float64)
    if maf_array.ndim != 1 or maf_array.size == 0:
        raise InputValidationError("MAFs must be a non-empty one-dimensional sequence.")
    if not np.all(np.isfinite(maf_array)):
        raise InputValidationError("MAFs must be finite.")
    if np.any((maf_array <= 0.0) | (maf_array > 0.5)):
        raise InputValidationError("MAFs must be in the interval (0, 0.5].")

    per_locus = [
        np.array([(1.0 - maf) ** 2, 2.0 * maf * (1.0 - maf), maf**2])
        for maf in maf_array
    ]
    weights = per_locus[0]
    for probabilities in per_locus[1:]:
        weights = np.kron(weights, probabilities)
    return np.asarray(weights, dtype=np.float64)


def genotype_combinations(order: int) -> NDArray[np.int8]:
    """Return all 0/1/2 genotype combinations with the last locus varying fastest."""

    if order not in {2, 3, 4, 5}:
        raise InputValidationError("Only interaction orders 2 through 5 are supported.")
    return np.asarray(list(product(range(3), repeat=order)), dtype=np.int8)


def marginal_constraint_matrix(mafs: ArrayLike) -> tuple[FloatArray, FloatArray]:
    """Construct generic no-marginal-effect and prevalence constraints A x = b."""

    maf_array = np.asarray(mafs, dtype=np.float64)
    weights = genotype_probabilities(maf_array)
    order = maf_array.size
    combinations = genotype_combinations(order)
    rows: list[FloatArray] = []

    for locus in range(order):
        for genotype in range(3):
            mask = combinations[:, locus] == genotype
            denominator = float(weights[mask].sum())
            row = np.zeros_like(weights)
            row[mask] = weights[mask] / denominator
            rows.append(row)

    rows.append(weights.copy())
    matrix = np.vstack(rows)
    return matrix, weights


def legacy_constraint_matrix(mafs: ArrayLike) -> tuple[FloatArray, FloatArray]:
    """Construct the exact order-specific marginal index maps used by MATLAB."""

    maf_array = np.asarray(mafs, dtype=np.float64)
    weights = genotype_probabilities(maf_array)
    order = maf_array.size
    size = 3**order
    rows: list[FloatArray] = []

    def add_group(indices_by_genotype: tuple[list[int], list[int], list[int]],
                  weight_groups: list[list[int]]) -> None:
        for genotype in range(3):
            row = np.zeros(size, dtype=np.float64)
            for target, weight_indices in zip(
                indices_by_genotype[genotype], weight_groups, strict=True
            ):
                row[target] = float(weights[weight_indices].sum())
            rows.append(row)

    block = 3 ** (order - 1)
    weight_groups_a = [
        [i, block + i, 2 * block + i] for i in range(block)
    ]
    add_group(
        (
            list(range(block)),
            list(range(block, 2 * block)),
            list(range(2 * block, 3 * block)),
        ),
        weight_groups_a,
    )

    if order >= 2:
        base_b = [
            j + outer * block
            for outer in range(3)
            for j in range(3 ** (order - 2))
        ]
        stride_b = 3 ** (order - 2)
        weight_groups_b = [
            [i, i + stride_b, i + 2 * stride_b] for i in base_b
        ]
        add_group(
            (
                base_b,
                [i + stride_b for i in base_b],
                [i + 2 * stride_b for i in base_b],
            ),
            weight_groups_b,
        )

    if order == 3:
        base_c = [outer * 9 + 3 * inner for outer in range(3) for inner in range(3)]
        weight_groups_c = [[i, i + 1, i + 2] for i in base_c]
        add_group(
            (base_c, [i + 1 for i in base_c], [i + 2 for i in base_c]),
            weight_groups_c,
        )
    elif order == 4:
        base_c = [inner + 9 * outer for outer in range(9) for inner in range(3)]
        weight_groups_c = [[i, i + 3, i + 6] for i in base_c]
        add_group(
            (base_c, [i + 3 for i in base_c], [i + 6 for i in base_c]),
            weight_groups_c,
        )

        # The original fourth-locus loop visits 12 rather than all 27 backgrounds.
        base_d = [outer * 27 + 3 * inner for outer in range(3) for inner in range(4)]
        weight_groups_d = [[i, i + 1, i + 2] for i in base_d]
        add_group(
            (base_d, [i + 1 for i in base_d], [i + 2 for i in base_d]),
            weight_groups_d,
        )
    elif order == 5:
        base_c = [inner + 27 * outer for outer in range(9) for inner in range(9)]
        weight_groups_c = [[i, i + 9, i + 18] for i in base_c]
        add_group(
            (base_c, [i + 9 for i in base_c], [i + 18 for i in base_c]),
            weight_groups_c,
        )

        base_d = [inner + 9 * outer for outer in range(27) for inner in range(3)]
        weight_groups_d = [[i, i + 3, i + 6] for i in base_d]
        add_group(
            (base_d, [i + 3 for i in base_d], [i + 6 for i in base_d]),
            weight_groups_d,
        )

        base_e = [3 * outer for outer in range(81)]
        weight_groups_e = [[i, i + 1, i + 2] for i in base_e]
        add_group(
            (base_e, [i + 1 for i in base_e], [i + 2 for i in base_e]),
            weight_groups_e,
        )

    rows.append(weights.copy())
    return np.vstack(rows), weights


def model_statistics(
    penetrance: ArrayLike,
    weights: ArrayLike,
    constraint_matrix: ArrayLike,
) -> tuple[float, float, FloatArray]:
    """Return prevalence, heritability, and single-locus marginal penetrances."""

    values = np.asarray(penetrance, dtype=np.float64)
    probability = np.asarray(weights, dtype=np.float64)
    matrix = np.asarray(constraint_matrix, dtype=np.float64)
    prevalence = float(probability @ values)
    denominator = prevalence * (1.0 - prevalence)
    heritability = (
        float(probability @ np.square(values - prevalence)) / denominator
        if denominator > 0.0
        else float("nan")
    )
    marginals = np.asarray(matrix[:-1] @ values, dtype=np.float64)
    return prevalence, heritability, marginals
