"""Python implementation of the EpiReSIM simulator."""

from .api import run, simulate
from .io import load_reference
from .probabilities import genotype_probabilities
from .reference import (
    build_reference_from_vcf,
    export_mat_reference,
    import_mat_reference,
    inspect_reference_bundle,
    validate_reference_bundle,
)
from .solvers import solve_penetrance
from .types import PenetranceModel, ReferenceData, SimulationConfig, SimulationResult

__all__ = [
    "PenetranceModel",
    "ReferenceData",
    "SimulationConfig",
    "SimulationResult",
    "build_reference_from_vcf",
    "export_mat_reference",
    "genotype_probabilities",
    "import_mat_reference",
    "inspect_reference_bundle",
    "load_reference",
    "run",
    "simulate",
    "solve_penetrance",
    "validate_reference_bundle",
]

__version__ = "0.1.0"
