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


def one(job, dry_run):
    model, variant, rep, story, out = job
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return json.loads(out.read_text())
    env = dict(os.environ, ETHICS_PROVIDER='anthropic')
    cmd = ['node', str(EXT / 'tools/replay-cluster.mjs'), '--story', str(story), '--output', str(out),
           '--policy', 'impact-aware' if dry_run else 'live', '--model', model, '--repo', str(ROOT)]
    subprocess.run(cmd, cwd=EXT, env=env, check=False, capture_output=True, text=True, timeout=7200)
    return json.loads(out.read_text()) if out.exists() else {'complete': False, 'adapter_failure': {'kind': 'replay_crashed'}, 'records': []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stories', type=Path, required=True)
    ap.add_argument('--config', type=Path, default=ROOT / 'benchmark/experiments/e1-anthropic/config.json')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--stage', default='pilot')
    ap.add_argument('--models')
    ap.add_argument('--dry-run', action='store_true', help='scripted impact-aware policy instead of live calls (plumbing check)')
    a = ap.parse_args()
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
    spent, results = 0.0, []
    with cf.ThreadPoolExecutor(max_workers=e1b.get('concurrency', 3)) as pool:
        futures = {}
        for job in jobs:
            if spent > budget:
                break
            futures[pool.submit(one, job, a.dry_run)] = job
        for fut in cf.as_completed(futures):
            m, v, r, _, _ = futures[fut]
            run = fut.result()
            c, tin, tout = cost_of(run.get('records', []), prices[m])
            spent += c
            results.append({'model': m, 'variant': v, 'rep': r, 'complete': run.get('complete'),
                            'failure': (run.get('adapter_failure') or {}).get('kind'),
                            'summary': {k: (run.get('summary') or {}).get(k) for k in METRICS},
                            'censoring': run.get('censoring'), 'cost_usd': round(c, 4), 'input_tokens': tin, 'output_tokens': tout})
            if spent > budget:
                print(f'budget cap ${budget} reached (${spent:.2f}); remaining jobs not started', file=sys.stderr)
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
