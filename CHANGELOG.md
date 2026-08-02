# Changelog

All notable changes are documented here. The project follows Semantic
Versioning after the first stable release.

## Unreleased

### Added

- Versioned, checksummed `.epiref` reference bundles with VCF/VCF.GZ
  construction, population/sample selection, validation, inspection, and
  MATLAB import/export.
- Exact compatibility- and strict-mode simulation parity tests between legacy
  MATLAB references and their native conversions.
- Transparent documentation of assumptions required because the historical
  reference-construction procedure was not recorded reproducibly.

## 0.1.0 — 2026-08-02

### Added

- Python package with public dataclasses, API, and `epiresim simulate` CLI.
- Compatibility and bounded strict penetrance solvers for orders 2–5.
- MATLAB v5 reference loading and MATLAB/text compatibility outputs.
- Seeded fragment resampling, phenotype assignment, and case/control quotas.
- Scientific, property, integration, published-model, and parity-gate tests.
- Wheel, Conda, and OCI packaging definitions.
- Beginner-oriented Astro documentation covering genetics, mathematics,
  reference data, model recipes, interfaces, outputs, limitations, validation,
  provenance, and Rewrite.bio commitments, with automatic GitHub Pages
  deployment.
- Checksummed `noarch: python` package published as
  `lescailab/epiresim 0.1.0 py_1`, with a clean remote installation test.

### Validation

- Corrected compatibility-mode nonlinear iteration, MATLAB twister random
  consumption, single-choice `randperm` behavior, and compressed MATLAB-class
  `double` output after a licensed MATLAB R2026a comparison.
- The remediation run matched 24/24 execution statuses, 48/48 same-seed output
  matrices, text files, and dtypes, 24/24 logs, and 200/200 stochastic replicate
  matrices. A committed golden corpus, a representative historical-reference
  comparison, clean wheel/Conda/OCI checks, and human approval complete the
  release gate for the declared MATLAB R2026a Update 4 on Apple Silicon scope.
