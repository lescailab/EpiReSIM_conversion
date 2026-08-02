---
title: Python API
description: Configure and run simulations programmatically with typed public dataclasses.
---

The public API is useful for notebooks, scripted experiment grids, and direct
inspection of the solved model.

## Complete run

```python
from pathlib import Path

from epiresim import SimulationConfig, run

config = SimulationConfig(
    reference_path=Path("/path/to/reference.mat"),
    case_count=100,
    control_count=100,
    snp_count=50,
    mafs=(0.20, 0.30),
    prevalence=0.20,
    heritability=None,
    order=2,
    replicates=10,
    output_prefix="simulation",
    output_formats=("mat", "txt"),
    seed=42,
    output_dir=Path("results"),
    mode="compatibility",
)

result = run(config)
print(result.model.penetrance)
print(result.model.loci)
print(result.diagnostics)
```

`run()` loads and validates the reference, chooses causal loci, solves the
model, generates all replicates, writes outputs, and returns the in-memory
result.

## Result objects

`SimulationResult` contains:

- `matrices`: generated matrices before output-format conversion;
- `model`: the `PenetranceModel`, including MAFs, loci, penetrances, achieved
  prevalence, heritability, mode, and solver diagnostics;
- `reference`: the selected `ReferenceData` window and controls; and
- `diagnostics`: reference HWE deviation, causal-locus correlation, and total
  sampling attempts.

## Solve without generating samples

```python
from epiresim import solve_penetrance

model = solve_penetrance(
    mafs=[0.20, 0.30],
    prevalence=0.20,
    heritability=0.05,
    mode="strict",
)
```

This uses the MAFs exactly as supplied. A complete `run()` instead selects loci
from the reference and solves with their observed MAFs.

## Lower-level public functions

The package also exposes:

- `load_reference()` for schema validation and window selection;
- `genotype_probabilities()` for the HWE/linkage-equilibrium weight vector;
- `simulate()` for one dataset from a prepared reference and model; and
- the public configuration and result dataclasses.

These are useful for focused experiments but require the caller to manage the
random generator and preserve the intended mode's semantics.
