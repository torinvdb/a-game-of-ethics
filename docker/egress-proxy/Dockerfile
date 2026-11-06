# syntax=docker/dockerfile:1.7
# Allowlisting CONNECT proxy (docker/egress-proxy/proxy.py, stdlib only). The only container
# attached to both the internal sandbox network and an egress network.
ARG REGISTRY=docker.io/library
ARG PYTHON_IMAGE=python:3.13-slim-bookworm@sha256:a5a7017efc5969e00ae2b91c8eb0631049a569652aa4ffc4501769049ae45c72
FROM ${REGISTRY}/${PYTHON_IMAGE}
LABEL org.opencontainers.image.title="a-game-of-ethics egress allowlist proxy" \
      org.opencontainers.image.source="https://github.com/torinvdb/a-game-of-ethics" \
      org.opencontainers.image.licenses="MIT"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY docker/egress-proxy/proxy.py /usr/local/lib/agoe/proxy.py
RUN find / -xdev -type f -perm /6000 -exec chmod a-s {} + \
 && rm -rf /usr/local/lib/python3.13/site-packages/pip* /usr/local/bin/pip* \
 && rm -rf /var/lib/apt /var/lib/dpkg /var/cache/apt /usr/bin/apt* /usr/bin/dpkg* /usr/lib/apt /etc/apt /usr/share/doc /usr/share/man
RUN ["python3", "-c", "import os\nfor p in ('/usr/bin/sh','/usr/bin/dash','/usr/bin/bash','/usr/bin/rbash'):\n    os.path.lexists(p) and os.remove(p)"]
USER 10001:10001
EXPOSE 3128
ENTRYPOINT ["python3", "-I", "/usr/local/lib/agoe/proxy.py"]
