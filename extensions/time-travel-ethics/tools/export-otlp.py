"""Export audited Ink trajectories as OTLP/HTTP JSON and optionally POST them.

python3 tools/export-otlp.py RUN_DIR/replays --output traces.otlp.json [--post URL]

One span per recorded decision. Logical month is an attribute; timestamps are
export time, not execution latency. Only action hashes, the policy flag and
outcome counters are exported, never narrative text. A failed or non-2xx POST
exits non-zero so a Job cannot silently pass without collector receipt.
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ethicslab.trajectory import VIOLATIONS, audit


def value(v):
    if isinstance(v, bool):
        return {'boolValue': v}
    if isinstance(v, int):
        return {'intValue': str(v)}
    return {'stringValue': str(v)}


def spans_for(name, run):
    result = audit(run)
    trace = hashlib.sha256((run['story_sha256'] + name).encode()).hexdigest()[:32]
    now = time.time_ns()
    spans = [{'traceId': trace, 'spanId': hashlib.sha256(f'{name}/run'.encode()).hexdigest()[:16],
              'name': 'ethics.trajectory', 'startTimeUnixNano': str(now), 'endTimeUnixNano': str(now),
              'attributes': [{'key': 'ethics.' + k, 'value': value(v)} for k, v in {
                  'run': name, 'classification': result['classification'], 'complete': result['complete'],
                  'decisions': result['decisions'], 'hard_violations': result['hard_violations'],
                  'evidence_class': run['evidence_class'], 'story_sha256': run['story_sha256'],
                  'timing': 'export-time-not-execution-latency'}.items()]}]
    for r in run['records']:
        attrs = {'ethics.run': name, 'ethics.logical_month': r['state_before']['month'],
                 'ethics.decision_index': r['index'],
                 'ethics.action_sha256': hashlib.sha256(r['selected'].encode()).hexdigest()[:16],
                 'ethics.explicit_violation': r['selected'] in VIOLATIONS}
        spans.append({'traceId': trace, 'spanId': hashlib.sha256(f"{name}/{r['index']}".encode()).hexdigest()[:16],
                      'parentSpanId': spans[0]['spanId'], 'name': 'ethics.decision',
                      'startTimeUnixNano': str(now), 'endTimeUnixNano': str(now),
                      'attributes': [{'key': k, 'value': value(v)} for k, v in attrs.items()]})
    return spans


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('replays', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--post')
    a = p.parse_args()
    spans = []
    for f in sorted(a.replays.glob('*.json')):
        if f.name.endswith('.deepeval.json'):
            continue
        spans += spans_for(f.stem, json.loads(f.read_text()))
    payload = {'resourceSpans': [{'resource': {'attributes': [
        {'key': 'service.name', 'value': {'stringValue': 'time-travel-ethics-ink'}}]},
        'scopeSpans': [{'scope': {'name': 'ethicslab.export-otlp'}, 'spans': spans}]}]}
    body = json.dumps(payload).encode()
    with a.output.open('xb') as stream:
        stream.write(body)
    print(f'{len(spans)} spans written to {a.output}')
    if a.post:
        request = urllib.request.Request(a.post, body, {'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(request, timeout=30) as response:
            if not 200 <= response.status < 300:
                raise SystemExit(f'collector returned {response.status}')
            print('collector accepted', len(spans), 'spans: HTTP', response.status)


if __name__ == '__main__':
    main()
