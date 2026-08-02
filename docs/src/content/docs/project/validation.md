---
title: Validation status
description: Exact scope, results, and release decision for comparison with the pinned MATLAB implementation.
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
| Representative historical-reference matrices | 2/2 exact, including dtype |
| Committed golden compatibility tests | 20/20 passed |
| Maximum nonlinear penetrance difference | $8.21\times10^{-11}$ |
| Registered penetrance tolerance | $5\times10^{-7}$ |

For the main registered matrix, both MAT writers expose a compressed Level-5
`SNP` variable with MATLAB class `double`. The compact golden fixture and the
representative comparison additionally verify integer-class propagation. Raw
file bytes can differ because MATLAB and SciPy use different headers and
internal numeric storage; validation compares the registered loaded schema,
class, and exact values.

## Release decision

The release gate passed on 2026-08-02 for the declared MATLAB R2026a Update 4
on Apple Silicon compatibility scope. The completed gate includes:

- a reviewed, committed, redistributable golden corpus and manifest;
- orders 2–5, both solver strategies, two reference dimensions and MATLAB
  classes, expected failures, MAT/text output, and exact logs;
- an ephemeral representative historical-reference comparison with no new
  genotype data committed;
- clean wheel, public Conda, and OCI installation checks; and
- explicit human approval of the completed report.

The bundled historical reference has incomplete construction provenance, so it
is evidence for compatibility behavior rather than a recommended reference for
new analyses. Other MATLAB releases, architectures, and untested boundary inputs
remain outside the equivalence claim.

Read the repository's
[full report](https://github.com/lescailab/EpiReSIM_conversion/blob/main/validation/equivalence/2026-08-02/REPORT.md)
and
[validation policy](https://github.com/lescailab/EpiReSIM_conversion/blob/main/VALIDATION.md)
before making a substitution claim.

:::caution
Passing Python-only tests does not establish MATLAB equivalence. Statistical
similarity cannot replace a failed same-seed comparison.
:::
