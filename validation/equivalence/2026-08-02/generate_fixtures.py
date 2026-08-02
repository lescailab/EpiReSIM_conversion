"""Generate the redistributable synthetic references used by the golden corpus."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.io import savemat


def build_reference(
    path: Path,
    *,
    seed: int,
    samples: int,
    snps: int,
    controls: int,
    matlab_dtype: np.dtype[np.generic],
) -> None:
    rng = np.random.default_rng(seed)
    mafs = np.resize(np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.40]), snps)
    probabilities = np.column_stack(
        ((1.0 - mafs) ** 2, 2.0 * mafs * (1.0 - mafs), mafs**2)
    )
    genotype_codes = np.array([1, 2, 3], dtype=matlab_dtype)
    genotypes = np.empty((samples, snps), dtype=matlab_dtype)
    for column in range(snps):
        genotypes[:, column] = rng.choice(
            genotype_codes, size=samples, p=probabilities[column]
        )

    sample_info = np.empty((samples, 6), dtype=object)
    for row in range(samples):
        sample_info[row] = [
            f"sample_{row + 1}",
            "group_a",
            row + 1,
            "batch_1",
            2 if row < controls else 1,
            "unused",
        ]
    snp_info = np.empty((snps, 2), dtype=object)
    for column in range(snps):
        snp_info[column] = [f"variant_{column + 1}", column + 1]

    path.parent.mkdir(parents=True, exist_ok=True)
    savemat(path, {"pts": genotypes, "SampleInfo": sample_info, "SNPInfo": snp_info})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_directory", type=Path)
    args = parser.parse_args()
    build_reference(
        args.output_directory / "reference_240x48.mat",
        seed=711,
        samples=240,
        snps=48,
        controls=200,
        matlab_dtype=np.dtype(np.float64),
    )
    build_reference(
        args.output_directory / "reference_80x16.mat",
        seed=712,
        samples=80,
        snps=16,
        controls=60,
        matlab_dtype=np.dtype(np.int8),
    )
    savemat(args.output_directory / "missing_variables.mat", {"unexpected": [[1.0]]})


if __name__ == "__main__":
    main()
