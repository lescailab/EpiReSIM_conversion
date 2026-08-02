# EpiReSIM

EpiReSIM is an experimental Python rewrite of the MATLAB simulator described
by Shang *et al.* (2022). It generates case-control SNP matrices containing an
epistatic model without marginal effects (eNME) while resampling fragments from
a reference genotype dataset.

The package currently supports interaction orders 2–5, MATLAB v5 reference
files, MATLAB-compatible matrix and text outputs, a compatibility mode, and a
bounded strict mode.

> **Validation status:** a licensed MATLAB comparison and remediation run now
> passes the registered synthetic deterministic, same-seed end-to-end, and
> 200-replicate stochastic matrices. Release-wide equivalence is not yet claimed
> because the reviewed golden corpus, broader fixtures, artifact checks, and
> human release approval remain outstanding. See [VALIDATION.md](VALIDATION.md)
> and the [2026-08-02 equivalence report](validation/equivalence/2026-08-02/REPORT.md).

## Installation

Python 3.11 or newer is required.

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e ".[dev]"
pytest
```

The full development/test environment is locked for Linux x86-64, Linux
ARM64, and Apple Silicon:

```bash
conda-lock install --name epiresim-dev conda-lock.yml
conda activate epiresim-dev
python -m pip install -e .
```

A `noarch: python` Conda recipe, environment definitions, and an OCI container
definition are included in the repository. The bundled reference dataset is
intentionally excluded from package and container artifacts.

## Documentation

The beginner-friendly manual is published at
[lescailab.github.io/EpiReSIM_conversion](https://lescailab.github.io/EpiReSIM_conversion/).
It covers the genetics and mathematics behind the model, reference-data
preparation, complete prevalence-only and heritability-constrained recipes,
interfaces, outputs, assumptions, validation, provenance, and Rewrite.bio
commitments. The Astro source lives in `docs/` and is deployed automatically by
GitHub Actions.

## Command line

The command maps the original 12 MATLAB arguments to named options:

```bash
epiresim simulate /path/to/reference.mat \
  --cases 100 \
  --controls 100 \
  --snps 50 \
  --maf 0.20 0.30 0.10 \
  --prevalence 0.20 \
  --heritability 0.30 \
  --order 3 \
  --replicates 10 \
  --prefix simulation \
  --format mat \
  --format txt \
  --seed 42 \
  --output-dir results \
  --mode strict
```

At least one `--format` is required. Compatibility is the default mode; strict
mode must be requested explicitly.

## Python API

```python
from pathlib import Path

from epiresim import SimulationConfig, run

config = SimulationConfig(
    reference_path=Path("/path/to/reference.mat"),
    case_count=100,
    control_count=100,
    snp_count=50,
    mafs=(0.20, 0.30, 0.10),
    prevalence=0.20,
    heritability=0.30,
    order=3,
    replicates=10,
    output_prefix="simulation",
    output_formats=("mat", "txt"),
    seed=42,
    output_dir=Path("results"),
    mode="strict",
)

result = run(config)
```

The public API also exposes `load_reference`, `genotype_probabilities`,
`solve_penetrance`, and `simulate`, together with the `ReferenceData`,
`PenetranceModel`, and `SimulationResult` result types.

## Modes

### Compatibility

Compatibility mode preserves the MATLAB implementation's:

- order-specific constraint maps, including its fourth-order indexing;
- minimum-norm linear solve and Newton/Gauss–Seidel nonlinear solve;
- negative-only penetrance clipping and 0.05 marginal verification threshold;
- random window, causal-locus, fragment, and quota-loop semantics;
- output names, genotype/phenotype codes, tab layout, and six-decimal log.

Potentially infinite loops have explicit safety limits. Python and MATLAB random
streams match for the validated R2026a same-seed scenarios; other MATLAB
releases remain to be validated.

### Strict

Strict mode:

- constructs generic no-marginal-effect constraints with tensor ordering;
- bounds every penetrance to `[0, 1]`;
- uses bounded linear or trust-region nonlinear least squares;
- supplies the nonlinear solver with an analytic Jacobian;
- rejects infeasible models and output collisions;
- requires distinct causal loci and exact case/control quotas;
- uses only a local seeded random generator; and
- reports deviations from Hardy–Weinberg and linkage-equilibrium assumptions.

Strict mode is scientifically safer but is not output-equivalent to MATLAB.

## Input and output schema

The reference MATLAB file must contain:

- `pts`: samples by SNPs, with genotype codes `1`, `2`, and `3`;
- `SampleInfo`: one row per sample and the class label in column five.

Control samples use legacy class label `2`. Optional `SNPInfo` rows are retained
when their dimensions match `pts`.

Each output matrix contains the selected SNP columns followed by a phenotype
column (`0` for control, `1` for case). MATLAB outputs contain a variable named
`SNP`; text outputs have no header and retain a trailing tab for compatibility.

## Mathematical definition

For minor-allele frequency $m_j$, locus $j$ has Hardy–Weinberg genotype
probabilities

$$
((1-m_j)^2,\;2m_j(1-m_j),\;m_j^2).
$$

Under linkage equilibrium, genotype combination $g$ has weight

$$
w_g = \prod_j q_{j,g_j}.
$$

For penetrance $f_g$, prevalence is $K=\sum_g w_gf_g$. Every single-locus
conditional penetrance is constrained to $K$, and broad-sense heritability on
the observed binary scale is

$$
H^2 = \frac{\sum_g w_g(f_g-K)^2}{K(1-K)}.
$$

The solver assumes Hardy–Weinberg and linkage equilibrium when constructing a
penetrance table. The resampling stage can preserve empirical linkage, so strict
mode reports diagnostics when the reference loci depart from those assumptions;
it does not silently replace the published mathematical model.

## Scope

In scope:

- binary case-control phenotypes;
- interaction orders 2–5;
- MATLAB v5 input and MATLAB/text output;
- the published HWE/linkage-equilibrium penetrance model;
- fragment resampling from control genotypes.

Out of scope:

- R bindings, VCF/PLINK input, GUIs, and workflow-engine wrappers;
- orders outside 2–5;
- empirical-LD penetrance solving;
- quantitative or multiclass phenotypes.

Unsupported behavior fails with an explicit error.

## Provenance and credit

This rewrite is based on:

- Shang J, Cai X, Zhang T, Sun Y, Zhang Y, Liu J, Guan B.
  “EpiReSIM: A Resampling Method of Epistatic Model without Marginal Effects
  Using Under-Determined System of Equations.”
  *Genes* 13 (2022), 2286.
  [doi:10.3390/genes13122286](https://doi.org/10.3390/genes13122286).
- Original implementation commit
  `16adb481b5b0223a5d97622e4df61ed6fc5b0c93`.
- Culverhouse R, Suarez B, Lin JH, Reich T.
  “A Perspective on Epistasis: Limits of Models Displaying No Main Effect.”
  [PMCID: PMC384920](https://pmc.ncbi.nlm.nih.gov/articles/PMC384920/).
- Urbanowicz RJ *et al.* “GAMETES: a fast, direct algorithm for generating
  pure, strict, epistatic models with random architectures.”
  [doi:10.1186/1756-0381-5-16](https://doi.org/10.1186/1756-0381-5-16).

Users of this rewrite should cite the original EpiReSIM paper.

## Implementation-assistance disclosure

The Python implementation was produced with assistance from generative coding
tools. The scientific requirements, compatibility boundaries, validation
criteria, and release decisions are human-defined. Correctness is evaluated
through tests and comparison with the pinned original implementation, not by
code generation or review alone.

Compliance with [Rewrite.bio](https://rewrites.bio/) is a binding project rule;
see [REWRITE_POLICY.md](REWRITE_POLICY.md). The project will not display an
equivalence claim or badge until the MATLAB golden validation gate is complete.

## License

The original and rewritten source are distributed under the MIT License. The
original copyright notice remains in [LICENSE](LICENSE).
