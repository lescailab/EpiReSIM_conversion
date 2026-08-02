---
title: Install EpiReSIM
description: Install the Python rewrite in an isolated environment and verify the command line.
---

EpiReSIM requires Python 3.11 or newer. Use an isolated environment so its
NumPy and SciPy requirements do not alter unrelated analyses.

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

:::note[Conda]
A noarch Conda package is being prepared for the `lescailab` channel. This page
will show a tested installation command once the uploaded package has been
verified from a clean environment.
:::

## Platform support

The package is pure Python, while NumPy and SciPy provide platform-specific
compiled libraries. The project tests Python 3.11–3.14 on Linux and macOS.
Check the repository's current CI before relying on an untested operating
system or architecture.
