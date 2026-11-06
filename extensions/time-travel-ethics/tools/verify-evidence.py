"""Compare a run directory with a recorded evidence manifest (SHA-256 per file).

python3 tools/verify-evidence.py RUN_DIR MANIFEST.json [--inputs-root REPO]

MANIFEST may be docs/agentic-ethics/evidence/manifest.json ("outputs" and
optional "inputs" maps) or a Job's evidence-manifest.json ("files" map).
Exit 0 only if every listed file exists and matches. Unlisted files are
reported but do not fail. A matching hash shows the bytes equal the recorded
bytes; it does not authenticate the manifest itself (store it out of band).
"""
import argparse, hashlib, json, sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(run_dir, manifest, inputs_root=None):
    expected = manifest.get('outputs') or manifest.get('files') or {}
    report = {'matched': [], 'mismatched': [], 'missing': [], 'unlisted': [], 'inputs_changed': []}
    for name, digest in sorted(expected.items()):
        path = run_dir / name
        if not path.is_file():
            report['missing'].append(name)
        elif sha(path) != digest:
            report['mismatched'].append(name)
        else:
            report['matched'].append(name)
    listed = set(expected) | {'evidence-manifest.json'}
    report['unlisted'] = sorted(str(p.relative_to(run_dir)) for p in run_dir.rglob('*')
                                if p.is_file() and str(p.relative_to(run_dir)) not in listed)
    if inputs_root is not None:
        for name, digest in sorted(manifest.get('inputs', {}).items()):
            path = inputs_root / name
            if not path.is_file() or sha(path) != digest:
                report['inputs_changed'].append(name)
    report['ok'] = bool(expected) and not (report['mismatched'] or report['missing'])
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run_dir', type=Path)
    p.add_argument('manifest', type=Path)
    p.add_argument('--inputs-root', type=Path)
    a = p.parse_args()
    report = verify(a.run_dir, json.loads(a.manifest.read_text()), a.inputs_root)
    print(json.dumps({k: (v if k in ('ok',) or len(v) < 30 else f'{len(v)} files') for k, v in report.items()}, indent=1))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
