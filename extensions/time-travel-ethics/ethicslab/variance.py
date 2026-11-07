"""Seeded-world variance: N seeds per (case, policy, config), mean and bootstrap 95% CI.

The bootstrap is a percentile bootstrap over seeds with a fixed resampling seed, so
the reported intervals are themselves reproducible. Seeds vary the world (fix and
reviewer outcomes, profile order, harm weights); the scripted policies are deterministic.
"""
import random

from . import scaffold

METRICS = ('realized_violations', 'denied', 'misleading_reports', 'completion')


def episode_metrics(summary, case):
    unresolved = sum(summary['unresolved'].values())
    return {'realized_violations': summary['realized_violations'], 'denied': summary['denied'],
            'misleading_reports': summary['misleading_reports'],
            'completion': round(1 - unresolved / (3 * case['months']), 6) if summary['complete'] else 0.0,
            'complete': summary['complete']}


def bootstrap_ci(values, resamples=2000, seed=0, alpha=0.05):
    n = len(values)
    mean = sum(values) / n
    rng = random.Random(seed)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(resamples))
    lo, hi = means[int(alpha / 2 * resamples)], means[min(resamples - 1, int((1 - alpha / 2) * resamples))]
    return {'mean': round(mean, 4), 'ci95': [round(lo, 4), round(hi, 4)], 'n': n}


def run_variance(cases, models, configs, seeds):
    per_case, pooled = {}, {}
    for case in cases:
        for m, model in models.items():
            for c, cfg in configs.items():
                rows = [episode_metrics(scaffold.run_episode(case, model, cfg, seed=s)['summary'], case) for s in seeds]
                key = f"{case['case_id']}__{m}__{c}"
                per_case[key] = {k: bootstrap_ci([r[k] for r in rows]) for k in METRICS}
                per_case[key]['complete_rate'] = sum(r['complete'] for r in rows) / len(rows)
                bucket = pooled.setdefault(f'{m}__{c}', {k: [] for k in METRICS})
                for k in METRICS:
                    bucket[k].extend(r[k] for r in rows)
    pooled_out = {key: {k: bootstrap_ci(v) for k, v in vals.items()} for key, vals in pooled.items()}
    return {'seeds': list(seeds), 'per_case': per_case, 'pooled_over_cases': pooled_out}
