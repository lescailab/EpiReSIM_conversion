---
title: Run a prevalence + heritability model
description: Add a broad-sense heritability constraint and diagnose infeasible parameter combinations.
---

Add `--heritability` when the penetrance table must satisfy both a prevalence
target and a broad-sense, observed-scale heritability target.

## Two-locus example

```bash
epiresim simulate /path/to/reference.mat \
  --cases 100 \
  --controls 100 \
  --snps 50 \
  --maf 0.20 0.30 \
  --prevalence 0.20 \
  --heritability 0.05 \
  --order 2 \
  --replicates 10 \
  --prefix order2_h2 \
  --format mat \
  --format txt \
  --seed 42 \
  --output-dir results/order2_h2 \
  --mode compatibility
```

## Higher-order examples

Only the model-specific options change:

```bash
# Order 3
--maf 0.10 0.20 0.30 --prevalence 0.20 --heritability 0.05 --order 3

# Order 4
--maf 0.10 0.20 0.30 0.40 --prevalence 0.15 --heritability 0.05 --order 4

# Order 5
--maf 0.10 0.15 0.20 0.25 0.30 --prevalence 0.15 --heritability 0.02 --order 5
```

These values are examples, not guarantees that every reference window and mode
will yield a feasible model.

## If the solver rejects the model

Do not repeatedly change random seeds until one answer appears acceptable
without recording that selection. Instead:

1. Confirm the number and range of MAF targets.
2. Inspect whether the reference contains enough loci near those targets.
3. Try a lower heritability target justified by the study design.
4. Try a lower interaction order if that still answers the evaluation question.
5. Compare compatibility and strict behavior, but do not present them as the
   same mathematical solution when they differ.
6. Record rejected settings as part of the simulation design.

## Interpretation

The target describes variance in the theoretical penetrance table under HWE and
linkage equilibrium. It is not the realized case fraction, an estimate from the
output, or a statement that the modeled SNPs explain that fraction of a real
trait's heritability.
