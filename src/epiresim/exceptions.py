"""Package-specific exceptions."""


class EpiReSIMError(Exception):
    """Base class for user-facing EpiReSIM errors."""


class InputValidationError(EpiReSIMError, ValueError):
    """Raised when reference data or configuration is invalid."""


class InfeasibleModelError(EpiReSIMError, RuntimeError):
    """Raised when the requested penetrance constraints cannot be satisfied."""


class SamplingError(EpiReSIMError, RuntimeError):
    """Raised when resampling cannot satisfy the requested quotas."""


class OutputCollisionError(EpiReSIMError, FileExistsError):
    """Raised when strict mode would overwrite an existing output."""
