---
title: Prepare reference data
description: Create the MATLAB v5 variables and genotype coding required by EpiReSIM.
---

EpiReSIM does not generate background genotype structure from a population
model. It resamples fragments from a reference dataset, so the input determines
which allele frequencies and local correlations can appear in the output.

## Required MATLAB variables

The input must be a MATLAB v5 `.mat` file containing:

| Variable | Shape | Required content |
|---|---|---|
| `pts` | samples × SNPs | Numeric genotype codes `1`, `2`, or `3`. |
| `SampleInfo` | samples × at least 5 columns | Column five contains the sample class. The original implementation selects controls with label `2`. |
| `SNPInfo` | SNPs × metadata columns | Optional. Retained for the selected window when dimensions agree. |

The row count of `SampleInfo` must equal the row count of `pts`.

## Genotype coding

For a biallelic SNP with common allele `A` and minor allele `a`:

| Code | Genotype | Minor-allele copies |
|---:|---|---:|
| `1` | `AA` | 0 |
| `2` | `Aa` | 1 |
| `3` | `aa` | 2 |

Do not use the common dosage coding `0/1/2` without converting it. In Python,
adding one converts a clean dosage matrix:

```python
encoded = dosage_matrix + 1
```

Validate that missing or imputed values have been handled first. EpiReSIM
rejects non-finite values and codes outside `1`, `2`, and `3`.

## Why only controls are resampled

The original method removes case samples before resampling so an association
already present in the reference cases is less likely to be carried into the
new data. The simulated phenotype is assigned from the new penetrance table.
This does not guarantee removal of every confounder or interaction in the
reference controls.

## Size requirements

- The reference must contain at least the requested number of SNP columns.
- Compatibility mode reproduces the original window-selection expression and
  therefore requires at least **two more** reference columns than requested.
- At least one row must have control label `2`.
- More control rows provide more donor fragments and usually more background
  diversity.

## Privacy and authorization

Simulated rows are mosaics of real control genotypes. Treat the reference and
outputs according to the consent, data-use agreement, and security rules that
apply to the source data. Do not assume resampling makes individual-level
genotypes anonymous.

:::caution
Never commit a real cohort `.mat` file or generated individual-level genotypes
to this public repository. Use synthetic, redistributable fixtures for tests
and documentation.
:::
