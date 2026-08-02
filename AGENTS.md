# Repository instructions

## Rewrite.bio compliance

This project is a rewrite of established scientific software and **must** follow
the principles published at [rewrites.bio](https://rewrites.bio/). These rules
apply to every human contribution and automated coding session.

- Keep the original authors, publication, license, and source version visibly
  credited.
- Treat `code/` at commit `16adb481b5b0223a5d97622e4df61ed6fc5b0c93`
  as the immutable compatibility oracle.
- Do not describe compatibility mode as equivalent, validated, or a drop-in
  replacement unless the release gates in `VALIDATION.md` pass.
- Require exact observable behavior for compatibility mode: filenames, schemas,
  dtypes, ordering, formatting, overwrite behavior, and same-seed stochastic
  outputs all count. Pre-registered numerical tolerances are permitted only for
  floating-point calculations.
- Statistical similarity is supplementary evidence and never substitutes for a
  failed exact-output comparison.
- Keep strict mode clearly identified as a non-equivalent extension.
- Validate focused components against the oracle before expanding scope. Never
  relax a tolerance after examining a failing result without a documented,
  scientifically approved justification.
- Pin validation dependencies and record exact versions, commands, fixtures,
  checksums, environments, failures, and coverage gaps in the repository.
- Use redistributable synthetic fixtures for committed tests. Representative
  real-data validation must respect authorization and privacy and must not add
  identifiable inputs or resampled genotypes to the repository.
- Preserve transparent disclosure of implementation assistance and validation
  limitations.
- Verify suspected defects manually against the original before contacting
  upstream maintainers; never send automated upstream reports.

The current cross-language result is recorded in
`validation/equivalence/2026-08-02/REPORT.md`. The registered synthetic
cross-language matrix, committed golden corpus, representative historical-data
comparison, artifact checks, and human approval satisfy the release gate for
the declared MATLAB R2026a Update 4 on Apple Silicon scope. Do not broaden this
claim to other MATLAB releases, architectures, or untested inputs.
