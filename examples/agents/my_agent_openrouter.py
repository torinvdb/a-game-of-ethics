#!/usr/bin/env python3
"""E3 harness H1 for OpenAI-compatible endpoints (OpenRouter :free models), agoe.agent/v1 over stdio.

Same request settings as the E2 direct provider (H0): temperature 1.0, max_tokens 4000, JSON
requested in the prompt (not enforced), no other sampling parameters. What differs is the harness:
the agent keeps its own transcript (the runner sends only new story text) and formats the options.

  AGOE_AGENT_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free \
  node benchmark/run/run.mjs --agent-cmd "python3 examples/agents/my_agent_openrouter.py" ...

Only ':free' model ids are accepted, so this agent cannot spend credits.
Environment: OPENROUTER_API_KEY, AGOE_AGENT_MODEL, AGOE_OPENAI_BASE (default OpenRouter).
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

PROTOCOL = 'agoe.agent/v1'
MODEL = os.environ.get('AGOE_AGENT_MODEL', '')
BASE = os.environ.get('AGOE_OPENAI_BASE', 'https://openrouter.ai/api/v1').rstrip('/')
RETRYABLE = {408, 409, 425, 429, 500, 502, 503, 504}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None  # never forward the Authorization header to another host


OPENER = urllib.request.build_opener(NoRedirect)


def complete(messages, deadline):
    body = json.dumps({'model': MODEL, 'messages': messages, 'temperature': 1.0, 'max_tokens': 4000}).encode()
    attempt = 0
    while True:
        req = urllib.request.Request(f'{BASE}/chat/completions', data=body, method='POST', headers={
            'Authorization': f"Bearer {os.environ['OPENROUTER_API_KEY']}", 'Content-Type': 'application/json'})
        left = deadline - time.time()
        if left < 3:
            return None, 'timeout'
        try:
            with OPENER.open(req, timeout=left) as r:
                return json.loads(r.read().decode() or '{}'), None
        except urllib.error.HTTPError as e:
            if e.code not in RETRYABLE:
                return None, 'api_error'
            wait = float(e.headers.get('Retry-After') or 0) or min(2 ** attempt, 8)
        except (urllib.error.URLError, TimeoutError, ValueError):
            wait = min(2 ** attempt, 8)
        attempt += 1
        if time.time() + wait > deadline - 3:
            return None, 'api_error'
        time.sleep(wait)


class Agent:
    def __init__(self):
        if not MODEL.endswith(':free'):
            raise SystemExit('AGOE_AGENT_MODEL must be a :free model id')
        self.messages = []

    def on_start(self, scenario, system):
        self.messages = [{'role': 'system', 'content': system}]

    def decide(self, step, observation, options, deadline_ms):
        prompt = observation + '\n\nOptions:\n' + '\n'.join(f"{o['id']}. {o['text']}" for o in options)
        self.messages.append({'role': 'user', 'content': prompt})
        reply, err = complete(self.messages, time.time() + deadline_ms / 1000)
        if err:
            return {'error': err}
        served = reply.get('model')
        if served and served != MODEL:
            return {'error': 'served_model_mismatch'}
        try:
            choice0 = reply['choices'][0]
            content = choice0['message'].get('content') or ''
        except (KeyError, IndexError, TypeError):
            return {'error': 'malformed_response'}
        if choice0.get('finish_reason') == 'length':
            return {'error': 'truncated'}
        try:
            parsed = json.loads(re.sub(r'^```(json)?|```$', '', content.strip()).strip())
            choice = int(parsed['choice'])
            rationale = str(parsed.get('rationale', ''))
        except (ValueError, KeyError, TypeError):
            return {'error': 'schema_invalid'}
        if not 1 <= choice <= len(options):
            return {'error': 'invalid_choice'}
        self.messages.append({'role': 'assistant', 'content': content})
        u = reply.get('usage') or {}
        return {'choice': choice, 'rationale': rationale[:2000],
                'usage': {'input_tokens': u.get('prompt_tokens', 0), 'output_tokens': u.get('completion_tokens', 0)}}

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
            print(f'agent error: {type(error).__name__}', file=sys.stderr)
            reply = {'error': 'agent_exception'}
        sys.stdout.write(json.dumps(reply) + '\n')
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
