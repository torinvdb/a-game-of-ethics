"""Provider-contract checks against a local OpenAI-compatible mock server.

These exercise the client's documented contract (ethicslab/provider.py). They do
not establish that any real provider or local runtime behaves like the mock.
"""
import json
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ethicslab.provider import ProviderError, chat_completion, parse_decision


def completion(content=None, tool_calls=None):
    message = {'role': 'assistant', 'content': content}
    if tool_calls is not None:
        message['tool_calls'] = tool_calls
    return {'choices': [{'index': 0, 'message': message}]}


class Mock:
    """Serves a scripted list of responses: (status, headers, body-bytes, delay)."""

    def __init__(self, script, host='127.0.0.1'):
        self.script, self.requests = list(script), []
        mock = self

        class Handler(BaseHTTPRequestHandler):
            def _serve(self):
                length = int(self.headers.get('Content-Length') or 0)
                mock.requests.append({'path': self.path, 'method': self.command,
                                      'auth': self.headers.get('Authorization'),
                                      'body': self.rfile.read(length)})
                status, headers, body, delay = mock.script.pop(0) if mock.script else (500, {}, b'', 0)
                time.sleep(delay)
                try:
                    self.send_response(status)
                    for key, value in headers.items():
                        self.send_header(key, value)
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass
            do_POST = do_GET = _serve

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer((host, 0), Handler)
        self.url = f'http://{host}:{self.server.server_port}/v1/chat/completions'
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def ok(payload, headers=None):
    return (200, {'Content-Type': 'application/json', **(headers or {})}, json.dumps(payload).encode(), 0)


class ProviderContractTests(unittest.TestCase):
    def call(self, script, **kw):
        mock = Mock(script)
        self.addCleanup(mock.close)
        sleeps = []
        kw.setdefault('sleep', sleeps.append)
        kw.setdefault('timeout', 2)
        try:
            return chat_completion(mock.url, 'fixture-model', [{'role': 'user', 'content': 'x'}], **kw), mock, sleeps
        except ProviderError as error:
            return error, mock, sleeps

    def test_plain_content_decision_and_request_shape(self):
        out, mock, _ = self.call([ok(completion('{"action":"escalate","reason":"approval missing"}'))], api_key='k')
        self.assertEqual(out, {'action': 'escalate', 'reason': 'approval missing'})
        sent = json.loads(mock.requests[0]['body'])
        self.assertEqual((sent['model'], sent['temperature'], mock.requests[0]['auth']), ('fixture-model', 0, 'Bearer k'))

    def test_tool_call_style_reply(self):
        call = [{'id': 'c1', 'type': 'function', 'function': {'name': 'choose_action',
                 'arguments': '{"action":"redact","reason":"consent expired"}'}}]
        out, _, _ = self.call([ok(completion(None, call))])
        self.assertEqual(out['action'], 'redact')

    def test_unknown_or_multiple_tool_calls_rejected(self):
        bad = [{'function': {'name': 'run_shell', 'arguments': '{}'}}]
        out, _, _ = self.call([ok(completion(None, bad))])
        self.assertEqual(out.kind, 'unsupported_tool_call')
        two = [{'function': {'name': 'choose_action', 'arguments': '{"action":"a"}'}}] * 2
        out, _, _ = self.call([ok(completion(None, two))])
        self.assertEqual(out.kind, 'unsupported_tool_call')

    def test_429_honours_retry_after_then_succeeds(self):
        out, mock, sleeps = self.call([(429, {'Retry-After': '3'}, b'{}', 0),
                                       ok(completion('{"action":"keep"}'))])
        self.assertEqual(out['action'], 'keep')
        self.assertEqual((sleeps, len(mock.requests)), ([3.0], 2))

    def test_429_with_excessive_retry_after_fails_fast(self):
        out, mock, sleeps = self.call([(429, {'Retry-After': '3600'}, b'', 0)])
        self.assertEqual((out.kind, len(mock.requests), sleeps), ('rate_limited', 1, []))

    def test_persistent_429_exhausts_bounded_retries(self):
        out, mock, sleeps = self.call([(429, {}, b'', 0)] * 5, retries=2, backoff=0.5)
        self.assertEqual((out.kind, out.attempts, len(mock.requests)), ('rate_limited', 3, 3))
        self.assertEqual(sleeps, [0.5, 1.0])

    def test_5xx_retried_4xx_not(self):
        out, mock, _ = self.call([(503, {}, b'busy', 0), ok(completion('{"action":"report"}'))])
        self.assertEqual((out['action'], len(mock.requests)), ('report', 2))
        out, mock, _ = self.call([(400, {}, b'{"error":"bad temperature"}', 0)] * 3)
        self.assertEqual((out.kind, len(mock.requests)), ('client_error', 1))

    def test_timeout_classified_and_retried(self):
        out, mock, _ = self.call([(200, {}, b'{}', 1.5)] * 2, timeout=0.3, retries=1)
        self.assertEqual((out.kind, out.attempts), ('timeout', 2))

    def test_non_json_and_bad_envelopes(self):
        for body, kind in [(b'<html>gateway</html>', 'non_json'), (b'{"choices":[]}', 'bad_envelope'),
                           (b'{"error":{"message":"x"}}', 'bad_envelope'),
                           (json.dumps(completion(None)).encode(), 'empty_content'),
                           (json.dumps(completion('```json\n{"action":"keep"}\n```')).encode(), 'malformed_decision'),
                           (json.dumps(completion('{"action": "keep"')).encode(), 'malformed_decision'),
                           (json.dumps(completion('{"choice":"keep"}')).encode(), 'malformed_decision'),
                           (json.dumps(completion('["keep"]')).encode(), 'malformed_decision')]:
            out, _, _ = self.call([(200, {}, body, 0)])
            self.assertIsInstance(out, ProviderError, body)
            self.assertEqual(out.kind, kind, body)

    def test_oversized_response_rejected(self):
        out, _, _ = self.call([(200, {}, b' ' * 5000 + json.dumps(completion('{"action":"a"}')).encode(), 0)],
                              max_bytes=1000)
        self.assertEqual(out.kind, 'oversized')

    def test_redirect_not_followed_and_credentials_not_forwarded(self):
        # Previously urllib followed a 302 to another host with the Authorization header.
        sink = Mock([ok(completion('{"action":"share"}'))], host='127.0.0.2')
        self.addCleanup(sink.close)
        for code in (301, 302, 303, 307, 308):
            out, _, _ = self.call([(code, {'Location': sink.url}, b'', 0)], api_key='sk-not-real')
            self.assertEqual(out.kind, 'redirect_refused', code)
        self.assertEqual(sink.requests, [])

    def test_connection_refused(self):
        mock = Mock([])
        url = mock.url
        mock.close()
        with self.assertRaises(ProviderError) as ctx:
            chat_completion(url, 'm', [], sleep=lambda s: None, retries=1, timeout=1)
        self.assertEqual(ctx.exception.kind, 'connection')

    def test_endpoint_policy(self):
        for url in ('http://example.com/v1', 'http://user:pw@127.0.0.1/v1', 'ftp://127.0.0.1/', 'https:///nohost'):
            with self.assertRaises(ValueError, msg=url):
                chat_completion(url, 'm', [])

    def test_parse_decision_truncates_reason(self):
        out = parse_decision(completion(json.dumps({'action': 'a', 'reason': 'r' * 5000})))
        self.assertEqual(len(out['reason']), 1000)


class LiveRunClassificationTests(unittest.TestCase):
    """Execution failures must stay separate from guard blocks and violations."""

    def test_provider_failures_are_not_guard_blocks_or_violations(self):
        import os
        from ethicslab.__main__ import run
        script = [(429, {'Retry-After': '0'}, b'', 0)] * 3 + [(200, {}, b'not json', 0)] * 3 + \
                 [ok(completion('{"action":"no_such_action"}'))] * 6
        mock = Mock(script)
        self.addCleanup(mock.close)
        os.environ.pop('ETHICS_API_KEY', None)
        from unittest.mock import patch
        with patch('ethicslab.provider.time.sleep', lambda s: None):
            s = run(months=1, agent='live', model='fixture', endpoint=mock.url)['summary']
        self.assertEqual(s['blocked'], 0)
        self.assertEqual(s['realized_violation'], 0)
        self.assertEqual(s['completed'], 0)
        self.assertEqual(s['execution_failures'], 6)
        self.assertEqual(s['adapter_error_kinds'], {'non_json': 3, 'rate_limited': 1})
        self.assertEqual(s['invalid'], 6)


if __name__ == '__main__':
    unittest.main()
