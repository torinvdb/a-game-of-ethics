#!/usr/bin/env python3
"""Longitudinal arm (E1b): live models on the 36-month Ink cluster scenario.

  npm run ethics:demo -- --output extensions/time-travel-ethics/runs/e1b-stories    # frozen stories + variants
  python3 benchmark/run/cluster.py --stories extensions/time-travel-ethics/runs/e1b-stories \\
      --config benchmark/experiments/e1-anthropic/config.json --out benchmark/experiments/e1-anthropic/runs/e1b-<stage> \\
      [--stage pilot|full] [--models a,b] [--dry-run]

Each replay calls the model once per decision through ethicslab.cluster_agent with
ETHICS_PROVIDER=anthropic. Adapter failures end the trajectory and are reported as
execution failures. Results: <out>/<model>/<variant>/rep-<n>.json and summary.json.
"""
import argparse
import concurrent.futures as cf
import json
import os
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXT = ROOT / 'extensions/time-travel-ethics'
METRICS = ['decision_count', 'hard_violations', 'exposure_windows', 'overdue_exception_windows', 'medical_disruption',
           'education_disruption', 'backlog', 'escalations', 'disclosure_failures']


def story_path(stories, variant):
    d = stories / variant if variant in ('generated', 'swapped') else stories / 'variants' / variant
    return d / 'cluster-pressure.ink.json'


def cost_of(records, price):
    tin = sum((r.get('usage') or {}).get('input_tokens', 0) for r in records)
    tout = sum((r.get('usage') or {}).get('output_tokens', 0) for r in records)
    return (tin * price['in'] + tout * price['out']) / 1e6, tin, tout


def absolute(p):
    # The replay subprocess runs with cwd=EXT, so every path handed to it must be absolute.
    return Path(os.path.abspath(p))


def schedule(jobs, work, cost, budget, workers):
    """Run jobs with at most `workers` in flight and start none once `spent >= budget`.

    Overshoot is bounded by the jobs already in flight when the cap is crossed.
    Returns (results as (job, run, cost) tuples, spent, jobs never started)."""
    pending, inflight, results, spent = list(jobs), {}, [], 0.0
    with cf.ThreadPoolExecutor(max_workers=workers) as pool:
        while pending or inflight:
            while pending and len(inflight) < workers and spent < budget:
                job = pending.pop(0)
                inflight[pool.submit(work, job)] = job
            if not inflight:
                break
            done, _ = cf.wait(inflight, return_when=cf.FIRST_COMPLETED)
            for fut in done:
                job = inflight.pop(fut)
                run = fut.result()
                c = cost(job, run)
                spent += c
                results.append((job, run, c))
    return results, spent, pending


# Wall-clock budget per decision for the replay's bridge process. A fresh Python process is
# spawned per decision; on a loaded or swapping host it can stall well past the replay's 90 s
# default and end a ~150-decision trajectory. API requests have their own shorter timeouts.
DECISION_TIMEOUT_MS = 300000


def replay_command(model, story, out, dry_run):
    return ['node', str(EXT / 'tools/replay-cluster.mjs'), '--story', str(story), '--output', str(out),
            '--policy', 'impact-aware' if dry_run else 'live', '--model', model, '--repo', str(ROOT),
            '--decision-timeout-ms', str(DECISION_TIMEOUT_MS)]


def one(job, dry_run):
    model, variant, rep, story, out = job
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return json.loads(out.read_text())
    env = dict(os.environ, ETHICS_PROVIDER='anthropic')
    cmd = replay_command(model, story, out, dry_run)
    proc = subprocess.run(cmd, cwd=EXT, env=env, check=False, capture_output=True, text=True, timeout=36000)
    if out.exists():
        return json.loads(out.read_text())
    tail = (proc.stderr or proc.stdout or '').strip()[-500:]
    print(f'replay crashed: {model} {variant} rep {rep} (exit {proc.returncode}): {tail}', file=sys.stderr)
    return {'complete': False, 'adapter_failure': {'kind': 'replay_crashed', 'detail': tail}, 'records': []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stories', type=Path, required=True)
    ap.add_argument('--config', type=Path, default=ROOT / 'benchmark/experiments/e1-anthropic/config.json')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--stage', default='pilot')
    ap.add_argument('--models')
    ap.add_argument('--dry-run', action='store_true', help='scripted impact-aware policy instead of live calls (plumbing check)')
    a = ap.parse_args()
    a.stories, a.out = absolute(a.stories), absolute(a.out)
    cfg = json.loads(a.config.read_text())
    e1b = cfg['e1b_cluster']
    models = a.models.split(',') if a.models else [m['id'] for m in cfg['models']]
    prices = {m['id']: m['price_per_mtok'] for m in cfg['models']}
    reps = e1b['stages'][a.stage]['reps']
    budget = e1b['stages'][a.stage]['budget_usd']
    if not a.dry_run and not (os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('ANTHROPIC_AUTH_TOKEN')):
        sys.exit('Set ANTHROPIC_API_KEY before a live run (or pass --dry-run).')
    jobs = [(m, v, r, story_path(a.stories, v), a.out / m / v / f'rep-{r}.json')
            for m in models for v in e1b['variants'] for r in range(reps)]
    for _, v, _, s, _ in jobs:
        if not s.exists():
            sys.exit(f'missing story for variant {v}: {s}')
    done, spent, not_started = schedule(jobs, lambda job: one(job, a.dry_run),
                                        lambda job, run: cost_of(run.get('records', []), prices[job[0]])[0],
                                        budget, e1b.get('concurrency', 3))
    if not_started:
        print(f'budget cap ${budget} reached (${spent:.2f}); {len(not_started)} job(s) not started', file=sys.stderr)
    results = []
    for (m, v, r, _, _), run, c in done:
        _, tin, tout = cost_of(run.get('records', []), prices[m])
        results.append({'model': m, 'variant': v, 'rep': r, 'complete': run.get('complete'),
                        'failure': (run.get('adapter_failure') or {}).get('kind'),
                        'summary': {k: (run.get('summary') or {}).get(k) for k in METRICS},
                        'censoring': run.get('censoring'), 'cost_usd': round(c, 4), 'input_tokens': tin, 'output_tokens': tout})
    agg = {}
    for m in models:
        for v in e1b['variants']:
            rs = [x for x in results if x['model'] == m and x['variant'] == v]
            ok = [x for x in rs if x['complete']]
            agg[f'{m}|{v}'] = {'runs': len(rs), 'complete': len(ok),
                               'failures': sorted({x['failure'] for x in rs if x['failure']}),
                               **{k: {'mean': statistics.mean(x['summary'][k] for x in ok),
                                      'sd': statistics.pstdev(x['summary'][k] for x in ok)} if ok else None for k in METRICS}}
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / 'summary.json').write_text(json.dumps({'stage': a.stage, 'dry_run': a.dry_run, 'spent_usd': round(spent, 4),
                                                    'aggregate': agg, 'runs': results}, indent=1) + '\n')
    print(json.dumps({'runs': len(results), 'spent_usd': round(spent, 4), 'out': str(a.out)}))


if __name__ == '__main__':
    main()
