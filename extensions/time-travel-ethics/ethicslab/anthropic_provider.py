"""Anthropic Messages API decisions via the official SDK (optional: requirements-anthropic.txt).

Structured output constrains "action" to the offered choices. No sampling parameters
(current models reject them) and no server-side fallbacks (a fallback would change the
model under test). Refusals, truncation and model substitution raise ProviderError.
"""
import json
import os

from .provider import ProviderError

# tools/replay-cluster.mjs gives each decision 90 s of wall clock. Every attempt plus the SDK's
# backoff must fit inside that, or one stalled request ends the trajectory without a retry.
REQUEST_TIMEOUT_S = 40
MAX_RETRIES = 1
BACKOFF_ALLOWANCE_S = 8  # SDK backoff caps at 8 s per retry


def decide_anthropic(model, system, user_text, choices, effort=None, max_tokens=16000, timeout=REQUEST_TIMEOUT_S,
                     client=None):
    import anthropic
    client = client or anthropic.Anthropic(timeout=timeout, max_retries=MAX_RETRIES)
    schema = {'type': 'object',
              'properties': {'action': {'type': 'string', 'enum': list(choices)}, 'reason': {'type': 'string'}},
              'required': ['action', 'reason'], 'additionalProperties': False}
    try:
        r = client.messages.create(
            model=model, max_tokens=max_tokens, system=system,
            messages=[{'role': 'user', 'content': user_text}],
            thinking={'type': 'adaptive'},
            output_config={'effort': effort or os.environ.get('ETHICS_EFFORT', 'medium'),
                           'format': {'type': 'json_schema', 'schema': schema}})
    except anthropic.APITimeoutError:
        raise ProviderError('timeout')
    except anthropic.RateLimitError:
        raise ProviderError('rate_limited')
    except anthropic.InternalServerError:
        raise ProviderError('server_error')
    except anthropic.APIStatusError:
        raise ProviderError('client_error')
    except anthropic.APIConnectionError:
        raise ProviderError('connection')
    if r.model != model:
        raise ProviderError('served_model_mismatch')
    if r.stop_reason == 'refusal':
        raise ProviderError('refusal')
    if r.stop_reason == 'max_tokens':
        raise ProviderError('truncated')
    text = ''.join(b.text for b in r.content if b.type == 'text')
    if not text.strip():
        raise ProviderError('empty_content')
    try:
        answer = json.loads(text)
    except json.JSONDecodeError:
        raise ProviderError('malformed_decision')
    if not isinstance(answer, dict) or answer.get('action') not in choices:
        raise ProviderError('malformed_decision')
    u = r.usage
    usage = {k: getattr(u, k, 0) or 0 for k in ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')}
    return {'action': answer['action'], 'reason': str(answer.get('reason', ''))[:1000], 'usage': usage, 'served_model': r.model}
