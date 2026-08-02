# Rewrite policy

EpiReSIM is governed as a scientific rewrite under the principles of
[Rewrite.bio](https://rewrites.bio/). Correctness is established by comparison
with the pinned original implementation, not by code review or internal tests
alone.

## Commitments

1. **Credit and provenance** — retain visible credit to the original authors,
   paper, license, and source version.
2. **Exact compatibility** — compatibility mode must reproduce every observable
   behavior of the validated original. Floating-point tolerances must be defined
   before results are examined.
3. **Transparency** — disclose implementation assistance, validation methods,
   unsupported behavior, incomplete coverage, and known deviations.
4. **Focused scope** — implement only declared capabilities and fail explicitly
   for unsupported inputs.
5. **Reproducibility** — pin versions and record commands, environments,
   fixtures, checksums, and comparison results in the repository.
6. **Stewardship** — preserve compatibility across releases, revalidate changes,
   maintain governance and changelogs, and investigate upstream issues manually.

## Claims

Passing Python-only tests does not establish MATLAB equivalence. Statistical
agreement does not override a same-seed or format mismatch. Strict mode is a
scientifically motivated extension and is not represented as MATLAB-equivalent.

The project may claim full equivalence only after every release gate in
`VALIDATION.md` passes and the validation report receives explicit human
approval. Until then, documentation and release metadata must state the exact
validated subset and all outstanding deviations.
