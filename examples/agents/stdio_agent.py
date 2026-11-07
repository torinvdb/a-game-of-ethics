#!/usr/bin/env python3
"""Reference agoe.agent/v1 agent over stdin/stdout (stdlib only).

The harness starts one process per run and writes one JSON message per line; the agent writes
exactly one JSON reply line per message. Logs go to stderr, never stdout.

  node benchmark/run/run.mjs --agent-cmd "python3 examples/agents/stdio_agent.py" --stage smoke \
      --scenarios hostage-holdout --out /tmp/agoe-stdio

--log-messages FILE appends every received message to FILE (JSON lines), for debugging.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rule_policy import RulePolicy  # noqa: E402

PROTOCOL = 'agoe.agent/v1'


def handle(msg, state):
    kind = msg.get('type')
    if kind == 'start':
        if msg.get('protocol') != PROTOCOL:
            return {'error': 'unsupported_protocol'}
        state['run_id'] = msg['run_id']
        state['policy'] = RulePolicy(msg['scenario'])
        return {'ok': True}
    if kind == 'decide':
        if state.get('run_id') != msg.get('run_id'):
            return {'error': 'unknown_run'}
        return state['policy'].decide(msg['step'], msg['options'])
    if kind == 'end':
        print(f"run {msg.get('run_id')} ended, completed={msg.get('completed')}", file=sys.stderr)
        return {'ok': True}
    return {'error': 'unknown_type'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--log-messages')
    a = ap.parse_args()
    state = {}
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if a.log_messages:
            with open(a.log_messages, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
        try:
            msg = json.loads(line)
            reply = handle(msg, state) if isinstance(msg, dict) else {'error': 'bad_message'}
        except (ValueError, KeyError, TypeError):
            reply = {'error': 'bad_message'}
        sys.stdout.write(json.dumps(reply) + '\n')
        sys.stdout.flush()
        if isinstance(msg, dict) and msg.get('type') == 'end':
            break
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
