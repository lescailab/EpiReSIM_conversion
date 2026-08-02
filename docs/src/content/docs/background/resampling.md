---
title: How resampling works
description: Follow the path from a reference genotype matrix to a simulated case-control dataset.
---

The method combines a theoretical penetrance model with empirical genotype
fragments. One run follows this sequence.

## Step 1: choose a consecutive SNP window

EpiReSIM selects one random consecutive window from `pts` containing the number
of columns requested by `--snps`. All later operations use this window.

## Step 2: keep reference controls

Rows whose fifth `SampleInfo` field equals `2` form the donor pool. Reference
cases are not used for resampling.

## Step 3: calculate observed MAFs

The program calculates one MAF per selected SNP from the donor controls. For
each requested target MAF, it searches within ±0.01, then widens the interval by
0.01 until candidates exist. One candidate becomes a causal locus.

Compatibility mode reproduces the original selection behavior, including the
possibility that the same locus is selected more than once. Strict mode requires
distinct causal loci.

## Step 4: solve the penetrance table

The actual MAFs of the selected causal loci—not merely the requested targets—go
into the model solver. The result is a vector of $3^k$ case probabilities.

## Step 5: create a genotype mosaic

For each candidate sample, random breakpoints split the selected SNP window
into contiguous fragments. Each fragment copies genotypes from a randomly
chosen control donor. This preserves within-fragment patterns present in real
controls, while recombining fragments across donors.

The procedure is a pragmatic resampling model. It is not a meiosis simulator,
pedigree model, coalescent model, ancestry model, or explicit recombination-map
model.

## Step 6: assign phenotype

The causal genotype combination indexes the penetrance table. EpiReSIM draws a
uniform random number and assigns case status with that penetrance probability.

## Step 7: enforce quotas by rejection

The candidate is kept only while its phenotype group still needs rows. Drawing
continues until the requested case and control counts are reached. Safety limits
turn the original potentially unbounded loop into an explicit error if quotas
cannot be filled.

## What the output preserves—and what it does not

The mosaic approach can preserve short-range allele-frequency and linkage
patterns from the donor controls. It does not guarantee preservation of:

- long-range haplotypes;
- population structure or ancestry proportions;
- relatedness or family structure;
- sex-chromosome inheritance;
- imputation uncertainty;
- physical recombination distances; or
- privacy of the source participants.

Use diagnostics and downstream quality checks appropriate to your study rather
than assuming the output is realistic in every genomic dimension.
