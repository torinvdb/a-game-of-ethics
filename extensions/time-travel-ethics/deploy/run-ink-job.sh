#!/bin/sh
# Container entry for the Ink cluster-scenario Job. Fails on any step, including collector receipt.
set -eu
OUT="/evidence/${RUN_ID:?RUN_ID must name a new evidence directory}"
python3 tools/demo.py --output "$OUT"
python3 -I -c 'import sys; sys.path.insert(0, "."); import hashlib, json, pathlib
out = pathlib.Path(sys.argv[1])
files = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob("*")) if p.is_file()}
(out / "evidence-manifest.json").write_text(json.dumps({"run_id": out.name, "files": files}, indent=1, sort_keys=True))
print("evidence manifest:", len(files), "files")' "$OUT"
python3 tools/export-otlp.py "$OUT/replays" --output "$OUT/traces.otlp.json" --post "${OTLP_ENDPOINT:-http://otel-collector:4318/v1/traces}"
# Negative control: the NetworkPolicy must stop egress to anything except the collector and DNS.
if python3 -c 'import socket,sys; socket.create_connection((sys.argv[1], 443), timeout=5)' "${EGRESS_PROBE_HOST:-example.com}" 2>/dev/null; then
  echo "EGRESS PROBE SUCCEEDED: network isolation is not enforced" >&2; exit 3
fi
echo "egress probe blocked as expected"
