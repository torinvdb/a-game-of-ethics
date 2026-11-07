import { test } from 'node:test';
import assert from 'node:assert/strict';
import { AdapterError, askModelForChoice, backoffDelay, redact, requestCompletion, resolveAdapterConfig } from '../src/lib/llm.js';
import { startMockServer, completion } from './helpers/mock-openai.js';

const KEY = 'sk-or-test-0123456789abcdef';
const noSleep = async () => {};

function config(url, extra = {}) {
  return resolveAdapterConfig({ baseUrl: url, apiKey: KEY, sleep: noSleep, ...extra }, {});
}

test('config: https required except loopback; key required for remote hosts', () => {
  assert.throws(() => resolveAdapterConfig({ baseUrl: 'http://example.com/v1', apiKey: KEY }, {}), /https/);
  assert.throws(() => resolveAdapterConfig({ baseUrl: 'https://user:pw@example.com/v1', apiKey: KEY }, {}), /credentials/);
  assert.throws(() => resolveAdapterConfig({}, {}), /OPENROUTER_API_KEY/);
  assert.equal(resolveAdapterConfig({ baseUrl: 'http://127.0.0.1:9/v1' }, {}).apiKey, '');
  assert.equal(resolveAdapterConfig({}, { OPENROUTER_API_KEY: KEY }).baseUrl, 'https://openrouter.ai/api/v1');
});

test('redact removes keys and bearer tokens', () => {
  const out = redact(`bad key ${KEY} / Authorization: Bearer abcdefghijklmnop / sk-zzzzzzzzzzzz`, [KEY]);
  assert.ok(!out.includes(KEY));
  assert.ok(!out.includes('abcdefghijklmnop'));
  assert.ok(!out.includes('zzzzzzzzzzzz'));
});

test('backoff grows and honours Retry-After', () => {
  assert.equal(backoffDelay(0, 2000), 2000);
  assert.equal(backoffDelay(0, 999_999), 30_000);
  assert.ok(backoffDelay(3, null, () => 1) > backoffDelay(0, null, () => 1));
});

test('retries 503 then succeeds; sends bearer key', async (t) => {
  const srv = await startMockServer((body, n) => (n < 3 ? { status: 503, json: { error: { message: 'busy' } } } : completion('CHOICE: 2')));
  t.after(srv.close);
  const r = await requestCompletion(config(srv.url), { model: 'm', messages: [] });
  assert.equal(r.content, 'CHOICE: 2');
  assert.equal(srv.requests.length, 3);
  assert.equal(srv.requests[0].headers.authorization, `Bearer ${KEY}`);
});

test('401 is not retried and the key is not echoed in the error', async (t) => {
  const srv = await startMockServer(() => ({ status: 401, json: { error: { message: `invalid key ${KEY}` } } }));
  t.after(srv.close);
  await assert.rejects(requestCompletion(config(srv.url), { model: 'm', messages: [] }), (err) => {
    assert.ok(err instanceof AdapterError);
    assert.equal(err.kind, 'http');
    assert.equal(err.status, 401);
    assert.ok(!err.message.includes(KEY));
    return true;
  });
  assert.equal(srv.requests.length, 1);
});

test('HTTP 200 with an error object is an adapter error', async (t) => {
  const srv = await startMockServer(() => ({ json: { error: { code: 400, message: 'provider rejected' } } }));
  t.after(srv.close);
  await assert.rejects(requestCompletion(config(srv.url), { model: 'm', messages: [] }), { kind: 'http' });
});

test('non-JSON and shape-less bodies are malformed_response', async (t) => {
  const srv = await startMockServer((b, n) => (n === 1 ? { text: '<html>oops' } : { json: { choices: [] } }));
  t.after(srv.close);
  await assert.rejects(requestCompletion(config(srv.url), { model: 'm', messages: [] }), { kind: 'malformed_response' });
  await assert.rejects(requestCompletion(config(srv.url), { model: 'm', messages: [] }), { kind: 'malformed_response' });
});

test('timeouts are retried then reported as timeout', async (t) => {
  const srv = await startMockServer(() => ({ hang: true }));
  t.after(srv.close);
  const cfg = config(srv.url, { timeoutMs: 1000, maxRetries: 1 });
  await assert.rejects(requestCompletion(cfg, { model: 'm', messages: [] }), { kind: 'timeout' });
  assert.equal(srv.requests.length, 2);
});

test('network errors are classified', async () => {
  const cfg = config('http://127.0.0.1:9/v1', { maxRetries: 0 });
  await assert.rejects(requestCompletion(cfg, { model: 'm', messages: [] }), { kind: 'network' });
});

test('askModelForChoice re-prompts once on an unparseable reply', async (t) => {
  const srv = await startMockServer((b, n) => (n === 1 ? completion('Let me think about it...') : completion('CHOICE: 3\nbecause.')));
  t.after(srv.close);
  const r = await askModelForChoice(config(srv.url), { context: 'ctx', choices: ['a', 'b', 'c'], model: 'm' });
  assert.equal(r.index, 2);
  assert.equal(r.attempts, 2);
  assert.match(srv.requests[1].body.messages.at(-1).content, /CHOICE: <number>/);
});

test('askModelForChoice surfaces refusals without re-prompting', async (t) => {
  const srv = await startMockServer(() => completion("I'm sorry, but I can't choose."));
  t.after(srv.close);
  await assert.rejects(askModelForChoice(config(srv.url), { context: 'ctx', choices: ['a', 'b'], model: 'm' }), { kind: 'refusal' });
  assert.equal(srv.requests.length, 1);
});

test('askModelForChoice handles provider refusal field', async (t) => {
  const srv = await startMockServer(() => ({ json: { choices: [{ finish_reason: 'stop', message: { role: 'assistant', content: null, refusal: 'no' } }] } }));
  t.after(srv.close);
  await assert.rejects(askModelForChoice(config(srv.url), { context: 'ctx', choices: ['a', 'b'], model: 'm' }), { kind: 'refusal' });
});
