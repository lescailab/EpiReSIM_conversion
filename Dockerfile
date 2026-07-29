# syntax=docker/dockerfile:1.7

ARG MICROMAMBA_IMAGE=mambaorg/micromamba:2.1.1@sha256:41cd3a282e3156c6426c7fa2bff96e8d038ca5c7ab3a183dbad446254f351821

FROM ${MICROMAMBA_IMAGE} AS builder

COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/environment.yml
RUN micromamba create --yes --name build --file /tmp/environment.yml \
    && micromamba clean --all --yes

COPY --chown=$MAMBA_USER:$MAMBA_USER . /tmp/source
WORKDIR /tmp/source
RUN micromamba run --name build python -m build --no-isolation --wheel --outdir /tmp/wheels

FROM ${MICROMAMBA_IMAGE} AS runtime

LABEL org.opencontainers.image.title="EpiReSIM" \
      org.opencontainers.image.description="Python rewrite of the EpiReSIM epistasis simulator" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.source="https://github.com/lescailab/EpiReSIM_conversion"

COPY --chown=$MAMBA_USER:$MAMBA_USER conda/runtime.yml /tmp/runtime.yml
RUN micromamba install --yes --name base --file /tmp/runtime.yml \
    && micromamba clean --all --yes

COPY --from=builder --chown=$MAMBA_USER:$MAMBA_USER /tmp/wheels/*.whl /tmp/wheels/
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN python -m pip install --no-deps /tmp/wheels/*.whl \
    && rm -rf /tmp/wheels

USER $MAMBA_USER
WORKDIR /work
ENTRYPOINT ["/opt/conda/bin/epiresim"]
CMD ["--help"]
