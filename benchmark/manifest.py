#!/usr/bin/env python3
"""Freeze or verify the benchmark manifest (benchmark/manifest.json).

  python3 benchmark/manifest.py verify          # exit 1 on any drift
  python3 benchmark/manifest.py freeze          # recompute hashes in place
  python3 benchmark/manifest.py freeze --bump 2.1.0

`verify` recomputes the sha256 of every scenario, the protocol and the tooling
listed in the manifest and fails if any file is missing or changed, or if a
.ink file in scenarios/core/ is not listed. `freeze` rewrites the hashes (and
optionally the version); it never changes splits or axis definitions, which
must be edited deliberately and reviewed. Re-freezing a held-out scenario after
results exist invalidates those results for comparison (PROTOCOL.md section 4).
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "benchmark" / "manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked(m: dict):
    for s in m["scenarios"]:
        yield s
    for t in m.get("tooling", []):
        yield t
    if "protocol" in m:
        yield m["protocol"]


def verify(m: dict) -> int:
    bad = 0
    for entry in tracked(m):
        p = ROOT / entry["path"]
        if not p.exists():
            print(f"MISSING  {entry['path']}")
            bad += 1
            continue
        h = sha256(p)
        if h != entry["sha256"]:
            print(f"DRIFT    {entry['path']}\n         manifest {entry['sha256']}\n         actual   {h}")
            bad += 1
        else:
            print(f"ok       {entry['path']}")
    listed = {s["path"] for s in m["scenarios"]}
    for p in sorted((ROOT / "scenarios" / "core").glob("*.ink")):
        rel = p.relative_to(ROOT).as_posix()
        if rel not in listed:
            print(f"UNLISTED {rel} (add it to manifest.json with a split, then freeze)")
            bad += 1
    print(f"\n{'FAIL' if bad else 'PASS'}: manifest {m['version']} ({bad} problem(s))")
    return 1 if bad else 0


def freeze(m: dict, bump: str | None) -> None:
    for entry in tracked(m):
        p = ROOT / entry["path"]
        if not p.exists():
            sys.exit(f"cannot freeze: {entry['path']} is missing")
        entry["sha256"] = sha256(p)
    if bump:
        m["version"] = bump
    m["frozen_at"] = dt.date.today().isoformat()
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(f"froze manifest {m['version']} ({sum(1 for _ in tracked(m))} files)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["verify", "freeze"])
    ap.add_argument("--bump", help="new manifest version when freezing")
    a = ap.parse_args()
    m = json.loads(MANIFEST.read_text())
    if a.command == "verify":
        sys.exit(verify(m))
    freeze(m, a.bump)


if __name__ == "__main__":
    main()
