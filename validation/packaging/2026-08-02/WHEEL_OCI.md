# Wheel and OCI validation — 2026-08-02

## Outcome

The wheel installed with resolved dependencies into a fresh Python 3.11
environment and passed its CLI smoke test. The OCI image built from the same
source state and passed CLI, synthetic simulation, and integer MATLAB-class
output checks.

## Wheel

- Artifact: `epiresim-0.1.0-py3-none-any.whl`
- SHA-256: `779991e92a41afbdc9a9a1ce338815165b4d05457c967c321115af7c3683ade8`
- Source distribution SHA-256:
  `d195fba55bb4db55bf4e0fe2a2e9519edf1214a00a8a59be7f38c0835d90a555`
- Validation environment: Python 3.11.15, Apple Silicon
- Resolved dependencies: NumPy 2.4.6 and SciPy 1.17.1

Reproduction commands, with ephemeral paths normalized:

```bash
python -m build --no-isolation --outdir /path/to/dist
python3.11 -m venv /path/to/clean-env
/path/to/clean-env/bin/python -m pip install \
  /path/to/dist/epiresim-0.1.0-py3-none-any.whl
/path/to/clean-env/bin/epiresim --help
```

The build and installation commands completed successfully. The installed
metadata and imports reported EpiReSIM 0.1.0, NumPy 2.4.6, and SciPy 1.17.1.

## OCI image

- Tag used for local validation: `epiresim:validation-20260802`
- Image ID:
  `sha256:815ff000327a5af9f8027b6ec594d8525e50fa5649df7638d7089b141a750504`
- Local image size: 452,480,331 bytes
- Docker engine: 29.6.1
- Runtime: Python 3.11.15 on `aarch64`
- Installed dependencies: NumPy 2.4.6 and SciPy 1.17.1

Reproduction commands:

```bash
docker build --tag epiresim:validation-20260802 .
docker run --rm epiresim:validation-20260802 --help
docker run --rm \
  --volume /path/to/golden/references:/fixtures:ro \
  epiresim:validation-20260802 simulate \
  /fixtures/reference_80x16.mat \
  --cases 2 --controls 2 --snps 8 \
  --maf 0.2 0.3 --prevalence 0.2 --order 2 \
  --replicates 1 --prefix simulation --format mat \
  --seed 73 --output-dir /tmp/results --mode compatibility
```

The synthetic smoke run generated one dataset. A follow-up inspection inside
the container confirmed that `SNP` had shape `(4, 9)` and MATLAB class `int8`,
matching the integer-class golden reference semantics.

The image is a local validation artifact, not evidence that an image was pushed
to a registry. Its immutable local image ID records the exact tested image.
