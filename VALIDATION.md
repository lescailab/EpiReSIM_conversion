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
registered synthetic matrix and an ephemeral representative historical-reference
comparison passed. The committed golden corpus, stochastic study, clean
wheel/Conda/OCI checks, documentation and governance review, and explicit human
approval complete the release gate for the declared MATLAB R2026a Update 4 on
Apple Silicon scope. This does not establish equivalence for other MATLAB
releases, architectures, or untested inputs. See
`validation/equivalence/2026-08-02/REPORT.md`.

## Automated validation

The Python suite covers:

- genotype-probability ordering, normalization, and property tests;
- generic and legacy constraint matrices for orders 2–5;
- the known fourth-order legacy index map;
- analytic nonlinear Jacobians against finite differences;
- bounded prevalence and prevalence-plus-heritability solving;
- invalid MATLAB schemas, genotype codes, labels, and output collisions;
- native reference schema, dimensions, genotype encoding, and component
  checksums;
- VCF sample/population selection, hard-call filtering, and minor-allele
  orientation;
- exact same-seed simulation equality after MATLAB-to-native conversion in both
  compatibility and strict modes;
- MATLAB export round-trip preservation of donor genotypes and control labels;
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

Native-format conversion has a stronger gate than the cross-language solver
comparison: because it only changes storage, selected loci, observed MAFs,
penetrances, and generated integer matrices must be exactly equal for the same
configuration and seed. No numerical tolerance is applied. A tolerance may be
registered in advance for a future adapter only when its specified source
representation necessarily introduces floating-point conversion; exact
genotypes, ordering, sample selection, and simulation matrices remain required.

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

The committed manifest exists and the compatibility tests enforce all eight
requirements above. The compact fixture uses an integer MATLAB class so output
class preservation is covered in addition to the original double-valued matrix.

## Stochastic validation

Statistical assessment supplements, but does not replace, same-seed exact-output
comparison. Equivalence requires a demonstrated MATLAB-compatible random stream
and random-consumption order for every MATLAB release inside the declared
compatibility boundary. That boundary is currently R2026a Update 4 on Apple
Silicon.
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
installation checks were also completed: the wheel resolved dependencies in a
fresh Python 3.11 environment, and the OCI image passed CLI and synthetic
simulation smoke tests. See
`validation/packaging/2026-08-02/WHEEL_OCI.md`.

## Release gate

A stable equivalence claim requires:

- all automated tests passing;
- completed MATLAB golden and stochastic validation;
- successful clean installation of wheel, Conda, and OCI artifacts;
- documented unsupported behavior and compatibility deviations;
- current citation, license, changelog, and governance files; and
- human approval of the validation report.

All gates above passed on 2026-08-02 for the explicitly bounded R2026a Update 4
on Apple Silicon compatibility claim. Future changes to compatibility behavior
or expansion of that boundary require revalidation.
