"""One-command offline cluster calibration; requires npm ci at repository root."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ethicslab.cluster import build
from ethicslab.trajectory import audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--deepeval-python', help='Optional Python with requirements-deepeval.txt installed')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    telemetry = json.loads((ROOT / 'examples/cluster-telemetry.synthetic.json').read_text())
    scenario = json.loads((ROOT / 'examples/cluster-scenario.seed.json').read_text())

    def command(argv, expected=0):
        result = subprocess.run([str(x) for x in argv], cwd=ROOT, capture_output=True,
                                text=True, timeout=120)
        if result.returncode != expected:
            raise RuntimeError(f'{argv[0]} returned {result.returncode}, expected {expected}\n'
                               f'{result.stdout}\n{result.stderr}')

    for swapped in (False, True):
        directory = output / ('swapped' if swapped else 'generated')
        directory.mkdir()
        source, manifest = build(telemetry, scenario, swapped)
        (directory / 'cluster-pressure.ink').write_text(source)
        (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        command(['node', ROOT / 'tools/compile-cluster.mjs', directory / 'cluster-pressure.ink',
                 directory / 'cluster-pressure.ink.json'])
    replays = output / 'replays'
    replays.mkdir()
    comparison = {}
    policies = ['impact-aware', 'delivery', 'exceptions', 'defer-batch', 'label-biased',
                'impact-aware-swapped', 'label-biased-swapped', 'rejected-live-adapter']
    for name in policies:
        swapped = name.endswith('-swapped')
        rejected = name == 'rejected-live-adapter'
        policy = 'live' if rejected else name.removesuffix('-swapped')
        story = output / ('swapped' if swapped else 'generated') / 'cluster-pressure.ink.json'
        extra = ['--model', 'invalid-fixture', '--endpoint', 'http://example.com/v1/chat/completions',
                 '--python', sys.executable] if rejected else []
        run_file = replays / (name + '.json')
        command(['node', ROOT / 'tools/replay-cluster.mjs', '--story', story,
                 '--output', run_file, '--policy', policy, *extra], expected=2 if rejected else 0)
        comparison[name] = audit(json.loads(run_file.read_text()))
        if args.deepeval_python:
            command([args.deepeval_python, '-m', 'ethicslab.deepeval_bridge', run_file,
                     '--output', replays / (name + '.deepeval.json')],
                    expected=1 if rejected or name == 'delivery' else 0)
        print(name + ': ' + json.dumps(comparison[name]), flush=True)
    command([sys.executable, ROOT / 'tools/check-cluster-replays.py', replays])
    (output / 'comparison.json').write_text(json.dumps(comparison, indent=2) + '\n')
    print('Verified scripted calibrations and paired cohort probes. Evidence: ' + str(output))


if __name__ == '__main__':
    main()
