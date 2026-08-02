# Conda package validation — 2026-08-02

## Outcome

`epiresim 0.1.0 py_0` was built as `noarch: python`, passed the recipe tests,
uploaded to the public `lescailab` Anaconda channel, and installed successfully
from that channel into a clean Python 3.11 environment.

- Package page: <https://anaconda.org/lescailab/epiresim>
- Distribution: `noarch/epiresim-0.1.0-py_0.tar.bz2`
- Artifact SHA-256:
  `979aaff236e88acfd7b3ccfc60d775ca933d3618839a7c4b78fb578880af5927`
- Source commit: `a1d54b772098edfe4e9fe9f8b67911a1fd4bd17b`
- Source-archive SHA-256:
  `133f0762c29f1dde933aef74029c7081227db82b437c6f233329e0e3bc2cfab7`

## Build environment

- Build platform: macOS Apple Silicon
- Conda: 23.7.4
- conda-build: 3.23.0
- anaconda-client: 1.12.3
- Build host Python selected by conda-build: 3.14.6
- Build channels: conda-forge plus the configured build-tool channels recorded
  in the artifact's `info/about.json`

The final package metadata declares only:

```text
python >=3.11
numpy >=1.26,<3
scipy >=1.12,<2
```

`info/index.json` records both `platform` and `arch` as null and `subdir` as
`noarch`, confirming that the EpiReSIM package itself is platform independent.

## Reproduction commands

Ephemeral machine paths are normalized to `/path/to/...` in accordance with
repository privacy policy; package names, URLs, options, hashes, and versions
are exact.

The source archive was independently downloaded and checksummed before the
recipe was built:

```bash
curl --fail --silent --show-error --location \
  https://github.com/lescailab/EpiReSIM_conversion/archive/a1d54b772098edfe4e9fe9f8b67911a1fd4bd17b.tar.gz \
  --output /path/to/source.tar.gz
shasum -a 256 /path/to/source.tar.gz
```

The release build used a temporary copy identical to the tracked recipe:

```bash
conda-build \
  --croot /path/to/build-root \
  --channel conda-forge \
  /path/to/recipe
```

The recipe tests imported `epiresim`, ran `epiresim --help`, and checked that
the order-two genotype-probability vector sums to one within `1e-12`. The build
and tests completed successfully. The installed conda-build version reported
that optional `conda-verify` was not installed; the recipe tests and independent
remote installation below were therefore used as the release checks.

## Publication and independent installation

The tested artifact was uploaded without a force or overwrite option:

```bash
anaconda upload --label main \
  /path/to/build-root/noarch/epiresim-0.1.0-py_0.tar.bz2
```

A new environment then resolved the package from the public channel rather than
the local build directory:

```bash
conda create --yes \
  --prefix /path/to/verification-env \
  --override-channels \
  --channel https://conda.anaconda.org/lescailab \
  --channel conda-forge \
  --strict-channel-priority \
  python=3.11 \
  epiresim=0.1.0
```

`conda list --show-channel-urls` identified the installed distribution as
`lescailab/noarch::epiresim-0.1.0-py_0`. Verification then confirmed:

- the `epiresim` command and help output;
- installed metadata version `0.1.0`;
- normalized genotype probabilities; and
- a solved order-two compatibility penetrance vector with nine entries.

## Rewrite.bio release checks

- The package description credits the Shang et al. original paper and DOI.
- The documentation URL exposes provenance, validation scope, limitations, and
  implementation-assistance disclosure.
- The source is pinned by immutable commit archive and SHA-256.
- The package contains the original MIT license.
- A pre-upload string scan found no identifiable local checkout path.
- The metadata states that compatibility is limited to the recorded validation
  environment and scenarios; it does not claim universal equivalence.
