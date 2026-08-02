"""Random-number helpers separating MATLAB compatibility from strict mode."""

from __future__ import annotations

import numpy as np

RandomSource = np.random.Generator | np.random.RandomState


def compatibility_random_state(seed: int | None) -> np.random.RandomState:
    """Return the MT19937 stream used by MATLAB ``rng(seed, 'twister')``."""

    # MATLAB's factory seed 0 maps to the original MT19937 initialization seed.
    numpy_seed = 5489 if seed == 0 else seed
    return np.random.RandomState(numpy_seed)


def random_integer(rng: RandomSource, low: int, high: int) -> int:
    """Draw an integer from either NumPy's modern or legacy random API."""

    if isinstance(rng, np.random.Generator):
        return int(rng.integers(low, high))
    return int(rng.randint(low, high))


def matlab_randperm_one(rng: RandomSource, size: int) -> int:
    """Return the zero-based result of MATLAB R2026a ``randperm(size, 1)``.

    MATLAB uses a size-dependent sampling path. For the one-element selection
    used by EpiReSIM, candidate sets of two through four advance the shared
    uniform stream by one additional draw. This behavior was verified against
    the pinned oracle environment before implementation.
    """

    if size < 1:
        raise ValueError("Permutation size must be positive.")
    if size == 1:
        return 0

    draw = float(rng.random())
    if size <= 4:
        rng.random()
    return min(int(np.floor(draw * size)), size - 1)
