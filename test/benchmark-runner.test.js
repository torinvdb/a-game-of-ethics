// Contract tests for benchmark/run: Anthropic adapter against a local Messages API mock,
// and an offline end-to-end run with resume.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { anthropicProvider, RunError } from '../benchmark/run/providers.mjs';

function serve(handler) {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      let body = '';
      req.on('data', (c) => (body += c));
      req.on('end', () => {
        const [status, payload] = handler(JSON.parse(body));
        res.writeHead(status, { 'content-type': 'application/json' });
        res.end(JSON.stringify(payload));
      });
    });
    srv.listen(0, '127.0.0.1', () => resolve(srv));
  });
}
const msg = (text, model = 'claude-haiku-5-5', stop = 'end_turn') => ({ id: 'm', type: 'message', role: 'assistant', model,
  content: [{ type: 'text', text }], stop_reason: stop, stop_sequence: null, usage: { input_tokens: 10, output_tokens: 5 } });

test('anthropic adapter: request shape and failure classes', async () => {
  let next;
  let last;
  const srv = await serve((body) => { last = body; return next; });
  process.env.ANTHROPIC_BASE_URL = `http://127.0.0.1:${srv.address().port}`;
  process.env.ANTHROPIC_API_KEY = 'test';
  const p = anthropicProvider({ maxRetries: 0, timeoutMs: 5000 });
  const call = () => p.decide({ system: 's', messages: [{ role: 'user', content: 'x' }], numChoices: 3, model: 'claude-haiku-5-5',
    settings: { max_tokens: 1000, effort: 'medium' } });
  try {
    next = [200, msg('{"choice":2,"rationale":"r"}')];
    const ok = await call();
    assert.equal(ok.choice, 2);
    assert.equal(last.temperature, undefined);
    assert.equal(last.fallbacks, undefined);
    assert.deepEqual(last.output_config.format.schema.properties.choice.enum, [1, 2, 3]);
    assert.equal(last.output_config.effort, 'medium');
    const expect = async (reply, cls) => {
      next = reply;
      await assert.rejects(call(), (e) => e instanceof RunError && e.failureClass === cls);
    };
    await expect([200, msg('{"choice":2,"rationale":"r"}', 'claude-haiku-5-5', 'refusal')], 'refusal');
    await expect([200, msg('{"choice":2', 'claude-haiku-5-5', 'max_tokens')], 'truncated');
    await expect([200, msg('{"choice":2,"rationale":"r"}', 'claude-opus-5-5')], 'served_model_mismatch');
    await expect([200, msg('{"choice":9,"rationale":"r"}')], 'schema_invalid');
    await expect([200, msg('nope')], 'schema_invalid');
    await expect([429, { type: 'error', error: { type: 'rate_limit_error', message: 'x' } }], 'api_error');
  } finally {
    srv.close();
    delete process.env.ANTHROPIC_BASE_URL;
  }
});

test('offline end-to-end run is complete and resumable', () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'agoe-run-'));
  const args = ['benchmark/run/run.mjs', '--provider', 'mock', '--stage', 'smoke', '--scenarios', 'hostage-holdout',
    '--models', 'claude-haiku-5-5', '--out', out];
  execFileSync(process.execPath, args, { encoding: 'utf8' });
  const rows = fs.readFileSync(path.join(out, 'results.jsonl'), 'utf8').trim().split('\n').map((l) => JSON.parse(l));
  assert.equal(rows.length, 2); // 1 rep x 2 framings
  for (const r of rows) {
    assert.ok(r.decisions.length >= 3);
    for (const d of r.decisions) assert.equal(d.option_text, d.options[d.original_index]);
  }
  const again = execFileSync(process.execPath, args, { encoding: 'utf8' });
  assert.match(again, /^0\/2 cells to run/m);
  fs.rmSync(out, { recursive: true, force: true });
});
