---
title: Five-minute simulation
description: Run a small two-locus prevalence-only model and understand each option.
---

This example generates two datasets containing 50 cases, 50 controls, and 100
SNP columns. Two of the SNPs define the epistatic model.

## Before you run

You need a native `.epiref` bundle or a legacy MATLAB v5 reference. The
[reference-data guide](../reference-data/) explains how to build a native
bundle from VCF/VCF.GZ or import an existing MAT file. Replace the example path
with your validated reference.

## Run the model

```bash
epiresim simulate /path/to/reference.epiref \
  --cases 50 \
  --controls 50 \
  --snps 100 \
  --maf 0.20 0.30 \
  --prevalence 0.20 \
  --order 2 \
  --replicates 2 \
  --prefix simulation \
  --format mat \
  --format txt \
  --seed 42 \
  --output-dir results \
  --mode compatibility
```

## Read the command

| Option | Meaning |
|---|---|
| `--cases 50` | Keep drawing simulated people until 50 have phenotype `1`. |
| `--controls 50` | Keep drawing until 50 have phenotype `0`. |
| `--snps 100` | Put 100 genotype columns in each output matrix. |
| `--maf 0.20 0.30` | Find two causal SNPs near target minor-allele frequencies 0.20 and 0.30. |
| `--prevalence 0.20` | Construct a model whose population disease probability is approximately 20%. |
| `--order 2` | Use two causal SNPs; therefore exactly two MAF values are required. |
| `--replicates 2` | Generate two independent output datasets in the same run. |
| `--format` | Repeat the option to request both MATLAB and text output. |
| `--seed 42` | Make the stochastic choices repeatable in the same mode and software version. |

Because `--heritability` is omitted, this is a **prevalence-only** model.

## Expected files

```text
results/
├── log.txt
├── simulation_1.mat
├── simulation_1.txt
├── simulation_2.mat
└── simulation_2.txt
```

Each matrix has 100 genotype columns plus a final phenotype column. Genotypes
use `1`, `2`, and `3`; phenotypes use `0` and `1`.

:::tip
Start with a small sample count and one replicate. Confirm the selected MAFs,
loci, penetrance range, and achieved statistics in `log.txt` before launching a
large simulation.
:::
