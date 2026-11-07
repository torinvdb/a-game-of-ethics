#!/usr/bin/env python3
"""Stage-friendly replay of recorded Ink cluster trajectories.

Reads the evidence directory written by `npm run ethics:demo -- --output DIR`
and plays one trajectory month by month in a retro terminal view, then prints the
cross-policy comparison. Read-only: it never changes the evidence files.

  python3 talks/three-years-in-thirty-minutes/demo/replay.py DIR --policy delivery --months 1-3
  python3 .../replay.py DIR --policy exceptions --find expiry      # jump to the first expiry review
  python3 .../replay.py DIR --compare                              # comparison table only

Keys in interactive mode: Enter = next decision, m = next month, q = finish.
--auto plays without input (use --delay to pace it). NO_COLOR is honoured.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import textwrap
import time
from pathlib import Path

COLOR = sys.stdout.isatty() and not os.environ.get('NO_COLOR')


def c(code, s):
    return f'\x1b[{code}m{s}\x1b[0m' if COLOR else s


GREEN, AMBER, RED, CYAN, MAG, DIM, BOLD = '38;5;120', '38;5;215', '38;5;203', '38;5;123', '38;5;205', '38;5;244', '1'
WATCH = [('hard_violations', 'violations', RED), ('exposure_windows', 'exposure windows', RED),
         ('overdue_exception_windows', 'expiry reviews', AMBER), ('medical_disruption', 'medical disruption', AMBER),
         ('education_disruption', 'education disruption', AMBER), ('backlog', 'release backlog', CYAN),
         ('temporary_capacity_credits', 'capacity credits', CYAN), ('escalations', 'escalations', GREEN)]


def width():
    return min(100, shutil.get_terminal_size((100, 30)).columns)


def rule(ch='─', col=DIM):
    print(c(col, ch * width()))


def banner(title, sub):
    w = width()
    print(c(GREEN, '┌' + '─' * (w - 2) + '┐'))
    print(c(GREEN, '│') + c(BOLD, f' {title}'.ljust(w - 2)) + c(GREEN, '│'))
    print(c(GREEN, '│') + c(DIM, f' {sub}'.ljust(w - 2)) + c(GREEN, '│'))
    print(c(GREEN, '└' + '─' * (w - 2) + '┘'))


def month_banner(m, horizon):
    bar_w = width() - 22
    done = int(bar_w * m / horizon)
    print()
    print(c(AMBER, f' MONTH {m:02d} / {horizon} ') + c(GREEN, '█' * done) + c(DIM, '░' * (bar_w - done)))


def show(rec, nxt, idx):
    obs = rec.get('observation', '').strip().splitlines()
    head = [ln for ln in obs if ln.strip()][:3]
    for ln in head:
        for part in textwrap.wrap(ln, width() - 4):
            print(c(DIM, '  │ ') + part)
    sel = rec.get('selected')
    for ch in rec.get('choices', []):
        mark = c(MAG, '  ▶ ') if ch['text'] == sel else '    '
        text = c(BOLD, ch['text']) if ch['text'] == sel else c(DIM, ch['text'])
        print(f'{mark}[{ch["index"]}] {text}')
    before = rec.get('state_before', {})
    after = (nxt or {}).get('state_before') if nxt else None
    if after:
        deltas = []
        for key, label, col in WATCH:
            d = after.get(key, 0) - before.get(key, 0)
            if d:
                deltas.append(c(col, f'{label} {d:+d}'))
        if before.get('controls_enabled') and not after.get('controls_enabled'):
            deltas.insert(0, c(RED, 'SIGNATURE CONTROL DISABLED'))
        if not before.get('controls_enabled') and after.get('controls_enabled'):
            deltas.insert(0, c(GREEN, 'signature control restored'))
        if not before.get('waiver_active') and after.get('waiver_active'):
            deltas.insert(0, c(AMBER, f'scoped exception granted, expires month {after.get("waiver_expires")}'))
        if deltas:
            print('      ' + c(DIM, '→ ') + '   '.join(deltas))


def parse_months(spec, horizon):
    if not spec:
        return 1, horizon
    a, _, b = spec.partition('-')
    return int(a), int(b or a)


def compare(root: Path):
    data = json.loads((root / 'comparison.json').read_text())
    rows = data.get('policies', data) if isinstance(data, dict) else data
    if isinstance(rows, dict):
        rows = [dict(policy=k, **v) for k, v in rows.items() if isinstance(v, dict)]
    banner('COMPARISON  ·  same incident, different policies',
           'scripted calibration controls · illustrative authored impact units · not model results')
    hdr = f"{'POLICY':<26}{'CHOICES':>8}{'VIOL.':>7}{'MED/EDU':>10}{'BACKLOG':>9}{'EXPIRY':>8}"
    print(c(DIM, hdr))
    for r in rows:
        s = r.get('summary', r)
        if not isinstance(s, dict) or 'decisions' not in s and 'decision_count' not in s:
            continue
        name = r.get('policy') or r.get('name', '?')
        viol = s.get('hard_violations', 0)
        line = (f"{name:<26}{s.get('decisions', s.get('decision_count', 0)):>8}{viol:>7}"
                f"{str(s.get('medical_disruption', 0)) + '/' + str(s.get('education_disruption', 0)):>10}"
                f"{s.get('backlog', 0):>9}{s.get('overdue_exception_windows', 0):>8}")
        print(c(RED, line) if viol else line)
    rule()
    print(c(DIM, ' Zero disruption can hide a backlog. Zero violations can still be unequal: see the swapped pairs.'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('evidence', type=Path, help='directory written by npm run ethics:demo -- --output DIR')
    ap.add_argument('--policy', default='delivery')
    ap.add_argument('--months', help='e.g. 1-3')
    ap.add_argument('--find', choices=['expiry', 'bypass', 'exception'], help='start at the first matching decision')
    ap.add_argument('--auto', action='store_true')
    ap.add_argument('--delay', type=float, default=0.9)
    ap.add_argument('--compare', action='store_true', help='only print the comparison table')
    a = ap.parse_args()
    if a.compare:
        compare(a.evidence)
        return 0
    path = a.evidence / 'replays' / f'{a.policy}.json'
    if not path.exists():
        options = sorted(p.stem for p in (a.evidence / 'replays').glob('*.json'))
        print(f'no replay for policy {a.policy!r}; available: {", ".join(options)}', file=sys.stderr)
        return 2
    run = json.loads(path.read_text())
    recs = run.get('records', [])
    horizon = run.get('summary', {}).get('horizon', 36)
    lo, hi = parse_months(a.months, horizon)
    banner(f'ETHICS LAB / REPLAY  ·  policy: {a.policy}',
           f"{run.get('evidence_class', '?')} · runtime {run.get('runtime', '?')} · story sha256 "
           f"{run.get('story_sha256', '')[:12]}…")
    if run.get('adapter_failure'):
        print(c(RED, f"  ADAPTER FAILURE (logged, not scored): {run['adapter_failure']}"))
    start = 0
    if a.find:
        key = {'expiry': 'overdue_exception_windows', 'bypass': 'exposure_windows', 'exception': 'waiver_active'}[a.find]
        for i in range(len(recs) - 1):
            if recs[i + 1]['state_before'].get(key, 0) > recs[i]['state_before'].get(key, 0):
                start = max(0, i - 1)
                lo = recs[start]['state_before']['month']
                hi = max(hi, lo) if a.months else lo + 1
                break
    month = None
    skip_month = None
    for i in range(start, len(recs)):
        rec = recs[i]
        m = rec['state_before'].get('month', 0)
        if m < lo:
            continue
        if m > hi:
            break
        if m != month:
            month = m
            month_banner(m, horizon)
        if skip_month == m:
            continue
        show(rec, recs[i + 1] if i + 1 < len(recs) else None, i)
        if a.auto:
            time.sleep(a.delay)
        elif sys.stdin.isatty():
            k = input(c(DIM, '      [enter] next · m next month · q finish ')).strip().lower()
            if k == 'q':
                break
            if k == 'm':
                skip_month = m
    s = run.get('summary', {})
    print()
    rule('═', GREEN)
    print('  ' + '   '.join(c(col, f'{label}: {s.get(key, 0)}') for key, label, col in WATCH[:6]))
    print(c(DIM, '  ' + run.get('limitations', 'Scripted calibration policy; not model evidence.')
            if isinstance(run.get('limitations'), str) else '  Scripted calibration policy; not model evidence.'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
