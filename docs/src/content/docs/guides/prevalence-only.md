---
title: Run a prevalence-only model
description: Complete command recipes for linear eNME models of orders two through five.
---

Prevalence-only models solve linear no-marginal-effect constraints. Omit the
`--heritability` option completely.

## Order 2

```bash
epiresim simulate /path/to/reference.mat \
  --cases 100 --controls 100 --snps 50 \
  --maf 0.20 0.30 \
  --prevalence 0.20 --order 2 \
  --replicates 10 --prefix order2 \
  --format mat --seed 42 --output-dir results/order2 \
  --mode compatibility
```

## Order 3

```bash
epiresim simulate /path/to/reference.mat \
  --cases 100 --controls 100 --snps 50 \
  --maf 0.10 0.20 0.30 \
  --prevalence 0.20 --order 3 \
  --replicates 10 --prefix order3 \
  --format mat --seed 42 --output-dir results/order3 \
  --mode compatibility
```

## Orders 4 and 5

Use exactly four or five targets:

```bash
# Order 4
--maf 0.10 0.20 0.30 0.40 --prevalence 0.15 --order 4

# Order 5
--maf 0.10 0.15 0.20 0.25 0.30 --prevalence 0.15 --order 5
```

Insert the chosen line into the full command above and use a distinct output
directory.

## What to verify

After every model:

1. Confirm the reported order and number of loci in `log.txt`.
2. Compare logged MAFs with the requested targets.
3. Confirm every output has `cases + controls` rows and `snps + 1` columns.
4. Count phenotype `1` and `0` values in the last column.
5. Record the command, seed, software version, and reference checksum.

:::tip
Use different output directories for parameter sets. Compatibility mode
overwrites MAT and log files with matching names and appends to existing text
files, faithfully reproducing the original behavior.
:::
