#!/usr/bin/env python3
"""Pre-registered analysis for benchmark/run/run.mjs output (see the experiment DESIGN.md).

  python3 benchmark/run/analyze.py RUN_DIR [--out RUN_DIR/analysis] [--boot 5000]

Writes summary.json and summary.md. Completed runs and failures are reported
separately; failures never enter score means. Requires numpy.
"""
import argparse
import collections
import itertools
import json
import math
from pathlib import Path

import numpy as np

AXES = ['hc', 'fj', 'ar', 'al', 'lt', 'it', 'sp', 'uc']
ROOT = Path(__file__).resolve().parents[2]


def load(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def boot_ci(x, rng, B):
    x = np.asarray(x, float)
    if len(x) < 2:
        return [float('nan'), float('nan')]
    m = rng.choice(x, size=(B, len(x)), replace=True).mean(1)
    return [float(np.quantile(m, .025)), float(np.quantile(m, .975))]


def boot_diff(a, b, rng, B):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = rng.choice(a, (B, len(a))).mean(1) - rng.choice(b, (B, len(b))).mean(1)
    return float(a.mean() - b.mean()), [float(np.quantile(d, .025)), float(np.quantile(d, .975))]


def perm_p(a, b, rng, B):
    """Two-sided permutation test on the difference in means."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = abs(a.mean() - b.mean())
    pool = np.concatenate([a, b])
    n = len(a)
    hits = 0
    for _ in range(B):
        rng.shuffle(pool)
        hits += abs(pool[:n].mean() - pool[n:].mean()) >= obs - 1e-12
    return (hits + 1) / (B + 1)


def holm(pvals):
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def cohens_d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    s = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / max(1, len(a) + len(b) - 2)) if len(a) > 1 and len(b) > 1 else 0
    return float((a.mean() - b.mean()) / s) if s else 0.0


def chi2_uniform(counts):
    """Pearson chi-square vs uniform; returns (stat, df, p) using the Wilson-Hilferty approximation."""
    counts = np.asarray(counts, float)
    k, n = len(counts), counts.sum()
    if k < 2 or n == 0:
        return 0.0, 0, 1.0
    e = n / k
    stat = float(((counts - e) ** 2 / e).sum())
    df = k - 1
    z = ((stat / df) ** (1 / 3) - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    return stat, df, float(0.5 * math.erfc(z / math.sqrt(2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dir', type=Path)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--boot', type=int, default=5000)
    a = ap.parse_args()
    out = a.out or a.run_dir / 'analysis'
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261106)
    rows = load(a.run_dir / 'results.jsonl')
    errs = load(a.run_dir / 'errors.jsonl')
    manifest = json.loads((ROOT / 'benchmark/manifest.json').read_text())
    chance = {s['id']: s.get('uniform_random_expected_average') for s in manifest['scenarios']}
    for r in rows:
        r['avg'] = sum(r['axes'][x] for x in AXES) / 8.0

    S = {'n_completed': len(rows), 'n_failed_attempts': len(errs)}
    # 1. Execution ledger: failures by class, per model
    fail = collections.defaultdict(collections.Counter)
    for e in errs:
        fail[e['model']][e['failure_class']] += 1
    attempted = collections.Counter(r['model'] for r in rows)
    for e in errs:
        attempted[e['model']] += 1
    S['execution'] = {m: {'attempts': attempted[m], 'completed': sum(1 for r in rows if r['model'] == m), 'failures': dict(fail[m])}
                      for m in sorted(attempted)}
    # 2. Per model x scenario x framing: mean axis average with bootstrap CI, verdict mix, chance gap
    cells = collections.defaultdict(list)
    for r in rows:
        cells[(r['model'], r['scenario'], r['framing'])].append(r)
    S['cells'] = []
    for (m, sc, fr), rs in sorted(cells.items()):
        x = [r['avg'] for r in rs]
        S['cells'].append({'model': m, 'scenario': sc, 'framing': fr, 'n': len(x), 'mean_avg': float(np.mean(x)),
                           'ci95': boot_ci(x, rng, a.boot), 'chance': chance.get(sc),
                           'verdicts': dict(collections.Counter(r['ink_verdict'] for r in rs)),
                           'cost_usd': float(sum(r['cost_usd'] for r in rs))})
    # 3. Choice fingerprint and consistency: modal-option share at each (scenario, step, option set)
    fp = collections.defaultdict(collections.Counter)
    for r in rows:
        for d in r['decisions']:
            knot = tuple(d.get('options') or [d['step']])  # the offered option set identifies the knot
            fp[(r['model'], r['scenario'], r['framing'], knot)][d['option_text']] += 1
    cons = collections.defaultdict(list)
    for (m, sc, fr, knot), c in fp.items():
        tot = sum(c.values())
        if tot >= 5:
            cons[m].append(max(c.values()) / tot)
    S['consistency_modal_share'] = {m: {'mean': float(np.mean(v)), 'n_knots': len(v)} for m, v in cons.items()}
    # 4. Position bias: presented position of the chosen option vs uniform (per model, per option count)
    pos = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for r in rows:
        for d in r['decisions']:
            pos[r['model']][d['n_options']][d['presented_index']] += 1
    S['position_bias'] = {}
    for m, by_k in pos.items():
        S['position_bias'][m] = {}
        for k, c in sorted(by_k.items()):
            counts = [c[i] for i in range(k)]
            stat, df, p = chi2_uniform(counts)
            S['position_bias'][m][str(k)] = {'counts': counts, 'chi2': stat, 'df': df, 'p': p}
    # 5. Framing effect (evaluation - deployment) per model x scenario, Holm-corrected
    tests = []
    for m in sorted({r['model'] for r in rows}):
        for sc in sorted({r['scenario'] for r in rows}):
            ev = [r['avg'] for r in cells.get((m, sc, 'evaluation'), [])]
            de = [r['avg'] for r in cells.get((m, sc, 'deployment'), [])]
            if len(ev) >= 2 and len(de) >= 2:
                diff, ci = boot_diff(ev, de, rng, a.boot)
                tests.append({'model': m, 'scenario': sc, 'diff_eval_minus_deploy': diff, 'ci95': ci,
                              'd': cohens_d(ev, de), 'p': perm_p(ev, de, rng, min(a.boot, 2000))})
    for t, q in zip(tests, holm([t['p'] for t in tests])):
        t['p_holm'] = q
    S['framing_effect'] = tests
    # 5b. Choice-level framing effect: total-variation distance between framings at each knot
    tvd = collections.defaultdict(list)
    keys = {(m, sc, knot) for (m, sc, fr, knot) in fp}
    for m, sc, knot in keys:
        ev, de = fp.get((m, sc, 'evaluation', knot)), fp.get((m, sc, 'deployment', knot))
        if ev and de and sum(ev.values()) >= 5 and sum(de.values()) >= 5:
            ne, nd = sum(ev.values()), sum(de.values())
            tvd[m].append(0.5 * sum(abs(ev[o] / ne - de[o] / nd) for o in set(ev) | set(de)))
    S['framing_choice_tvd'] = {m: {'mean': float(np.mean(v)), 'max': float(np.max(v)), 'n_knots': len(v)} for m, v in tvd.items()}
    # 6. Pairwise model differences on held-out scenarios (primary endpoint), pooled over framings
    held = [r for r in rows if r.get('split') == 'held_out']
    pw = []
    for m1, m2 in itertools.combinations(sorted({r['model'] for r in rows}), 2):
        a1 = [r['avg'] for r in held if r['model'] == m1]
        a2 = [r['avg'] for r in held if r['model'] == m2]
        if len(a1) >= 2 and len(a2) >= 2:
            diff, ci = boot_diff(a1, a2, rng, a.boot)
            pw.append({'a': m1, 'b': m2, 'diff': diff, 'ci95': ci, 'd': cohens_d(a1, a2), 'p': perm_p(a1, a2, rng, min(a.boot, 2000))})
    for t, q in zip(pw, holm([t['p'] for t in pw])):
        t['p_holm'] = q
    S['primary_heldout_pairwise'] = pw
    S['cost_usd_total'] = float(sum(r['cost_usd'] for r in rows) + sum(e.get('cost_usd', 0) for e in errs))
    (out / 'summary.json').write_text(json.dumps(S, indent=1) + '\n')

    md = ['# Analysis summary', '', f"Completed runs: {S['n_completed']} · failed attempts: {S['n_failed_attempts']} · spend: ${S['cost_usd_total']:.2f}", '',
          'Axis scores are author-assigned deltas (inter-rater review pending); read them with the choice fingerprints.', '',
          '## Execution ledger', '', '| model | attempts | completed | failures |', '| --- | ---: | ---: | --- |']
    for m, v in S['execution'].items():
        md.append(f"| {m} | {v['attempts']} | {v['completed']} | {', '.join(f'{k}: {n}' for k, n in v['failures'].items()) or '-'} |")
    md += ['', '## Primary endpoint: held-out scenarios, pairwise mean-average difference', '', '| a | b | diff | 95% CI | d | p (Holm) |', '| --- | --- | ---: | --- | ---: | ---: |']
    for t in pw:
        md.append(f"| {t['a']} | {t['b']} | {t['diff']:+.3f} | [{t['ci95'][0]:+.3f}, {t['ci95'][1]:+.3f}] | {t['d']:+.2f} | {t['p_holm']:.3g} |")
    md += ['', '## Framing effect (evaluation minus deployment), Holm-corrected', '', '| model | scenario | diff | 95% CI | p (Holm) |', '| --- | --- | ---: | --- | ---: |']
    for t in tests:
        md.append(f"| {t['model']} | {t['scenario']} | {t['diff_eval_minus_deploy']:+.3f} | [{t['ci95'][0]:+.3f}, {t['ci95'][1]:+.3f}] | {t['p_holm']:.3g} |")
    md += ['', '## Framing effect at the choice level (total-variation distance per knot)', '', '| model | mean TVD | max TVD | knots |', '| --- | ---: | ---: | ---: |']
    for m, v in S['framing_choice_tvd'].items():
        md.append(f"| {m} | {v['mean']:.3f} | {v['max']:.3f} | {v['n_knots']} |")
    md += ['', '## Position bias (chosen presented position vs uniform)', '', '| model | options | counts | p |', '| --- | ---: | --- | ---: |']
    for m, by in S['position_bias'].items():
        for k, v in by.items():
            md.append(f"| {m} | {k} | {v['counts']} | {v['p']:.3g} |")
    md += ['', '## Cells', '', '| model | scenario | framing | n | mean avg | 95% CI | chance |', '| --- | --- | --- | ---: | ---: | --- | ---: |']
    for c in S['cells']:
        ch = '' if c['chance'] is None else f"{c['chance']:.3f}"
        md.append(f"| {c['model']} | {c['scenario']} | {c['framing']} | {c['n']} | {c['mean_avg']:.3f} | [{c['ci95'][0]:.3f}, {c['ci95'][1]:.3f}] | {ch} |")
    (out / 'summary.md').write_text('\n'.join(md) + '\n')
    print(f"wrote {out / 'summary.md'}")


if __name__ == '__main__':
    main()
