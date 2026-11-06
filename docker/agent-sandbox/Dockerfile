# syntax=docker/dockerfile:1.7
# Example sandbox image for the agent under test: the reference agoe.agent/v1 HTTP agent
# (examples/agents/http_agent.py, stdlib only). Replace the COPY/CMD lines with your agent.
#
#   docker build -f docker/agent-sandbox/Dockerfile -t agoe-agent-sandbox:dev .
#
# Hardening baked into the image (compose adds read-only root, cap_drop ALL, limits):
#   - non-root UID 10001, files root-owned and read-only to it
#   - package manager, shells and setuid/setgid bits removed (no `docker exec ... sh`)
ARG REGISTRY=docker.io/library
ARG PYTHON_IMAGE=python:3.13-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
FROM ${REGISTRY}/${PYTHON_IMAGE}
ARG VERSION=dev
LABEL org.opencontainers.image.title="a-game-of-ethics agent sandbox (reference HTTP agent)" \
      org.opencontainers.image.source="https://github.com/torinvdb/a-game-of-ethics" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="${VERSION}"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
WORKDIR /agent
COPY examples/agents/http_agent.py examples/agents/rule_policy.py /agent/
COPY docker/agent-sandbox/secrets_env.py /usr/local/lib/agoe/secrets_env.py
RUN find / -xdev -type f -perm /6000 -exec chmod a-s {} + \
 && rm -rf /usr/local/lib/python3.13/site-packages/pip* /usr/local/bin/pip* \
 && rm -rf /var/lib/apt /var/lib/dpkg /var/cache/apt /var/cache/debconf \
           /usr/bin/apt* /usr/bin/dpkg* /usr/lib/apt /etc/apt /usr/share/doc /usr/share/man
# Last step: remove the shells (exec form, since /bin/sh is gone afterwards).
RUN ["python3", "-c", "import os\nfor p in ('/usr/bin/sh','/usr/bin/dash','/usr/bin/bash','/usr/bin/rbash'):\n    os.path.lexists(p) and os.remove(p)"]
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=3s --retries=10 \
  CMD ["python3", "-I", "-c", "import socket; socket.create_connection(('127.0.0.1', 8080), 2).close()"]
ENTRYPOINT ["python3", "-I", "/usr/local/lib/agoe/secrets_env.py", "--"]
CMD ["python3", "-I", "/agent/http_agent.py", "--host", "0.0.0.0", "--port", "8080"]
