from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import savemat


@pytest.fixture
def reference_mat(tmp_path: Path) -> Path:
    rng = np.random.default_rng(711)
    sample_count = 240
    snp_count = 30
    mafs = np.linspace(0.08, 0.45, snp_count)
    probabilities = np.column_stack(
        ((1.0 - mafs) ** 2, 2.0 * mafs * (1.0 - mafs), mafs**2)
    )
    genotypes = np.empty((sample_count, snp_count), dtype=np.int8)
    for column in range(snp_count):
        genotypes[:, column] = rng.choice(
            np.array([1, 2, 3], dtype=np.int8),
            size=sample_count,
            p=probabilities[column],
        )

    sample_info = np.empty((sample_count, 6), dtype=object)
    for row in range(sample_count):
        sample_info[row] = [
            f"sample_{row + 1}",
            "group_a",
            row + 1,
            "batch_1",
            2 if row < 200 else 1,
            "unused",
        ]
    snp_info = np.empty((snp_count, 2), dtype=object)
    for column in range(snp_count):
        snp_info[column] = [f"variant_{column + 1}", column + 1]

    path = tmp_path / "reference.mat"
    savemat(path, {"pts": genotypes, "SampleInfo": sample_info, "SNPInfo": snp_info})
    return path
