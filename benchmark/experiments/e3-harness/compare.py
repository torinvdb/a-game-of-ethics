#!/usr/bin/env python3
"""E3: compare harnesses that wrap the same model, at the level of choice distributions per knot.

  python3 benchmark/experiments/e3-harness/compare.py \
      --h0 benchmark/experiments/e1-anthropic/runs/full --h0-model claude-haiku-5-5 \
      --arm H1=benchmark/experiments/e3-harness/runs/h1-haiku \
      --arm H2=benchmark/experiments/e3-harness/runs/h2-haiku \
      --out benchmark/experiments/e3-harness/analysis

A knot is identified by its offered option set, as in benchmark/run/analyze.py. For each
(scenario, framing, knot) seen in both arms, TVD = 0.5 * sum |p_a - p_b| over chosen option text.
Knots are weighted equally. The noise floor compares disjoint random subsamples of H0 drawn at
the other arm's rep count, so it shows how much TVD sampling alone produces at that sample size.
"""
import argparse
import collections
import json
import random
import statistics
from pathlib import Path


def load(path, model=None, scenarios=None):
    rows = [json.loads(l) for l in open(Path(path) / 'results.jsonl')]
    if model:
        rows = [r for r in rows if r['model'] == model]
    if scenarios:
        rows = [r for r in rows if r['scenario'] in scenarios]
    return rows


def fingerprint(rows):
    fp = collections.defaultdict(collections.Counter)
    for r in rows:
        for d in r['decisions']:
            fp[(r['scenario'], r['framing'], tuple(d.get('options') or [d['step']]))][d['option_text']] += 1
    return fp


def tvd(a, b):
    na, nb = sum(a.values()), sum(b.values())
    return 0.5 * sum(abs(a[k] / na - b[k] / nb) for k in set(a) | set(b))


def mean_tvd(fa, fb):
    common = [k for k in fa if k in fb]
    vals = [tvd(fa[k], fb[k]) for k in common]
    return (statistics.mean(vals) if vals else float('nan')), len(common)


def noise_floor(h0, reps, draws=200, seed=7):
    """Mean TVD between two disjoint H0 subsamples of `reps` runs per (scenario, framing)."""
    rng = random.Random(seed)
    cells = collections.defaultdict(list)
    for r in h0:
        cells[(r['scenario'], r['framing'])].append(r)
    out = []
    for _ in range(draws):
        a, b = [], []
        for runs in cells.values():
            pick = rng.sample(runs, min(len(runs), 2 * reps))
            a += pick[:reps]
            b += pick[reps:2 * reps]
        out.append(mean_tvd(fingerprint(a), fingerprint(b))[0])
    out.sort()
    return statistics.mean(out), out[int(0.95 * len(out)) - 1]


def mean_ci(xs):
    m = statistics.mean(xs)
    se = statistics.stdev(xs) / len(xs) ** 0.5 if len(xs) > 1 else float('nan')
    return m, m - 1.96 * se, m + 1.96 * se


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--h0', required=True)
    ap.add_argument('--h0-model', required=True)
    ap.add_argument('--arm', action='append', required=True, help='NAME=run_dir')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    arms = dict(x.split('=', 1) for x in a.arm)
    arm_rows = {n: load(p) for n, p in arms.items()}
    scenarios = {r['scenario'] for rows in arm_rows.values() for r in rows}
    h0 = load(a.h0, a.h0_model, scenarios)
    fp0 = fingerprint(h0)
    report = {'h0': {'dir': a.h0, 'model': a.h0_model, 'runs': len(h0)}, 'scenarios': sorted(scenarios), 'arms': {}}
    md = ['# E3 harness comparison', '', f'Model under every harness: `{a.h0_model}`. Scenarios: {", ".join(sorted(scenarios))}.', '',
          '## Choice distributions per knot (total-variation distance against H0)', '',
          '| arm | runs | knots compared | mean TVD vs H0 | H0 noise floor (mean / 95th pct) |', '| --- | ---: | ---: | ---: | --- |']
    for name, rows in arm_rows.items():
        reps = max(collections.Counter((r['scenario'], r['framing']) for r in rows).values())
        t, k = mean_tvd(fingerprint(rows), fp0)
        nm, n95 = noise_floor(h0, reps)
        report['arms'][name] = {'dir': arms[name], 'runs': len(rows), 'reps_per_cell': reps, 'knots': k,
                                'mean_tvd_vs_h0': t, 'noise_floor_mean': nm, 'noise_floor_p95': n95}
        md.append(f'| {name} | {len(rows)} | {k} | {t:.3f} | {nm:.3f} / {n95:.3f} |')
    names = list(arm_rows)
    for i, x in enumerate(names):
        for y in names[i + 1:]:
            t, k = mean_tvd(fingerprint(arm_rows[x]), fingerprint(arm_rows[y]))
            report.setdefault('pairs', {})[f'{x}-{y}'] = {'mean_tvd': t, 'knots': k}
            md.append(f'| {x} vs {y} | | {k} | {t:.3f} | |')
    md += ['', '## Mean Ink average per cell (95% CI)', '', '| scenario | framing | ' + ' | '.join(['H0'] + names) + ' |',
           '| --- | --- |' + ' ---: |' * (1 + len(names))]
    for sc in sorted(scenarios):
        for fr in ('deployment', 'evaluation'):
            cells = []
            for rows in [h0] + [arm_rows[n] for n in names]:
                xs = [r['ink_average'] for r in rows if r['scenario'] == sc and r['framing'] == fr]
                cells.append('n/a' if not xs else '{:.2f} [{:.2f}, {:.2f}] n={}'.format(*mean_ci(xs), len(xs)))
            md.append(f'| {sc} | {fr} | ' + ' | '.join(cells) + ' |')
    md += ['', 'Arms differ in request details (Inspect sends its own request shape), so they are compared, never pooled.',
           'A mean TVD inside the H0 noise floor is no evidence that the harness changed choices at this sample size.']
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'compare.json').write_text(json.dumps(report, indent=1) + '\n')
    (out / 'compare.md').write_text('\n'.join(md) + '\n')
    print('\n'.join(md))


if __name__ == '__main__':
    main()
