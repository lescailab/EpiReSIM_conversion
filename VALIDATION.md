# Validation policy

## Status

The reference MATLAB implementation is pinned to:

```text
16adb481b5b0223a5d97622e4df61ed6fc5b0c93
```

The MATLAB source in `code/` remains unchanged and is the validation oracle.
A licensed MATLAB comparison and remediation run was completed on 2026-08-02.
The initial run exposed nonlinear-solver, RNG, success/failure, dtype, and
serialization differences. After targeted compatibility corrections, the
registered synthetic matrix passed. Release-wide cross-language equivalence is
still not claimed because the committed golden corpus and remaining release
gates below are incomplete. See
`validation/equivalence/2026-08-02/REPORT.md`.

## Automated validation

The Python suite covers:

- genotype-probability ordering, normalization, and property tests;
- generic and legacy constraint matrices for orders 2–5;
- the known fourth-order legacy index map;
- analytic nonlinear Jacobians against finite differences;
- bounded prevalence and prevalence-plus-heritability solving;
- invalid MATLAB schemas, genotype codes, labels, and output collisions;
- seeded fragment resampling and exact strict-mode quotas;
- end-to-end API and CLI reproducibility;
- MATLAB R2026a twister and single-choice `randperm` compatibility probes;
- MATLAB-compatible nonlinear Gauss–Seidel convergence behavior;
- MATLAB-class `double`, compressed Level-5 compatibility output;
- recomputation of the eight published model tables; and
- wheel, Conda, and container smoke installation in CI.

The published tables contain six-decimal MAFs and penetrances. Recomputed
statistics therefore use tolerances that include documented rounding loss:
`6e-4` for prevalence, `6e-3` for heritability, and the original `<0.05`
marginal threshold.

## Required MATLAB golden corpus

Before an equivalence release:

1. Run the pinned source with a recorded MATLAB release and Symbolic Math
   Toolbox version.
2. Record exact commands, seeds, platform, dependency versions, and source
   commit.
3. Cover orders 2–5, prevalence-only and heritability-constrained models,
   MATLAB and text outputs, multiple reference dimensions, and expected
   failures.
4. Store only small redistributable synthetic fixtures.
5. Add `tests/golden/manifest.json` with checksums and environment metadata.
6. Compare internal floating-point penetrances within `5e-7`.
7. Compare normalized text and log output byte-for-byte.
8. Compare MATLAB variables after loading: names, shapes, dtypes, and values.

The compatibility test is intentionally skipped until that manifest exists.

## Stochastic validation

Statistical assessment supplements, but does not replace, same-seed exact-output
comparison. Full equivalence requires a demonstrated MATLAB-compatible random
stream and random-consumption order for every supported MATLAB release.
Repeated runs must also compare:

- SNP minor-allele frequencies;
- genotype-frequency distributions;
- pairwise linkage disequilibrium;
- phenotype prevalence and exact quotas;
- causal-genotype risks; and
- fragment-length and donor distributions.

Confidence intervals, replicate counts, and equivalence margins must be
registered in the golden manifest before results are examined. Statistical
agreement may support a narrower distributional claim, but individual
same-seed mismatches still fail the full Rewrite.bio equivalence gate.

## Performance claims

No speed or memory claim may be published until benchmarks record exact
commands, data dimensions, CPU architecture, operating system, dependency
versions, elapsed time, and peak resident memory. Benchmarks must cover x86-64
and ARM64.

## Artifact validation status

The `lescailab/epiresim 0.1.0 py_1` noarch Conda package was built from a
checksummed archive of the recorded source commit, passed the recipe tests, and
was installed successfully from the public channel into a clean Python 3.11
environment. See `validation/packaging/2026-08-02/CONDA.md`. Clean wheel and OCI
artifact validation remain outstanding.

## Release gate

A stable equivalence claim requires:

- all automated tests passing;
- completed MATLAB golden and stochastic validation;
- successful clean installation of wheel, Conda, and OCI artifacts;
- documented unsupported behavior and compatibility deviations;
- current citation, license, changelog, and governance files; and
- human approval of the validation report.
