---
title: Genetics without jargon
description: Understand the genetic terms used by EpiReSIM before choosing model parameters.
---

This page introduces only the concepts needed to use EpiReSIM. The simulator
models a binary phenotype—such as affected versus unaffected—using several
biallelic genetic markers.

## DNA variation, alleles, and SNPs

A **single-nucleotide polymorphism (SNP)** is a genomic position where people
can carry different DNA bases. EpiReSIM treats each SNP as **biallelic**: it has
two alleles, written here as `A` and `a`.

People carry two copies of an autosomal chromosome, so their genotype at the
SNP is one of:

- `AA`: two copies of the common allele;
- `Aa`: one common and one minor allele; or
- `aa`: two copies of the minor allele.

EpiReSIM encodes these as `1`, `2`, and `3`, respectively.

## Minor-allele frequency

The **minor-allele frequency (MAF)** is the fraction of all chromosome copies
carrying the less common allele. A MAF of `0.20` means that 20% of allele copies
are `a`; it does **not** mean that 20% of people have genotype `aa`.

For `N` people encoded as `AA`, `Aa`, and `aa`:

$$
\mathrm{MAF}=\frac{n_{Aa}+2n_{aa}}{2N}.
$$

The `--maf` values are targets used to find causal loci in the selected
reference window. The actual MAFs in `log.txt` can differ because reference
data are finite and the search widens in steps of 0.01 until it finds candidates.

## Hardy–Weinberg equilibrium

If the minor allele has frequency $p$, **Hardy–Weinberg equilibrium (HWE)**
gives the idealized genotype frequencies:

$$
P(AA)=(1-p)^2,\quad P(Aa)=2p(1-p),\quad P(aa)=p^2.
$$

EpiReSIM uses these theoretical frequencies when solving the penetrance model.
The reference data need not follow HWE perfectly; strict mode reports the
largest observed frequency deviation at the selected loci.

## Phenotype, prevalence, and penetrance

A **phenotype** is the outcome being simulated. EpiReSIM uses `1` for a case
and `0` for a control.

**Prevalence** is the probability of being a case in the modeled population:

$$
K=P(D).
$$

**Penetrance** is conditional risk. For genotype combination $g$:

$$
f_g=P(D\mid g).
$$

A penetrance of `0.70` means that people with that multi-SNP genotype are
assigned case status with probability 0.70. It does not mean every generated
dataset will contain exactly 70% cases, because EpiReSIM subsequently samples
until it meets the case and control quotas requested by the user.

## Epistasis and interaction order

**Epistasis** means that the joint genotype at multiple loci affects risk in a
way that cannot be understood from each locus independently.

The **order** is the number of causal SNPs in the interaction:

| Order | Causal SNPs | Genotype combinations |
|---:|---:|---:|
| 2 | 2 | $3^2=9$ |
| 3 | 3 | $3^3=27$ |
| 4 | 4 | $3^4=81$ |
| 5 | 5 | $3^5=243$ |

Higher-order models have rapidly growing penetrance tables and can be harder to
solve or detect.

## “Without marginal effects”

In an epistatic model without marginal effects (eNME), knowing the genotype at
one causal SNP alone does not change expected risk. After averaging over the
other causal SNPs, each single-locus genotype has the same penetrance as the
overall prevalence.

For a two-locus model, for example:

$$
P(D\mid AA)=P(D\mid Aa)=P(D\mid aa)=K
$$

and the corresponding three equalities hold at the second locus. Individual
cells of the two-locus penetrance table can still have very different risks.
The signal is in the **combination**, not in either locus viewed alone.

:::note
“No marginal effect” describes the constructed penetrance model under its
frequency assumptions. Sampling variation, imperfect HWE, linkage
disequilibrium, or the reference data can still produce nonzero marginal
associations in a finite simulated dataset.
:::
