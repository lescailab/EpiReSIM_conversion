---
title: Install EpiReSIM
description: Install the Python rewrite in an isolated environment and verify the command line.
---

EpiReSIM requires Python 3.11 or newer. Use an isolated environment so its
NumPy and SciPy requirements do not alter unrelated analyses.

## Install with Conda

The tested `noarch: python` package is published on the `lescailab` channel.
Use conda-forge for NumPy, SciPy, and their compiled dependencies:

```bash
conda create --name epiresim \
  --channel lescailab \
  --channel conda-forge \
  --strict-channel-priority \
  epiresim=0.1.0
conda activate epiresim
```

Pinning `0.1.0` makes this installation record explicit. The package was built
as `noarch`, so the EpiReSIM code is shared across platforms; Conda still
selects platform-specific NumPy and SciPy builds.

## Install from the repository

```bash
git clone https://github.com/lescailab/EpiReSIM_conversion.git
cd EpiReSIM_conversion
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Verify the installation

```bash
epiresim --help
epiresim simulate --help
```

The first command lists the available subcommands. The second lists every
simulation parameter.

## Development installation

Use this only when changing the source or running the test suite:

```bash
python -m pip install -e ".[dev]"
pytest
```

Package metadata and the clean remote-install test are recorded in the
[Conda packaging report](https://github.com/lescailab/EpiReSIM_conversion/blob/main/validation/packaging/2026-08-02/CONDA.md).

## Platform support

The package is pure Python, while NumPy and SciPy provide platform-specific
compiled libraries. The project tests Python 3.11–3.14 on Linux and macOS.
Check the repository's current CI before relying on an untested operating
system or architecture.
