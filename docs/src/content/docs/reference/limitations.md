---
title: Assumptions and limits
description: Know what EpiReSIM models, what it approximates, and what remains outside scope.
---

EpiReSIM is a focused simulator for evaluating interaction-detection methods.
It is not a general population-genetics or clinical-risk simulator.

## Model assumptions

- Causal SNPs are biallelic and encoded as three diploid genotypes.
- HWE determines theoretical single-locus genotype probabilities.
- Linkage equilibrium determines theoretical multi-locus probabilities in the
  penetrance solver.
- The phenotype is binary.
- No-marginal-effect constraints are defined relative to the theoretical model.
- Heritability is broad-sense and on the observed binary scale used by the
  original paper.

## Resampling assumptions

- Control rows labeled `2` are appropriate donors for the intended study.
- Random fragment mosaics are an adequate approximation for the benchmark.
- A random consecutive reference window is scientifically acceptable.
- Observed reference MAFs provide suitable causal-locus candidates.

## Not modeled

- quantitative or multiclass phenotypes;
- environmental effects or gene-environment interactions;
- explicit ancestry, demography, pedigrees, or relatedness;
- recombination maps, mutation, selection, or coalescent history;
- genotype likelihoods, phasing uncertainty, or imputation dosage;
- direct BCF, PLINK, genotype-likelihood, or arbitrary tabular reference input;
- interaction orders below two or above five; or
- a penetrance solver that directly models empirical linkage disequilibrium.

## Important interpretation limits

1. The requested prevalence is not the case fraction in the output.
2. The requested heritability is not an estimate from a real population.
3. A finite generated dataset may show marginal associations even when the
   theoretical penetrance table has none.
4. Preserved reference patterns can carry confounding, structure, artifacts,
   or private information into outputs.
5. Exact same-seed validation covers registered scenarios, not the entire input
   space.
6. The original reference file's public construction record is insufficient to
   recover its source assembly, QC, and allele-orientation steps. Native builds
   are transparent project extensions rather than reconstructions of those
   unrecorded choices.

## Failure is informative

Strict mode intentionally rejects infeasible penetrance tables, duplicate
causal loci, and output collisions. Compatibility mode can also fail when it
reproduces an invalid legacy window choice or cannot fill phenotype quotas
within its safety limit. Treat these as explicit model or input limitations,
not merely software inconvenience.
