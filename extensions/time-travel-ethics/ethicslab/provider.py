"""OpenAI-compatible chat-completions client with explicit failure classes.

Every failure raises ProviderError with a stable ``kind``. Callers record the
kind as an execution failure; it is never a policy outcome. Response bodies,
headers and credentials are not copied into errors or evidence.

Contract (what this module promises, and what was tested against a local mock):
- HTTPS for remote hosts; plain HTTP only for loopback; no URL credentials.
- Redirects are refused, so an Authorization header cannot be forwarded to a
  different host and an answer cannot come from a host the caller did not name.
- 429 and 5xx are retried a bounded number of times. Retry-After (seconds) is
  honoured up to ``max_wait``; larger values fail instead of stalling a run.
- Timeouts are retried like 5xx. Other 4xx are not retried.
- Response bodies above ``max_bytes`` are rejected.
- The decision is a JSON object with a string ``action``. It may arrive as the
  message content or as the arguments of a single ``choose_action`` tool call.
  Markdown fences and free text around JSON are rejected, not repaired.
This is not a claim that any specific provider or local runtime conforms.
"""
import ipaddress
import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

KINDS = ('config', 'rate_limited', 'server_error', 'client_error', 'timeout',
         'connection', 'redirect_refused', 'oversized', 'non_json', 'bad_envelope',
         'empty_content', 'malformed_decision', 'unsupported_tool_call',
         'refusal', 'truncated', 'served_model_mismatch')


class ProviderError(Exception):
    def __init__(self, kind, attempts=1):
        assert kind in KINDS, kind
        super().__init__(kind)
        self.kind, self.attempts = kind, attempts


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError('redirect_refused')


_OPENER = urllib.request.build_opener(_NoRedirect)


def check_endpoint(endpoint):
    url = urllib.parse.urlparse(endpoint)
    try:
        local = ipaddress.ip_address(url.hostname).is_loopback
    except (ValueError, TypeError):
        local = url.hostname == 'localhost'
    if not url.hostname or url.username or url.password or (
            url.scheme != 'https' and not (url.scheme == 'http' and local)):
        raise ValueError('Use HTTPS, or HTTP for a loopback model server; no URL credentials')


def parse_decision(data):
    """Extract {"action", "reason"} from a chat-completions envelope."""
    try:
        message = data['choices'][0]['message']
    except (KeyError, IndexError, TypeError):
        raise ProviderError('bad_envelope')
    if not isinstance(message, dict):
        raise ProviderError('bad_envelope')
    calls = message.get('tool_calls') or []
    if calls:
        if len(calls) != 1 or (calls[0].get('function') or {}).get('name') != 'choose_action':
            raise ProviderError('unsupported_tool_call')
        raw = calls[0]['function'].get('arguments')
    else:
        raw = message.get('content')
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raise ProviderError('empty_content')
    try:
        answer = json.loads(raw) if isinstance(raw, str) else raw
    except json.JSONDecodeError:
        raise ProviderError('malformed_decision')
    if not isinstance(answer, dict) or not isinstance(answer.get('action'), str):
        raise ProviderError('malformed_decision')
    return {'action': answer['action'], 'reason': str(answer.get('reason', ''))[:1000]}


def _with_usage(result, data):
    """Attach token counts and the served model when the envelope reports them (for cost caps)."""
    usage = data.get('usage') if isinstance(data, dict) else None
    if isinstance(usage, dict):
        result['usage'] = {'input_tokens': int(usage.get('prompt_tokens') or 0),
                           'output_tokens': int(usage.get('completion_tokens') or 0)}
    if isinstance(data, dict) and isinstance(data.get('model'), str):
        result['served_model'] = data['model'][:200]
    return result


def _retry_after(headers):
    value = headers.get('Retry-After') if headers else None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return None


def chat_completion(endpoint, model, messages, api_key=None, timeout=60, retries=2,
                    backoff=1.0, max_wait=30.0, max_bytes=1 << 20, sleep=time.sleep,
                    extra=None):
    check_endpoint(endpoint)
    body = json.dumps({'model': model, 'temperature': 0, 'messages': messages, **(extra or {})}).encode()
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['Authorization'] = 'Bearer ' + api_key
    attempt = 0
    while True:
        attempt += 1
        wait, kind = backoff * attempt, None
        try:
            request = urllib.request.Request(endpoint, body, headers, method='POST')
            with _OPENER.open(request, timeout=timeout) as response:
                payload = response.read(max_bytes + 1)
            if len(payload) > max_bytes:
                raise ProviderError('oversized', attempt)
            try:
                data = json.loads(payload)
            except (json.JSONDecodeError, UnicodeDecodeError):
                raise ProviderError('non_json', attempt)
            try:
                result = parse_decision(data)
            except ProviderError as error:
                raise ProviderError(error.kind, attempt)
            return _with_usage(result, data)
        except ProviderError as error:
            if error.kind == 'redirect_refused':
                raise ProviderError('redirect_refused', attempt)
            raise
        except urllib.error.HTTPError as error:
            if error.code == 429:
                kind = 'rate_limited'
                hinted = _retry_after(error.headers)
                if hinted is not None:
                    if hinted > max_wait:
                        raise ProviderError(kind, attempt)
                    wait = hinted
            elif 300 <= error.code < 400:
                raise ProviderError('redirect_refused', attempt)
            elif error.code >= 500:
                kind = 'server_error'
            else:
                raise ProviderError('client_error', attempt)
        except (socket.timeout, TimeoutError):
            kind = 'timeout'
        except urllib.error.URLError as error:
            kind = 'timeout' if isinstance(error.reason, (socket.timeout, TimeoutError)) else 'connection'
        except (ConnectionError, OSError):
            kind = 'connection'
        if attempt > retries:
            raise ProviderError(kind, attempt)
        sleep(min(wait, max_wait))
