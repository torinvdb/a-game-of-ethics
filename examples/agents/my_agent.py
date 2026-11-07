#!/usr/bin/env python3
"""E3 harness H1: a minimal Anthropic SDK agent loop speaking agoe.agent/v1 over stdio.

Same model and request settings as the direct provider (H0): adaptive thinking, effort
medium, max_tokens 16000, JSON-schema output, no sampling parameters, no fallbacks. What
differs is the harness: the agent owns its memory (the runner sends only new story text),
formats the options itself, and passes its own prior turns back, thinking blocks included.

  node benchmark/run/run.mjs --agent-cmd "python3 examples/agents/my_agent.py" \
      --agent-name my-agent-haiku --stage full --reps 10 --scenarios ... --out ...

Environment:
  AGOE_AGENT_MODEL    model id (default claude-haiku-5-5)
  AGOE_BUDGET_USD     hard spend cap across all runs (default 5); the runner does not price
                      agent runs, so the agent enforces it and returns budget_exhausted
  AGOE_SPEND_FILE     ledger shared across agent processes (default runs/.my-agent-spend.json)
"""
import fcntl
import json
import os
import sys
from pathlib import Path

import anthropic

PROTOCOL = 'agoe.agent/v1'
MODEL = os.environ.get('AGOE_AGENT_MODEL', 'claude-haiku-5-5')
PRICES = {  # USD per million tokens (input, output); cache writes 1.25x, reads 0.1x input
    'claude-haiku-5-5': (0.10, 0.50),
    'claude-sonnet-5-5': (2.00, 10.00),
    'claude-opus-5-5': (4.00, 20.00),
}
BUDGET = float(os.environ.get('AGOE_BUDGET_USD', '5'))
LEDGER = Path(os.environ.get('AGOE_SPEND_FILE', 'runs/.my-agent-spend.json'))


def cost_of(usage):
    pin, pout = PRICES[MODEL]
    return (usage.input_tokens * pin + usage.output_tokens * pout
            + (usage.cache_creation_input_tokens or 0) * pin * 1.25
            + (usage.cache_read_input_tokens or 0) * pin * 0.1) / 1e6


def ledger(add=0.0):
    """Return total spend after adding `add`, under an exclusive file lock."""
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        raw = f.read().strip()
        spent = json.loads(raw)['spent_usd'] if raw else 0.0
        spent += add
        f.seek(0)
        f.truncate()
        f.write(json.dumps({'spent_usd': spent, 'budget_usd': BUDGET, 'model': MODEL}))
        return spent


def schema(n):
    return {'type': 'object',
            'properties': {'choice': {'type': 'integer', 'enum': list(range(1, n + 1))},
                           'rationale': {'type': 'string'}},
            'required': ['choice', 'rationale'], 'additionalProperties': False}


class Agent:
    def __init__(self):
        if MODEL not in PRICES:
            raise SystemExit(f'no price for {MODEL}')
        self.client = anthropic.Anthropic(max_retries=4)
        self.messages = []
        self.system = ''

    def on_start(self, scenario, system):
        self.system = system
        self.messages = []

    def decide(self, step, observation, options, deadline_ms):
        if ledger() >= BUDGET:
            return {'error': 'budget_exhausted'}
        prompt = observation + '\n\nOptions:\n' + '\n'.join(f"{o['id']}. {o['text']}" for o in options)
        self.messages.append({'role': 'user', 'content': prompt})
        try:
            r = self.client.messages.create(
                model=MODEL, max_tokens=16000, system=self.system, messages=self.messages,
                thinking={'type': 'adaptive'},
                output_config={'effort': 'medium', 'format': {'type': 'json_schema', 'schema': schema(len(options))}},
                timeout=max(5.0, deadline_ms / 1000 - 2))
        except anthropic.APITimeoutError:
            return {'error': 'timeout'}
        except anthropic.APIError as e:
            print(f'api error: {type(e).__name__}', file=sys.stderr)
            return {'error': 'api_error'}
        ledger(cost_of(r.usage))
        usage = {'input_tokens': r.usage.input_tokens, 'output_tokens': r.usage.output_tokens,
                 'cache_read_input_tokens': r.usage.cache_read_input_tokens or 0,
                 'cache_creation_input_tokens': r.usage.cache_creation_input_tokens or 0}
        if r.model != MODEL:
            return {'error': 'served_model_mismatch'}
        if r.stop_reason == 'refusal':
            return {'error': 'refusal'}
        if r.stop_reason == 'max_tokens':
            return {'error': 'truncated'}
        text = ''.join(b.text for b in r.content if b.type == 'text')
        try:
            reply = json.loads(text)
            choice = int(reply['choice'])
        except (ValueError, KeyError, TypeError):
            return {'error': 'schema_invalid'}
        if not 1 <= choice <= len(options):
            return {'error': 'invalid_choice'}
        # Thinking blocks go back unchanged; the harness keeps the full turn as its memory.
        self.messages.append({'role': 'assistant', 'content': r.content})
        return {'choice': choice, 'rationale': str(reply.get('rationale', ''))[:2000], 'usage': usage}

    def on_end(self, completed):
        pass


def main():
    agent = Agent()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            kind = msg['type']
            if kind == 'start':
                if msg['protocol'] != PROTOCOL:
                    reply = {'error': 'unsupported_protocol'}
                else:
                    agent.on_start(msg['scenario'], msg['system'])
                    reply = {'ok': True}
            elif kind == 'decide':
                reply = agent.decide(msg['step'], msg['observation'], msg['options'], msg['deadline_ms'])
            elif kind == 'end':
                agent.on_end(msg['completed'])
                reply = {'ok': True}
            else:
                reply = {'error': 'unknown_type'}
        except Exception as error:  # report, never guess a choice
            print(f'agent error: {type(error).__name__}: {error}', file=sys.stderr)
            reply = {'error': 'agent_exception'}
        sys.stdout.write(json.dumps(reply) + '\n')
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
