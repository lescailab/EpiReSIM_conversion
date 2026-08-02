---
title: Command-line reference
description: Complete reference for the epiresim simulate command.
---

## Synopsis

```text
epiresim simulate REFERENCE [options]
```

## Parameters

| Argument | Required | Meaning |
|---|:---:|---|
| `REFERENCE` | yes | Path to the MATLAB v5 reference file. |
| `--cases INTEGER` | yes | Number of phenotype-1 rows per replicate; may be zero if controls are positive. |
| `--controls INTEGER` | yes | Number of phenotype-0 rows per replicate; may be zero if cases are positive. |
| `--snps INTEGER` | yes | Number of consecutive genotype columns in each output. |
| `--maf VALUE [...]` | yes | One target MAF per causal locus. Count must equal order. |
| `--prevalence FLOAT` | yes | Target model prevalence strictly between zero and one. |
| `--heritability FLOAT` | no | Target broad-sense heritability in `(0, 1]`. Omit for prevalence-only solving. |
| `--order {2,3,4,5}` | yes | Number of causal loci. |
| `--replicates INTEGER` | yes | Number of datasets to generate. |
| `--prefix TEXT` | yes | Filename prefix without directory separators. |
| `--format {mat,txt}` | yes | Output type. Repeat the option to request both. |
| `--seed INTEGER` | no | Local random seed. Record it for reproducibility. |
| `--output-dir PATH` | no | Output directory; defaults to the current directory. |
| `--mode {compatibility,strict}` | no | Behavior profile; defaults to `compatibility`. |

Run `epiresim simulate --help` for the installed version's authoritative
parser output.

## Exit behavior

- Exit code `0`: the run completed.
- Exit code `2`: invalid input, infeasible model, sampling failure, output
  collision, or filesystem error reported through the command-line interface.

Do not infer why a job failed from the exit code alone; preserve standard error
in workflow logs.

## Reproducible command record

Alongside a simulation, record:

```text
EpiReSIM version or git commit:
Mode:
Complete command:
Seed:
Reference checksum:
Python, NumPy, and SciPy versions:
Operating system and architecture:
```

This information is necessary to reproduce stochastic output and to interpret
compatibility claims.
