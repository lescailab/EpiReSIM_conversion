---
title: Read the outputs
description: Interpret MAT matrices, text matrices, phenotype codes, and the model log.
---

## Matrix files

For prefix `simulation` and two replicates, EpiReSIM creates
`simulation_1` and `simulation_2` in each requested format.

Every matrix has:

- one row per simulated person;
- the requested number of genotype columns; and
- one final phenotype column.

If 100 SNPs were requested, the matrix has 101 columns.

## MATLAB output

The `.mat` file is MATLAB Level 5 and contains one variable named `SNP`.
Compatibility mode exposes it as MATLAB class `double` and uses compression,
matching the registered semantic schema of the original output.

```python
from scipy.io import loadmat

matrix = loadmat("results/simulation_1.mat", mat_dtype=True)["SNP"]
genotypes = matrix[:, :-1]
phenotype = matrix[:, -1]
```

Raw MAT bytes can differ between MATLAB and SciPy because their headers and
internal numeric storage differ. Validation compares the loaded variable name,
MATLAB class, shape, and exact values.

## Text output

The `.txt` file is tab-separated, has no header, and retains a trailing tab on
each row for compatibility. Do not assume a standard CSV parser will infer the
final empty field correctly; specify tab separation and select the expected
number of columns.

Compatibility mode appends if the text path already exists. Use a new output
directory for a clean run.

## Codes

| Position | Code | Meaning |
|---|---:|---|
| Genotype columns | `1` | `AA` |
| Genotype columns | `2` | `Aa` |
| Genotype columns | `3` | `aa` |
| Final column | `0` | control |
| Final column | `1` | case |

## Model log

`log.txt` records:

- interaction order;
- observed MAFs of the selected causal loci;
- one-based causal-locus indices, matching MATLAB;
- the penetrance vector;
- achieved prevalence; and
- achieved heritability.

The locus indices refer to columns in the randomly selected output window, not
necessarily the original full reference matrix.

## Minimum quality checks

Before analysis, confirm:

```python
import numpy as np
from scipy.io import loadmat

matrix = loadmat("results/simulation_1.mat")["SNP"]
assert matrix.shape == (200, 51)  # 100 cases + 100 controls, 50 SNPs + phenotype
assert set(np.unique(matrix[:, :-1])) <= {1, 2, 3}
assert np.count_nonzero(matrix[:, -1] == 1) == 100
assert np.count_nonzero(matrix[:, -1] == 0) == 100
```
