---
title: Prepare reference data
description: Build a provenance-aware native reference or use a legacy MATLAB file.
---

EpiReSIM does not generate background genotype structure from an independent
population model. It resamples contiguous fragments from donor genotypes, so
the selected population, variants, quality filters, and genomic ordering all
affect the simulated data.

## What the original work establishes

The published article explains that a real biological SNP dataset was converted
to a samples-by-SNPs matrix, encoded as `1`, `2`, and `3`, and filtered to retain
controls before resampling. The original repository also supplies a MATLAB
reference file with the variables expected by the code.

The publication and repository do not, however, record a reproducible source
download, genome assembly, sample-selection rule, quality-control thresholds,
allele-orientation procedure, or conversion script for that file. This does not
imply that those steps were not performed; it means they cannot be reconstructed
confidently from the public record available to this project.

EpiReSIM therefore makes the following distinction:

- legacy MATLAB support reproduces the supplied input contract for
  compatibility;
- native reference construction is a documented extension based on explicit
  assumptions, not a claim about the original authors' unpublished preparation;
- every native bundle records its source checksum and transformation settings.

See the [original article](https://doi.org/10.3390/genes13122286) and
[original source repository](https://github.com/CDMB-lab/EpiReSIM).

## Recommended source data

Use an indexed, quality-controlled population reference panel and obtain it
under its applicable data-use terms. The
[International Genome Sample Resource](https://www.internationalgenome.org/data/)
maintains 1000 Genomes data collections, including genotype VCFs and sample
population files. HapMap-derived inputs can also be converted when their genome
build and allele conventions are known, but 1000 Genomes/IGSR is the recommended
starting point for new references.

The current builder reads text VCF and compressed `VCF.GZ`. It does not yet read
binary BCF or PLINK PGEN directly.

## Build a native reference

Build one chromosome per bundle. This prevents a contiguous resampling window
from crossing a chromosome boundary.

```bash
epiresim reference build /path/to/panel.vcf.gz \
  --output /path/to/reference_chr1.epiref \
  --genome-build GRCh38 \
  --chromosome 1 \
  --source-name reference_panel \
  --source-release release_name \
  --source-url https://example.org/reference-panel
```

The builder:

1. retains records marked `PASS` or `.`;
2. retains biallelic single-nucleotide variants;
3. requires complete diploid `FORMAT/GT` hard calls across selected samples;
4. calculates allele frequency in the selected donor samples;
5. stores dosage relative to the selected population's minor allele as `0`,
   `1`, or `2`;
6. records when REF rather than ALT is the minor allele;
7. preserves VCF variant order; and
8. validates component checksums after writing.

Use `--include-filtered` only when including filtered VCF records is an explicit
study decision. Use `--min-maf VALUE` to exclude variants below a chosen donor
population frequency. The default is `0`, so no undocumented MAF threshold is
introduced.

:::caution
Variants containing missing, haploid, polyploid, or non-hard-call genotypes in
the selected samples are excluded. The builder does not silently impute them.
Review the skipped-variant counts recorded in `manifest.json`.
:::

## Select samples or a population

Use a one-ID-per-line file to select samples:

```bash
epiresim reference build /path/to/panel.vcf.gz \
  --output /path/to/reference_chr1.epiref \
  --genome-build GRCh38 \
  --chromosome 1 \
  --sample-file /path/to/sample_ids.txt
```

For population selection, provide tab-separated metadata:

```text
sample	population
sample_1	population_a
sample_2	population_a
sample_3	population_b
```

```bash
epiresim reference build /path/to/panel.vcf.gz \
  --output /path/to/reference_chr1.epiref \
  --genome-build GRCh38 \
  --chromosome 1 \
  --sample-metadata /path/to/sample_metadata.tsv \
  --population population_a
```

Use `--sample-column` and `--population-column` when the metadata uses different
column names. Population-panel samples are all donor controls; no artificial
case labels are added.

## Native bundle contents

A `.epiref` bundle is a versioned directory:

```text
reference_chr1.epiref/
├── manifest.json
├── genotypes.npy
├── variants.tsv
└── samples.tsv
```

- `genotypes.npy` is an `int8` samples-by-variants counted-allele dosage matrix
  using `0/1/2`. VCF builds use the selected population's minor allele as the
  counted allele.
- `variants.tsv` records coordinates, alleles, counted-allele frequency, and
  source-ALT orientation changes.
- `samples.tsv` records selected sample IDs and populations.
- `manifest.json` records the format version, genome build, source checksum,
  filters, skipped-record counts, dimensions, and component checksums.

The input path is deliberately not copied into the manifest. Record a stable
public source using `--source-name`, `--source-release`, and `--source-url`.

Inspect or validate a bundle before simulation:

```bash
epiresim reference inspect /path/to/reference_chr1.epiref
epiresim reference validate /path/to/reference_chr1.epiref
```

## Convert legacy MATLAB references

Import a MATLAB v5 reference into the native format:

```bash
epiresim reference import-mat /path/to/reference.mat \
  --output /path/to/reference.epiref \
  --genome-build unknown
```

Only rows with legacy control label `2` are retained. Because the optional
legacy variant metadata has no documented column schema, the importer does not
infer coordinates or allele meanings from it; it records placeholders and
preserves the original column order.

The historical matrix also contains columns where the frequency calculated
from codes `2` and `3` exceeds 0.5. Therefore, the importer conservatively calls
legacy `0/1/2` values **counted-allele dosage**, not verified minor-allele
dosage. It does not flip those columns, because doing so would change legacy
simulation behavior.

Export a native bundle for the original MATLAB interface when needed:

```bash
epiresim reference export-mat /path/to/reference.epiref \
  --output /path/to/reference.mat
```

MATLAB export is a compatibility bridge. The native bundle remains the
recommended representation for new Python workflows.

## Run a simulation

Pass the bundle directory in the same position previously occupied by the MAT
file:

```bash
epiresim simulate /path/to/reference_chr1.epiref \
  --cases 100 \
  --controls 100 \
  --snps 50 \
  --maf 0.20 0.30 \
  --prevalence 0.20 \
  --order 2 \
  --replicates 10 \
  --prefix simulation \
  --format txt \
  --seed 42 \
  --output-dir results \
  --mode strict
```

The requested SNP window must fit inside the bundle. Compatibility mode retains
the original window-selection expression and therefore requires at least two
more variants than the requested window.

## Legacy MATLAB schema

Direct MATLAB input remains supported and must contain:

| Variable | Shape | Required content |
|---|---|---|
| `pts` | samples × SNPs | Numeric genotype codes `1`, `2`, or `3`. |
| `SampleInfo` | samples × at least 5 columns | Column five contains class labels; controls use `2`. |
| `SNPInfo` | SNPs × metadata columns | Optional metadata retained when dimensions agree. |

For a biallelic SNP, legacy codes `1/2/3` represent zero, one, and two copies of
the encoded allele. The original implementation describes that allele as minor,
but the supplied data do not satisfy that interpretation consistently. Do not
provide conventional dosage `0/1/2` without converting it or using the native
builder.

## Privacy and authorization

Simulated rows are mosaics of donor genotypes. Treat references and outputs
according to the consent, data-use agreement, and security requirements of the
source data. Resampling does not by itself establish anonymity.

Never commit restricted reference data or generated individual-level genotypes
to the public repository. Committed tests use redistributable synthetic fixtures.
