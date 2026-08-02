---
title: Compatibility or strict?
description: Choose between legacy MATLAB behavior and the safer bounded Python extension.
---

The two modes answer different needs. Compatibility is the default so existing
commands preserve the translated program's legacy intent; strict must be
requested explicitly.

| Behavior | Compatibility | Strict |
|---|---|---|
| Primary goal | Match the pinned MATLAB implementation | Enforce safer mathematical and file-handling rules |
| Random generator | MATLAB-compatible twister for validated seeds | NumPy modern generator |
| Constraint maps | Original order-specific maps | Generic tensor construction |
| Linear solver | Original minimum-norm behavior | Bounded linear least squares |
| Nonlinear solver | Original Newton/Gauss–Seidel behavior | Bounded trust-region least squares |
| Penetrance bounds | Negative values clipped; upper values not clipped | Every value required in `[0, 1]` |
| Causal loci | Repeated locus can occur | Loci must be distinct |
| Existing outputs | MAT/log overwrite; text appends | Any collision is rejected |
| MAT storage | Compressed MATLAB-class `double` | Uncompressed integer matrix |
| Safety limits | Added to stop legacy non-termination | Added and enforced |

## Choose compatibility when

- reproducing an existing MATLAB analysis;
- testing same-seed behavior against the validated oracle;
- preserving legacy filenames, text formatting, and overwrite behavior; or
- contributing a new equivalence fixture.

The validated scope is MATLAB R2026a Update 4 on Apple Silicon with the versions
recorded in the equivalence report. Compatibility is not a blanket claim for
every MATLAB release or dataset.

## Choose strict when

- designing a new simulation rather than reproducing a legacy one;
- every penetrance must be a valid probability;
- causal loci must be distinct;
- accidental output overwrite must be prevented; or
- explicit infeasibility is preferable to legacy numerical behavior.

Strict mode is a documented extension. Its outputs are not expected to match
MATLAB.

:::caution
Do not switch modes mid-study without treating it as a methodological change.
Record the mode with every simulation command and result.
:::
