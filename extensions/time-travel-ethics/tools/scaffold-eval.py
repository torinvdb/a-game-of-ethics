"""Run scripted policies through the offline agent scaffold, guarded vs unguarded.

Usage: python3 tools/scaffold-eval.py --split dev|heldout|all --output runs/scaffold-001
Writes one session bundle per (case, model, config), results.json and a
manifest of SHA-256 digests. No network, cluster or model inference is used.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ethicslab.scaffold import CONFIGS, fairness_probe, load_cases, run_episode, verify_session, digest
from ethicslab.scripted_models import MODELS

KEYS = ('realized_violations', 'attempted_violations', 'denied', 'execution_failures')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--split', choices=['dev', 'heldout', 'all'], default='all')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    splits = ['dev', 'heldout'] if a.split == 'all' else [a.split]
    results, table = {}, {}
    for split in splits:
        for case in load_cases(split):
            for model_name, model in MODELS.items():
                for config_name, config in CONFIGS.items():
                    session = run_episode(case, model, config, model_id='scripted:' + model_name)
                    assert verify_session(session)
                    name = f"{case['case_id']}__{model_name}__{config_name}"
                    (a.output / (name + '.json')).write_text(json.dumps(session, indent=1, sort_keys=True))
                    s = session['summary']
                    results[name] = {'split': split, 'case': case['case_id'], 'model': model_name,
                                     'config': config_name, 'ledger_head': session['ledger'][-1]['hash'],
                                     'disruption_env_reported': session['cluster']['disruption'],
                                     'release_backlog_env_reported': session['cluster']['release_backlog'],
                                     'batch_backlog_env_reported': session['cluster']['batch_backlog'], **s}
                    row = table.setdefault((split, model_name, config_name),
                                           dict.fromkeys(KEYS, 0) | {'cases': 0, 'complete': 0, 'releases_shipped_authorized': 0})
                    row['cases'] += 1
                    row['complete'] += s['complete']
                    row['releases_shipped_authorized'] += s['useful_work'].get('release_shipped', 0)
                    for svc, units in session['cluster']['disruption'].items():
                        row[svc + '_disruption'] = row.get(svc + '_disruption', 0) + units
                    for k in KEYS:
                        row[k] += s[k]
    fairness = {}
    for split in splits:
        for case in load_cases(split):
            if case['capacity_deficit'] > 0:
                for model_name in ('careful', 'label-biased'):
                    fairness[f"{case['case_id']}__{model_name}"] = fairness_probe(case, MODELS[model_name], CONFIGS['guarded'])
    summary = [{'split': s, 'model': m, 'config': c, **row} for (s, m, c), row in sorted(table.items())]
    out = {'evidence_class': 'scripted-calibration (offline scaffold, mocked tools)',
           'heldout_frozen_sha256': json.loads((ROOT / 'cases/heldout.FROZEN.json').read_text())['set_sha256'],
           'summary': summary, 'fairness_probes': fairness, 'runs': results}
    (a.output / 'results.json').write_text(json.dumps(out, indent=1, sort_keys=True) + '\n')
    files = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(a.output.glob('*.json'))}
    (a.output / 'manifest.json').write_text(json.dumps({'files': files, 'set_sha256': digest(sorted(files.items()))}, indent=1) + '\n')
    width = max(len(r['model']) for r in summary)
    print(f"{'split':8} {'model':{width}} {'config':10} cases complete realized attempted denied exec_fail shipped")
    for r in summary:
        print(f"{r['split']:8} {r['model']:{width}} {r['config']:10} {r['cases']:5} {r['complete']:8} "
              f"{r['realized_violations']:8} {r['attempted_violations']:9} {r['denied']:6} {r['execution_failures']:9} "
              f"{r['releases_shipped_authorized']:7}")
    for k, v in fairness.items():
        print('fairness', k, v['label_flips'], '/', v['cuts'])


if __name__ == '__main__':
    main()
