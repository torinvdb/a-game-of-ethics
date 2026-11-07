#!/usr/bin/env python3
"""Reference agoe.agent/v1 agent over HTTP (stdlib http.server only).

Serves POST /start, /decide and /end, plus GET /health for container health checks. One server handles many runs at once; memory is keyed by
run_id and dropped at /end.

  python3 examples/agents/http_agent.py --host 127.0.0.1 --port 8080
  node benchmark/run/run.mjs --agent-url http://127.0.0.1:8080 --stage smoke \
      --scenarios hostage-holdout --out /tmp/agoe-http

--port 0 picks a free port. The first stdout line is "listening on http://HOST:PORT".
If AGOE_AGENT_TOKEN is set, requests must carry "Authorization: Bearer <token>".
"""
import argparse
import hmac
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rule_policy import RulePolicy  # noqa: E402

PROTOCOL = 'agoe.agent/v1'
MAX_BODY = 1024 * 1024
RUNS = {}
LOCK = threading.Lock()
TOKEN = os.environ.get('AGOE_AGENT_TOKEN')
LOG = None


def handle(route, msg):
    run_id = msg.get('run_id')
    if route == 'start':
        if msg.get('protocol') != PROTOCOL:
            return {'error': 'unsupported_protocol'}
        with LOCK:
            RUNS[run_id] = RulePolicy(msg['scenario'])
        return {'ok': True}
    with LOCK:
        policy = RUNS.get(run_id)
    if policy is None:
        return {'error': 'unknown_run'}
    if route == 'decide':
        return policy.decide(msg['step'], msg['options'])
    with LOCK:
        RUNS.pop(run_id, None)
    return {'ok': True}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        # Optional liveness probe for container health checks; not part of agoe.agent/v1.
        if self.path.rstrip('/') == '/health':
            return self.reply(200, {'ok': True})
        return self.reply(404, {'error': 'not_found'})

    def do_POST(self):
        route = self.path.rstrip('/').rsplit('/', 1)[-1]
        if route not in ('start', 'decide', 'end'):
            return self.reply(404, {'error': 'not_found'})
        if TOKEN and not hmac.compare_digest(self.headers.get('authorization', ''), f'Bearer {TOKEN}'):
            return self.reply(401, {'error': 'unauthorized'})
        length = int(self.headers.get('content-length') or 0)
        if length > MAX_BODY:
            return self.reply(413, {'error': 'too_large'})
        raw = self.rfile.read(length)
        if LOG:
            with LOCK, open(LOG, 'a', encoding='utf-8') as f:
                f.write(raw.decode('utf-8', 'replace') + '\n')
        try:
            msg = json.loads(raw)
            if not isinstance(msg, dict):
                raise ValueError
            return self.reply(200, handle(route, msg))
        except (ValueError, KeyError, TypeError):
            return self.reply(400, {'error': 'bad_message'})

    def log_message(self, fmt, *args):
        sys.stderr.write('%s %s\n' % (self.address_string(), fmt % args))


def main():
    global LOG
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=8080)
    ap.add_argument('--log-messages')
    a = ap.parse_args()
    LOG = a.log_messages
    server = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f'listening on http://{a.host}:{server.server_address[1]}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
