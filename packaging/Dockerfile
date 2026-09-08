# syntax=docker/dockerfile:1

FROM python:3.12-bookworm AS builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc patchelf ccache && \
    rm -rf /var/lib/apt/lists/*

ENV CC='ccache gcc' \
    CXX='ccache g++' \
    PATH='/usr/lib/ccache:/usr/local/bin:/usr/bin:/bin'

WORKDIR /src

COPY pyproject.toml README.md ./
COPY telorax ./telorax

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install nuitka ordered-set zstandard && \
    pip install .

ARG NUITKA_JOBS=4
RUN --mount=type=cache,target=/root/.cache/Nuitka \
    --mount=type=cache,target=/root/.cache/ccache \
    mkdir -p /out && \
    python -m nuitka \
      --standalone \
      --onefile \
      --jobs=${NUITKA_JOBS} \
      --output-dir=/out \
      --output-filename=telorax \
      --include-package=telorax \
      telorax/cli/app.py && \
    chmod +x /out/telorax

FROM scratch AS export
COPY --from=builder /out/telorax /telorax
