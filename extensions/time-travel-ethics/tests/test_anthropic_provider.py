"""Contract tests for ethicslab.anthropic_provider against a local Messages API mock."""
import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

try:
    import anthropic
except ImportError:  # optional dependency
    anthropic = None

from ethicslab.anthropic_provider import decide_anthropic
from ethicslab.provider import ProviderError

REPLY = {}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['content-length'])))
        REPLY['last_request'] = body
        status, payload = REPLY['next']
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('content-type', 'application/json')
        self.send_header('content-length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def message(text, model='claude-haiku-5-5', stop='end_turn'):
    return {'id': 'msg_1', 'type': 'message', 'role': 'assistant', 'model': model,
            'content': [{'type': 'text', 'text': text}], 'stop_reason': stop, 'stop_sequence': None,
            'usage': {'input_tokens': 12, 'output_tokens': 7}}


@unittest.skipIf(anthropic is None, 'anthropic SDK not installed')
class AnthropicProviderContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = HTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.client = anthropic.Anthropic(api_key='test', base_url=f'http://127.0.0.1:{cls.srv.server_port}', max_retries=0)

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def call(self, status, payload):
        REPLY['next'] = (status, payload)
        return decide_anthropic('claude-haiku-5-5', 'sys', 'obs', ['a', 'b'], client=self.client)

    def test_valid_decision_and_request_shape(self):
        out = self.call(200, message(json.dumps({'action': 'b', 'reason': 'r'})))
        self.assertEqual(out['action'], 'b')
        self.assertEqual(out['usage']['input_tokens'], 12)
        req = REPLY['last_request']
        self.assertNotIn('temperature', req)
        self.assertNotIn('fallbacks', req)
        self.assertEqual(req['thinking'], {'type': 'adaptive'})
        self.assertEqual(req['output_config']['format']['schema']['properties']['action']['enum'], ['a', 'b'])

    def test_failure_classes(self):
        cases = [((200, message('{"action":"b","reason":"r"}', stop='refusal')), 'refusal'),
                 ((200, message('{"action":"b"', stop='max_tokens')), 'truncated'),
                 ((200, message('{"action":"b","reason":"r"}', model='claude-opus-5-5')), 'served_model_mismatch'),
                 ((200, message('{"action":"zzz","reason":"r"}')), 'malformed_decision'),
                 ((200, message('not json')), 'malformed_decision'),
                 ((429, {'type': 'error', 'error': {'type': 'rate_limit_error', 'message': 'slow'}}), 'rate_limited'),
                 ((500, {'type': 'error', 'error': {'type': 'api_error', 'message': 'x'}}), 'server_error'),
                 ((400, {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'x'}}), 'client_error')]
        for (status, payload), kind in cases:
            with self.subTest(kind=kind):
                with self.assertRaises(ProviderError) as cm:
                    self.call(status, payload)
                self.assertEqual(cm.exception.kind, kind)


class RetryBudgetTests(unittest.TestCase):
    def test_client_retries_fit_inside_the_replay_decision_timeout(self):
        # replay-cluster.mjs kills the bridge after a fixed wall-clock budget per decision. If one
        # request may outlive it, a single stalled call ends the trajectory instead of being retried.
        import re
        from pathlib import Path
        from ethicslab import anthropic_provider as ap
        src = (Path(__file__).resolve().parents[1] / 'tools/replay-cluster.mjs').read_text()
        bridge_ms = int(re.search(r"arg\('--decision-timeout-ms','(\d+)'\)", src).group(1))  # default budget
        worst = ap.REQUEST_TIMEOUT_S * (ap.MAX_RETRIES + 1) + ap.BACKOFF_ALLOWANCE_S
        self.assertLess(worst, bridge_ms / 1000)
        self.assertGreaterEqual(ap.MAX_RETRIES, 1)


if __name__ == '__main__':
    unittest.main()
