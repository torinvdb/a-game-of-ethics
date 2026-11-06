# Ink cluster-scenario evaluation image (Node + inkjs compiler/runtime + Python stdlib harness).
# Build from the extension root:  docker build -f deploy/Dockerfile -t ethics-lab:0.2.0 .
# Repository layout is preserved under /app so tools resolve inkjs from /app/node_modules.
# Pin both images by digest for published builds; tags here are examples.
ARG NODE_IMAGE=node:22-slim
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${NODE_IMAGE} AS deps
WORKDIR /app
COPY deploy/runtime/package.json deploy/runtime/package-lock.json ./
# Optional build secret "ca" supplies a corporate/proxy CA bundle; omitted secrets are ignored.
RUN --mount=type=secret,id=ca,required=false \
    if [ -f /run/secrets/ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/ca; fi; \
    npm ci --omit=dev --ignore-scripts --no-audit --no-fund

FROM ${PYTHON_IMAGE}
# The node binary needs only glibc, libstdc++ and libgcc_s, which the Python slim image ships.
# No package-manager step: the runtime stage needs no network access to build.
COPY --from=deps /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY --from=deps /app/node_modules /app/node_modules
COPY deploy/runtime/package.json /app/package.json
COPY ethicslab /app/extensions/time-travel-ethics/ethicslab
COPY tools /app/extensions/time-travel-ethics/tools
COPY scenarios /app/extensions/time-travel-ethics/scenarios
COPY examples /app/extensions/time-travel-ethics/examples
COPY cases /app/extensions/time-travel-ethics/cases
COPY deploy/run-ink-job.sh /app/extensions/time-travel-ethics/deploy/run-ink-job.sh
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 NODE_OPTIONS=--max-old-space-size=192
WORKDIR /app/extensions/time-travel-ethics
USER 10001:10001
RUN node --version && python3 --version
ENTRYPOINT ["/bin/sh"]
CMD ["deploy/run-ink-job.sh"]
