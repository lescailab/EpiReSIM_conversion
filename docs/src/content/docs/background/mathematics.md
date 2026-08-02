---
title: The mathematical model
description: See how genotype probabilities, penetrance, prevalence, heritability, and no-marginal-effect constraints fit together.
---

EpiReSIM separates the problem into two parts: construct a penetrance table,
then generate genotype mosaics and assign phenotypes from that table.

## 1. Genotype-combination probabilities

For causal locus $j$ with MAF $p_j$, HWE assigns probabilities

$$
q_j=\left((1-p_j)^2,\;2p_j(1-p_j),\;p_j^2\right)
$$

to `AA`, `Aa`, and `aa`. The model solver also assumes **linkage equilibrium**
among the causal loci, so the probability of a multi-locus genotype $g$ is the
product

$$
w_g=\prod_{j=1}^{k}q_{j,g_j}.
$$

This multiplication is an assumption used to build the penetrance table. The
resampling stage can preserve local linkage disequilibrium from the reference.

## 2. Prevalence

Let $f_g=P(D\mid g)$ be one element of the penetrance table. The population
prevalence implied by the table is the weighted mean

$$
K=\sum_g w_gf_g.
$$

## 3. No-marginal-effect constraints

For every causal locus and each of its three genotypes, EpiReSIM averages over
the other loci and requires the conditional risk to equal $K$. These are linear
constraints on the penetrance vector $f$ and can be written

$$
Af=b,
$$

where every element of $b$ is the requested prevalence.

There are $3^k$ penetrance values but fewer independent constraints. The system
is **underdetermined**: many tables can satisfy it. In prevalence-only mode, the
compatibility solver follows the original minimum-norm linear solution.

## 4. Broad-sense heritability

When heritability is requested, EpiReSIM uses the original paper's binary-trait,
observed-scale expression:

$$
H^2=\frac{\sum_g w_g(f_g-K)^2}{K(1-K)}.
$$

The numerator measures variation in genotype-specific risks around prevalence.
The denominator is the total variance of a Bernoulli phenotype with probability
$K$. This is **broad-sense model heritability**, not an estimate of narrow-sense
heritability from real pedigrees or a guarantee about the realized variance in
one finite simulated dataset.

Adding this quadratic constraint makes the system nonlinear. Compatibility mode
reproduces the original Newton and Gauss–Seidel calculations. Strict mode uses a
bounded nonlinear least-squares problem and rejects a request when it cannot
meet the registered tolerances.

## 5. Why some parameter combinations fail

A valid penetrance is a probability between zero and one, but not every
combination of order, MAFs, prevalence, heritability, and no-marginal-effect
constraints has a solution in that interval.

Failure becomes more likely when:

- requested heritability is too high for the prevalence and MAFs;
- causal alleles are very rare, leaving little genotype probability mass;
- the reference does not contain loci close to the requested MAFs; or
- numerical constraints become singular or fail their tolerances.

Compatibility mode matches the original behavior, including clipping negative
penetrances but not imposing an upper bound. Strict mode requires every value
to stay in `[0, 1]`.

## 6. Realized data versus model targets

The solver's prevalence and heritability describe the theoretical penetrance
table under HWE and linkage equilibrium. The generated file is quota sampled:
it contains exactly the requested numbers of cases and controls. Consequently,
the fraction of cases in the output is determined by `--cases` and
`--controls`, not by `--prevalence`.

:::caution[Do not confuse prevalence with the output case fraction]
Use `--prevalence` to shape the disease model. Use `--cases` and `--controls`
to choose the case-control study design. They answer different questions.
:::
