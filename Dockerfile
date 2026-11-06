# syntax=docker/dockerfile:1.7
# Harness image: plays the frozen Ink scenarios through benchmark/run/run.mjs.
# Default run is offline (--provider mock) and writes only to /out.
#
#   docker build -t agoe-harness:dev .
#   docker run --rm --read-only --cap-drop ALL --security-opt no-new-privileges \
#     --network none -v "$PWD/out:/out" agoe-harness:dev
#
# Behind a TLS-intercepting proxy, pass its CA as a BuildKit secret (never a build-arg,
# never COPY): it is mounted only for the npm ci step and is not stored in any layer.
#   docker build --secret id=ca,src=/path/ca.pem -t agoe-harness:dev .
#
# Base images are pinned by digest. REGISTRY lets you pull the same digests through a
# mirror (e.g. --build-arg REGISTRY=mirror.gcr.io/library); a digest is content-addressed,
# so a mirror cannot substitute a different image.
ARG REGISTRY=docker.io/library
ARG NODE_IMAGE=node:22-bookworm-slim@sha256:5ec23b7c622b00547753bc6ffd78085dd868a68aeb41c8e0a1418f033e13d96d
ARG PYTHON_IMAGE=python:3.13-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72

FROM ${REGISTRY}/${NODE_IMAGE} AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=secret,id=ca,required=false \
    --mount=type=cache,target=/root/.npm,sharing=locked \
    if [ -f /run/secrets/ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/ca; fi; \
    npm ci --omit=dev --ignore-scripts --no-audit --no-fund \
 && rm -rf node_modules/.package-lock.json \
 # figlet ships ~20 MB of fonts; the CLI banner uses four of them, the runner none.
 && find node_modules/figlet/fonts -type f ! -name 'ANSI Shadow.flf' ! -name 'Small.flf' \
      ! -name 'Future.flf' ! -name 'Standard.flf' -delete \
 && rm -rf node_modules/figlet/importable-fonts \
 && find node_modules -name '*.map' -type f -delete

FROM ${REGISTRY}/${PYTHON_IMAGE} AS runtime
ARG VERSION=dev
ARG REVISION=unknown
LABEL org.opencontainers.image.title="a-game-of-ethics harness" \
      org.opencontainers.image.description="Scenario-based ethics benchmark runner (Ink scenarios, offline mock provider by default)" \
      org.opencontainers.image.source="https://github.com/torinvdb/a-game-of-ethics" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}"
# The node binary needs only glibc, libstdc++ and libgcc_s, which python:3.13-slim-bookworm ships.
# No package-manager step in this stage, so it builds without network access.
COPY --from=deps /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
# .dockerignore is an allowlist: only runtime sources reach the build context.
COPY . /app/
ENV NODE_ENV=production \
    NODE_OPTIONS=--max-old-space-size=384 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    AGOE_OUT=/out
# Files stay root-owned and read-only for the runtime user; /out is the only writable path.
# pip is not needed at runtime. manifest.py runs on the stdlib; analyze.py/stats.py need numpy and
# are meant to run on the host against the results directory.
RUN rm -rf /usr/local/lib/python3.13/site-packages/pip* /usr/local/bin/pip* \
 && mkdir -p /out && chown 10001:10001 /out && chmod 0750 /out \
 && node --version && python3 --version
USER 10001:10001
VOLUME ["/out"]
ENTRYPOINT ["node", "/app/docker/harness/entrypoint.mjs"]
CMD []
