"""Public dataclasses used throughout EpiReSIM."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .exceptions import InputValidationError

Mode = Literal["compatibility", "strict"]
OutputFormat = Literal["mat", "txt"]
IntArray = NDArray[np.integer]
FloatArray = NDArray[np.floating]


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    """Configuration for one complete EpiReSIM run."""

    reference_path: Path
    case_count: int
    control_count: int
    snp_count: int
    mafs: tuple[float, ...]
    prevalence: float
    heritability: float | None
    order: int
    replicates: int
    output_prefix: str
    output_formats: tuple[OutputFormat, ...]
    seed: int | None = None
    output_dir: Path = Path(".")
    mode: Mode = "compatibility"
    max_sampling_attempts: int = 1_000_000
    max_maf_search_steps: int = 101

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_path", Path(self.reference_path))
        object.__setattr__(self, "output_dir", Path(self.output_dir))
        object.__setattr__(self, "mafs", tuple(float(value) for value in self.mafs))
        object.__setattr__(self, "output_formats", tuple(dict.fromkeys(self.output_formats)))

        if self.case_count < 0 or self.control_count < 0:
            raise InputValidationError("Case and control counts must be non-negative.")
        if self.case_count + self.control_count == 0:
            raise InputValidationError("At least one case or control sample is required.")
        if self.snp_count < 1:
            raise InputValidationError("SNP count must be positive.")
        if self.order not in {2, 3, 4, 5}:
            raise InputValidationError("Only interaction orders 2 through 5 are supported.")
        if len(self.mafs) != self.order:
            raise InputValidationError(
                f"Expected {self.order} target MAF values, received {len(self.mafs)}."
            )
        if any(not 0.0 < maf <= 0.5 for maf in self.mafs):
            raise InputValidationError("Every target MAF must be in the interval (0, 0.5].")
        if not 0.0 < self.prevalence < 1.0:
            raise InputValidationError("Prevalence must be in the interval (0, 1).")
        if self.heritability is not None and not 0.0 < self.heritability <= 1.0:
            raise InputValidationError("Heritability must be in the interval (0, 1].")
        if self.replicates < 1:
            raise InputValidationError("Replicate count must be positive.")
        if not self.output_prefix or Path(self.output_prefix).name != self.output_prefix:
            raise InputValidationError("Output prefix must be a non-empty filename prefix.")
        if not self.output_formats:
            raise InputValidationError("At least one output format is required.")
        if any(fmt not in {"mat", "txt"} for fmt in self.output_formats):
            raise InputValidationError("Output formats are limited to 'mat' and 'txt'.")
        if self.mode not in {"compatibility", "strict"}:
            raise InputValidationError("Mode must be 'compatibility' or 'strict'.")
        if self.max_sampling_attempts < 1 or self.max_maf_search_steps < 1:
            raise InputValidationError("Safety limits must be positive.")


@dataclass(frozen=True, slots=True)
class ReferenceData:
    """Validated reference genotypes and labels."""

    genotypes: IntArray
    labels: IntArray
    control_genotypes: IntArray
    variant_metadata: NDArray[np.object_] | None
    name: str
    window_start: int

    def __post_init__(self) -> None:
        if self.genotypes.ndim != 2:
            raise InputValidationError("Reference genotypes must be a two-dimensional matrix.")
        if self.labels.ndim != 1 or self.labels.shape[0] != self.genotypes.shape[0]:
            raise InputValidationError("Reference labels must match the genotype rows.")
        if self.control_genotypes.ndim != 2:
            raise InputValidationError("Control genotypes must be a two-dimensional matrix.")


@dataclass(frozen=True, slots=True)
class PenetranceModel:
    """A solved epistasis model."""

    mafs: FloatArray
    penetrance: FloatArray
    prevalence: float
    heritability: float
    order: int
    mode: Mode
    loci: tuple[int, ...] = ()
    diagnostics: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "mafs", np.asarray(self.mafs, dtype=np.float64))
        object.__setattr__(self, "penetrance", np.asarray(self.penetrance, dtype=np.float64))
        object.__setattr__(
            self, "diagnostics", MappingProxyType(dict(self.diagnostics))
        )
        if self.mafs.shape != (self.order,):
            raise InputValidationError("Model MAF count does not match the interaction order.")
        if self.penetrance.shape != (3**self.order,):
            raise InputValidationError("Penetrance vector length must equal 3**order.")
        if self.loci and len(self.loci) != self.order:
            raise InputValidationError("Model locus count does not match the interaction order.")


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Outputs and diagnostics from one complete simulation."""

    matrices: tuple[IntArray, ...]
    model: PenetranceModel
    reference: ReferenceData
    diagnostics: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "diagnostics", MappingProxyType(dict(self.diagnostics))
        )
