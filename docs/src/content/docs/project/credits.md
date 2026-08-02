---
title: Credits and citation
description: Credit the original EpiReSIM authors, paper, implementation, and scientific foundations.
---

This Python package is a rewrite of EpiReSIM and depends on the scientific and
software work of its original authors. Please cite the original publication
when using either implementation:

> Shang J, Cai X, Zhang T, Sun Y, Zhang Y, Liu J, Guan B. EpiReSIM: A
> Resampling Method of Epistatic Model without Marginal Effects Using
> Under-Determined System of Equations. *Genes*. 2022;13:2286.
> [doi:10.3390/genes13122286](https://doi.org/10.3390/genes13122286)

Original source and minimal manual:

- [CDMB-lab/EpiReSIM](https://github.com/CDMB-lab/EpiReSIM)
- oracle commit `16adb481b5b0223a5d97622e4df61ed6fc5b0c93`

The repository also records supporting references for no-marginal-effect
epistatic models and penetrance-table generation in its README and citation
metadata.

## Cite this rewrite

Use the repository's
[`CITATION.cff`](https://github.com/lescailab/EpiReSIM_conversion/blob/main/CITATION.cff)
through GitHub's “Cite this repository” control. When reporting simulated data,
also state:

- the rewrite version or commit;
- `compatibility` or `strict` mode;
- complete model parameters and seed;
- reference-data provenance and preprocessing;
- output quotas and replicate count; and
- relevant validation boundary.

## Implementation-assistance disclosure

The Python implementation and documentation were produced with assistance from
generative coding tools. Humans define the scientific requirements, acceptable
tolerances, validation scope, and release decisions. Correctness is evaluated
by comparison with the pinned original implementation, not by code review or
generation method alone.
