"""Convert an Inspect log of the agoe task into run.mjs-style ledgers.

    python -m agoe.export logs/<file>.eval --out benchmark/experiments/<exp>/runs/inspect-<name>
    python3 benchmark/run/analyze.py benchmark/experiments/<exp>/runs/inspect-<name>

Writes results.jsonl (one row per completed run), errors.jsonl (one row per
failed run) and run.json, with the field names benchmark/run/analyze.py reads.
Rows are appended; an existing key is skipped so re-exporting is idempotent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from inspect_ai.log import EvalLog, read_eval_log

from .task import STORE_KEY


def _cost(sample: Any) -> float:
    """Sum of ModelUsage.total_cost (set when Inspect has prices, e.g. --model-cost-config); else 0.0."""
    return float(sum((u.total_cost or 0.0) for u in (sample.model_usage or {}).values()))


def _usage(sample: Any) -> dict[str, int]:
    total = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}
    for u in (sample.model_usage or {}).values():
        total["input_tokens"] += u.input_tokens or 0
        total["output_tokens"] += u.output_tokens or 0
        total["cache_read_input_tokens"] += u.input_tokens_cache_read or 0
        total["cache_creation_input_tokens"] += u.input_tokens_cache_write or 0
    return total


def ledger_rows(log: EvalLog) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    model = log.eval.model.split("/", 1)[-1]
    framing = (log.eval.task_args or {}).get("framing", "deployment")
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for s in log.samples or []:
        rec = (s.store or {}).get(STORE_KEY) or {}
        rep = rec.get("rep", s.epoch - 1)
        key = rec.get("key") or f"{model}|{s.id}|{framing}|{rep}"
        base = {"key": key, "model": model, "scenario": s.metadata.get("scenario", s.id), "framing": rec.get("framing", framing), "rep": rep}
        usage = _usage(s)
        if rec.get("status") == "completed":
            results.append(
                {
                    **base,
                    "split": s.metadata.get("split"),
                    "seed": rec.get("seed"),
                    "axes": rec["axes"],
                    "ink_total": rec.get("ink_total"),
                    "ink_average": rec.get("ink_average"),
                    "ink_verdict": rec.get("ink_verdict"),
                    "decisions": rec.get("decisions", []),
                    "usage": usage,
                    "cost_usd": _cost(s),
                    "latency_s": s.total_time,
                    "source": "inspect",
                }
            )
        else:
            fc = rec.get("failure_class")
            if not fc:
                # s.error: Inspect gave up on the sample (API error after its retries, or an exception).
                fc = "sample_error" if s.error else ("limit_exceeded" if rec.get("status") == "running" else "harness_error")
            detail = rec.get("detail") or (s.error.message if s.error else "")
            errors.append(
                {
                    **base,
                    "failure_class": fc,
                    "detail": str(detail)[:300],
                    "at_decision": rec.get("at_decision"),
                    "usage": usage,
                    "cost_usd": _cost(s),
                    "at": log.eval.created,
                    "source": "inspect",
                }
            )
    meta = log.eval.metadata or {}
    scen = {}
    for s in log.samples or []:
        scen[s.metadata.get("scenario", s.id)] = {"id": s.metadata.get("scenario", s.id), "sha256": s.metadata.get("sha256"), "split": s.metadata.get("split")}
    run = {
        "experiment_id": meta.get("experiment_id"),
        "stage": "inspect",
        "provider": f"inspect:{log.eval.model.split('/', 1)[0]}",
        "config_sha256": meta.get("config_sha256"),
        "git_commit": log.eval.revision.commit if log.eval.revision else None,
        "inspect_ai": log.eval.packages.get("inspect_ai") if log.eval.packages else None,
        "manifest_version": meta.get("manifest_version"),
        "scenarios": list(scen.values()),
        "models": [model],
        "reps": log.eval.config.epochs,
        "framing": framing,
        "inspect_log": log.location,
        "started_at": log.eval.created,
        "cost_note": "cost_usd is Inspect's ModelUsage.total_cost; 0.0 when Inspect had no prices for the model.",
    }
    return results, errors, run


def export(log_path: str, out: Path) -> dict[str, int]:
    log = read_eval_log(log_path)
    results, errors, run = ledger_rows(log)
    out.mkdir(parents=True, exist_ok=True)
    counts = {"results": 0, "errors": 0}
    for name, rows in (("results", results), ("errors", errors)):
        f = out / f"{name}.jsonl"
        seen = set()
        if f.exists():
            seen = {json.loads(line)["key"] for line in f.read_text().splitlines() if line.strip()}
        with f.open("a") as fh:
            for r in rows:
                if r["key"] in seen:
                    continue
                fh.write(json.dumps(r) + "\n")
                counts[name] += 1
    (out / "run.json").write_text(json.dumps(run, indent=1) + "\n")
    return counts


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("log", nargs="+", help="Inspect log file(s) (.eval or .json)")
    p.add_argument("--out", required=True, type=Path, help="Run directory to write ledgers into")
    a = p.parse_args(argv)
    for lp in a.log:
        print(json.dumps({"log": lp, **export(lp, a.out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
