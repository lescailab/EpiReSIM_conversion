---
title: Validation status
description: Exact scope, results, and remaining gates for comparison with the pinned MATLAB implementation.
---

## Current result

The registered synthetic equivalence matrix passes after remediation against:

- original source commit `16adb481b5b0223a5d97622e4df61ed6fc5b0c93`;
- MATLAB R2026a Update 4 on Apple Silicon;
- Symbolic Math Toolbox 26.1; and
- the pinned Toxo dependency recorded in the repository report.

The original MATLAB files under `code/` were unchanged during validation.

## Recorded comparisons

| Validation component | Result |
|---|---:|
| Paired execution statuses | 24/24 matched |
| End-to-end loaded matrices | 48/48 exact |
| Text files | 48/48 byte-identical |
| Model logs | 24/24 byte-identical |
| 200-replicate same-seed study | 200/200 matrices exact |
| Maximum nonlinear penetrance difference | $8.21\times10^{-11}$ |
| Registered penetrance tolerance | $5\times10^{-7}$ |

Both MAT writers expose a compressed Level-5 `SNP` variable with MATLAB class
`double`. Raw file bytes differ because MATLAB and SciPy use different headers
and internal numeric storage; validation compares the registered loaded schema
and exact values.

## What remains

Release-wide equivalence is not yet claimed. Outstanding gates include:

- a reviewed, committed, redistributable golden corpus and manifest;
- broader reference dimensions, boundaries, and expected failures;
- authorized representative real-data comparison;
- validation of supported MATLAB releases and architectures, or an explicit
  R2026a compatibility boundary;
- clean wheel and OCI artifact validation (the public noarch Conda 0.1.0
  package has passed a clean remote-install check); and
- explicit human approval of the completed release report.

Read the repository's
[full report](https://github.com/lescailab/EpiReSIM_conversion/blob/main/validation/equivalence/2026-08-02/REPORT.md)
and
[validation policy](https://github.com/lescailab/EpiReSIM_conversion/blob/main/VALIDATION.md)
before making a substitution claim.

:::caution
Passing Python-only tests does not establish MATLAB equivalence. Statistical
similarity cannot replace a failed same-seed comparison.
:::
