# Changelog

All notable changes are documented here. The project follows Semantic
Versioning after the first stable release.

## 0.1.0 — Unreleased

### Added

- Python package with public dataclasses, API, and `epiresim simulate` CLI.
- Compatibility and bounded strict penetrance solvers for orders 2–5.
- MATLAB v5 reference loading and MATLAB/text compatibility outputs.
- Seeded fragment resampling, phenotype assignment, and case/control quotas.
- Scientific, property, integration, published-model, and parity-gate tests.
- Wheel, Conda, and OCI packaging definitions.

### Validation

- Corrected compatibility-mode nonlinear iteration, MATLAB twister random
  consumption, single-choice `randperm` behavior, and compressed MATLAB-class
  `double` output after a licensed MATLAB R2026a comparison.
- The remediation run matched 24/24 execution statuses, 48/48 same-seed output
  matrices, text files, and dtypes, 24/24 logs, and 200/200 stochastic replicate
  matrices. Release-wide equivalence remains unclaimed pending the full release
  gate in `VALIDATION.md`.
