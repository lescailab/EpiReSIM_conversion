# MATLAB golden corpus

This directory contains small, redistributable synthetic references and outputs
from the pinned MATLAB reference implementation. No private or representative
real dataset is included.

`manifest.json` records the source commit, MATLAB and Symbolic Math Toolbox
versions, platform, commands, seeds, fixture checksums, and pre-registered
comparison tolerances. The compatibility tests verify every checksum, compare
deterministic floating-point results within the registered tolerance, and
compare loaded matrices, MATLAB dtypes, text output, and logs exactly.
