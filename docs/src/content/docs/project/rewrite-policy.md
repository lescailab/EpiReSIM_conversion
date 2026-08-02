---
title: Rewrite.bio commitments
description: How EpiReSIM applies responsible scientific-software rewrite principles.
---

This project treats the principles at [rewrites.bio](https://rewrites.bio/) as
binding repository policy.

## Credit and provenance

The original authors, paper, license, repository, and pinned source commit are
visible in the README, manual, citation metadata, validation record, and release
materials. Users are instructed to cite the original work.

## Emulate exactly

Compatibility mode treats filenames, schemas, MATLAB classes, ordering, text
format, logs, overwrite behavior, success/failure, floating-point tolerances,
and same-seed stochastic output as observable behavior. Improvements that change
scientific behavior belong in strict mode and are not labeled equivalent.

## Be transparent

The project discloses generative implementation assistance, exact validation
environment, synthetic scope, deviations in raw MAT encoding, unsupported
features, and unfinished release gates.

## Work in validated increments

The original MATLAB implementation is an immutable oracle. Focused components
are compared before scope expands, and tolerances are registered before results
are inspected.

## Pin and document

Validation records source commits, dependency versions, commands, fixtures,
checksums, environment, failures, and coverage gaps. Compatibility claims are
always tied to that recorded boundary.

## Maintain and govern

The repository includes contribution, security, governance, changelog, citation,
and validation policies. New releases must preserve compatibility or explicitly
document and revalidate changes.

## Responsible upstream contact

Suspected original defects must be reproduced manually against clean data and
understood before a human contacts upstream maintainers. Automated issue filing
is prohibited.

The authoritative project rule is
[`REWRITE_POLICY.md`](https://github.com/lescailab/EpiReSIM_conversion/blob/main/REWRITE_POLICY.md).
