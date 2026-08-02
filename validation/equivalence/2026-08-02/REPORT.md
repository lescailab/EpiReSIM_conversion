# MATLAB–Python equivalence report — 2026-08-02

## Outcome

**The registered synthetic equivalence matrix passes after remediation.** The
initial run exposed nonlinear iteration, RNG-consumption, status, and output
encoding differences. Targeted compatibility changes were then tested against
the unchanged MATLAB oracle without relaxing the pre-registered numerical
tolerance.

This establishes equivalence for the scenarios and environment recorded below,
not for every input or MATLAB release. The reviewed golden corpus,
representative historical-reference comparison, artifact validation, and
explicit human approval complete the release gate for the declared MATLAB
R2026a Update 4 on Apple Silicon compatibility scope.

## Provenance and environment

- Original oracle commit: `16adb481b5b0223a5d97622e4df61ed6fc5b0c93`
- Oracle integrity: `git diff --exit-code <oracle-commit> -- code` passed
- MATLAB: R2026a Update 4, Apple Silicon
- Symbolic Math Toolbox: 26.1
- Toxo dependency: `0e49e8d2454a501e098b9456bfad53226c34eed1`
- Python: 3.11.15
- NumPy: 2.4.6
- SciPy: 1.17.1
- Final Python suite: 77 passed
- Committed test data: generated, redistributable synthetic genotypes only
- Representative check: ephemeral use of the original project's public
  historical reference; no additional genotypes or resampled outputs committed

The Toxo commit is the last public repository state predating publication and
is a documented dependency assumption; the original project did not record its
exact Toxo revision.

## Registered test design

The synthetic reference contained 240 samples and 48 SNPs. The first 200
samples used control label `2`; the remaining 40 used label `1`. Genotypes were
drawn in Python with NumPy seed 711 under Hardy–Weinberg probabilities, cycling
target MAFs `[0.10, 0.15, 0.20, 0.25, 0.30, 0.40]` across columns. MATLAB read
the resulting Level-5 MAT fixture through the unchanged `Data.m` implementation.

Deterministic solver inputs were prevalence `0.2` and:

| Order | MAFs | Prevalence-only H2 | Joint H2 |
|---:|---|---:|---:|
| 2 | `[0.2, 0.3]` | `0` | `0.05` |
| 3 | `[0.1, 0.2, 0.3]` | `0` | `0.05` |
| 4 | `[0.1, 0.2, 0.3, 0.4]` | `0` | `0.05` |
| 5 | `[0.1, 0.15, 0.2, 0.25, 0.3]` | `0` | `0.02` |

End-to-end cases used seeds 11, 29, and 47; 6 cases, 6 controls, 24 SNPs,
two replicates, and both MAT and text outputs. The stochastic study used seed
20260802; 50 cases, 50 controls, 24 SNPs, 200 replicates, and the order-two
prevalence-only model.

The committed golden corpus repeats all eight deterministic and end-to-end case
classes at seed 11. It adds a second reference with 80 samples and 16 SNPs,
integer-class genotypes, seed 73, and an eight-SNP output window. This covers
both `double` and integer MATLAB output-class propagation. Missing-variable and
insufficient-column fixtures cover safe expected failures.

## Compatibility corrections

The remediation made four focused changes:

1. The nonlinear compatibility solver now reproduces the original explicit
   lower-matrix inverse and its convergence-before-assignment behavior.
2. Compatibility mode uses MATLAB's seeded twister sequence, including the
   R2026a random-consumption behavior of `randperm(n, 1)` used for locus choice.
3. Compatibility MAT output uses compressed Level-5 elements and exposes `SNP`
   using the class propagated by the MATLAB reference input.
4. The compatibility writer now preserves that reference-dependent MATLAB
   output class; the representative historical reference exposed the previously
   untested integer-class path.

Strict mode retains its independent generator, bounded solver, integer MAT
storage, and other documented safety behavior.

## Deterministic calculations

Eight registered cases covered orders 2–5 with prevalence-only and joint
heritability constraints.

| Case class | Remediated result |
|---|---|
| Genotype probabilities | Passed; maximum absolute difference `5.55e-17` |
| Prevalence-only penetrance, orders 2–5 | Passed; maximum absolute difference `7.22e-16` |
| Order 2 heritability penetrance | Passed; maximum difference `1.71e-15` |
| Order 3 heritability penetrance | Passed; maximum difference `5.84e-14` |
| Order 4 heritability fixed case | Both implementations rejected the model |
| Order 5 heritability penetrance | Passed; maximum difference `8.21e-11` |

The registered penetrance tolerance was `5e-7`; it was not changed after the
initial failures were observed. Before remediation, the maximum nonlinear
penetrance difference was `2.027e-05`.

## End-to-end comparison

The matrix comprised orders 2–5, both solver strategies, seeds 11, 29, and 47,
two replicates, and MATLAB plus text outputs.

- Paired executions with matching success status: **24/24**.
- Exact loaded matrix values and shapes: **48/48**.
- Matching MATLAB variable names, class dtypes, and phenotype quotas: **48/48**.
- Byte-identical text files: **48/48**.
- Byte-identical model logs: **24/24**.

Both writers produce compressed Level-5 MAT files whose `SNP` variable has
MATLAB class `double`. Their raw file bytes are not expected to match: headers
contain implementation-specific metadata, and MATLAB stores these integer-valued
double arrays using a compact internal numeric element while SciPy writes an
`miDOUBLE` element. Validation therefore compares the loaded variable name,
shape, MATLAB class, and exact values, as registered in `VALIDATION.md`.

Within each implementation, rerunning into the same directory behaved alike:
MAT and log files were overwritten deterministically, while text output appended
from 12 to 24 rows.

## Supplemental stochastic comparison

A representative order-two prevalence-only run generated 200 replicates of 100
samples in each implementation.

- Both stacks had shape `(200, 100, 25)` and exact 50/50 quotas.
- Exact same-seed matrix matches: **200/200**.
- All allele-frequency and genotype-frequency differences: `0`.
- MATLAB and Python mean pairwise r-squared:
  `0.00035392548139573284` in both implementations.

This exact result confirms the validated random stream and consumption order for
the exercised R2026a path; the statistical summaries are supplementary.

## Golden and representative-reference validation

The committed redistributable corpus contains two synthetic reference
dimensions, eight deterministic oracle files, 18 end-to-end MAT outputs, 18
byte-comparison text outputs, nine logs, expected-failure input, and a manifest
with SHA-256 checksums, commands, versions, seeds, and pre-registered
tolerances. Its executable comparison suite passed **20/20** tests.

An additional ephemeral comparison used the public historical reference bundled
with the original project. At seed 73, both implementations produced **2/2**
exact loaded matrices with matching MATLAB classes, **2/2** byte-identical text
files, and **1/1** byte-identical log. No additional reference genotypes or
resampled outputs were committed. The historical reference has incomplete
construction provenance and is therefore compatibility evidence, not a
recommended reference source for new analyses.

## Failure and interface behavior

Both implementations rejected fixtures missing required MATLAB variables and
requests with insufficient reference columns. MATLAB raised native indexing or
field errors; Python raised explicit `InputValidationError` exceptions. Unsafe
non-termination cases were not executed against the unbounded original.

## Release decision and boundary

The automated suite, committed golden corpus, stochastic study, representative
historical-reference comparison, clean wheel/Conda/OCI checks, documentation,
citation, license, changelog, governance review, and explicit maintainer
approval all passed on 2026-08-02. The release gate in `VALIDATION.md` is
therefore complete for MATLAB R2026a Update 4 on Apple Silicon.

Other MATLAB releases, architectures, and untested boundary inputs remain
outside the equivalence claim. Strict mode remains a non-equivalent extension.
Expanding either scope requires a new pre-registered validation run.
