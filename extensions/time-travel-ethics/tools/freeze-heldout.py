"""Write cases/heldout.FROZEN.json: per-file SHA-256 and a set digest.

Run once when the held-out set is authored, commit the result, and never edit
held-out files afterwards; load_cases('heldout') refuses to run on any change.
A changed held-out case is a new set: freeze it under a new name and say so.
"""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ethicslab.scaffold import digest
p = argparse.ArgumentParser(description=__doc__); p.add_argument('--force', action='store_true'); a = p.parse_args()
target = ROOT / 'cases/heldout.FROZEN.json'
if target.exists() and not a.force:
    p.error('Already frozen; refusing to overwrite (use --force only for a new, announced set)')
files = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT / 'cases/heldout').glob('*.json'))}
target.write_text(json.dumps({'note': 'Frozen before any held-out run. Authored by the same reviewer as the dev cases and scripted policies; held out from policy development only, not independently authored.',
                              'files': files, 'set_sha256': digest(sorted(files.items()))}, indent=2) + '\n')
print('frozen', len(files), 'held-out cases:', digest(sorted(files.items())))
