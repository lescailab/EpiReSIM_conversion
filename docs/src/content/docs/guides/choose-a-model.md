---
title: Choose a model
description: Translate a simulation goal into order, MAF, prevalence, heritability, mode, and sample-size parameters.
---

Choose parameters in this order so each decision has a clear scientific role.

## 1. Define the evaluation question

Write down what the simulated data will test. Examples include sensitivity to a
two-locus interaction, robustness as causal alleles become rare, or performance
on higher-order interactions without single-locus marginal effects.

Do not choose parameters only because a solver accepts them. They should reflect
the behavior your downstream method is meant to evaluate.

## 2. Choose interaction order

Order is the number of causal SNPs. Use order two for the easiest interpretation
and debugging. Increase to three, four, or five only when the evaluation
requires higher-order interactions; the penetrance table grows as $3^k$.

The number of `--maf` values must equal `--order`.

## 3. Choose target MAFs

Choose MAFs represented in the intended reference population. Targets between
0.05 and 0.30 were recommended by the original study for higher model-generation
success, but this is guidance from its experiments rather than a universal law.

Inspect `log.txt` after the run because the selected loci use observed reference
MAFs near the targets.

## 4. Choose prevalence

Prevalence shapes the penetrance table. It does not set the output case fraction.
Use a value relevant to the modeled binary trait and population, while
remembering that ascertainment in a case-control study can deliberately produce
a very different case fraction.

The original study explored lower prevalence ranges more successfully for
higher-order models. Start conservatively and test feasibility before scaling.

## 5. Decide whether to constrain heritability

- Omit `--heritability` for the linear, prevalence-only model.
- Add it when the benchmark requires a specific broad-sense, observed-scale
  genetic variance from the penetrance table.

Heritability-constrained models are nonlinear and have more ways to be
infeasible. Do not interpret this parameter as narrow-sense heritability.

## 6. Choose mode

Use `compatibility` when reproducing a validated MATLAB scenario or comparing
against legacy output. Use `strict` when beginning a new analysis that requires
bounded penetrances, distinct causal loci, collision protection, and tighter
constraint checks. See [Compatibility or strict?](./modes/).

## 7. Choose cases, controls, SNPs, and replicates

- `--cases` and `--controls` define each output dataset's quotas.
- `--snps` defines the consecutive reference window width.
- `--replicates` defines how many independently resampled datasets are produced.

Plan power and replication for the downstream method separately. EpiReSIM does
not perform a power calculation.

## A conservative first run

For a new reference file, begin with:

- order 2;
- MAFs represented by many reference loci;
- prevalence-only solving;
- 20 cases and 20 controls;
- 20–100 SNPs;
- one replicate; and
- a recorded seed.

Then inspect the log and output before adding heritability, higher order, or
larger quotas.
