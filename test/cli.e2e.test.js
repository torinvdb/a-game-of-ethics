// End-to-end: run the real CLI against a local mock of the chat-completions API.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startMockServer, completion, alwaysFirst } from './helpers/mock-openai.js';
import { playInkStory } from '../src/manual-player.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const cli = path.join(root, 'ethi-cli.js');
const scenario = path.join(root, 'scenarios', 'core', 'hostage-holdout.ink');
const KEY = 'sk-or-e2e-secret-0123456789';

function run(args, env = {}) {
  return new Promise((resolve) => {
    const child = spawn(process.execPath, [cli, ...args], {
      cwd: root,
      env: { PATH: process.env.PATH, NO_COLOR: '1', ETHI_MAX_RETRIES: '0', ...env }
    });
    let out = '';
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (out += d));
    child.on('close', (code) => resolve({ code, out }));
  });
}

const tmp = (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ethi-e2e-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  return dir;
};
const results = (dir) =>
  fs.readdirSync(dir, { recursive: true }).filter((f) => f.endsWith('.json')).map((f) => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')));

test('--help and list work without a TTY', async () => {
  const help = await run(['--help']);
  assert.equal(help.code, 0);
  assert.match(help.out, /model \[options\] <file>/);
  const list = await run(['list', '--json']);
  assert.equal(list.code, 0);
  assert.ok(JSON.parse(list.out).some((s) => s.id === 'hostage-holdout'));
  const plain = await run(['list']);
  assert.doesNotMatch(plain.out, /\x1b\[/);
});

test('interactive mode refuses to start without a TTY', async () => {
  const r = await run([]);
  assert.equal(r.code, 1);
  assert.match(r.out, /needs a terminal/);
});

test('model run against mock endpoint completes and records a verdict', async (t) => {
  const srv = await startMockServer(alwaysFirst);
  t.after(srv.close);
  const out = tmp(t);
  const r = await run(['model', scenario, '--model', 'mock/first', '--base-url', srv.url, '-o', out], { OPENROUTER_API_KEY: KEY });
  assert.equal(r.code, 0, r.out);
  assert.ok(!r.out.includes(KEY), 'API key must never be printed');
  const [res] = results(out);
  assert.equal(res.complete, true);
  assert.ok(res.choices.length > 0);
  assert.ok(res.choices.every((c) => c.selected === 0 && c.parse_method === 'explicit'));
  assert.match(res.verdict, /^(EXEMPLARY|RESPONSIBLE|AMBIGUOUS|QUESTIONABLE|HARMFUL)/);
  assert.equal(srv.requests[0].body.model, 'mock/first');
});

test('adapter errors abort the run and are never recorded as choices', async (t) => {
  const srv = await startMockServer(() => completion('I am thinking about the trade-offs here...'));
  t.after(srv.close);
  const out = tmp(t);
  const r = await run(['model', scenario, '--model', 'mock/broken', '--base-url', srv.url, '-o', out], { ETHI_PARSE_RETRIES: '1' });
  assert.equal(r.code, 2, r.out);
  const [res] = results(out);
  assert.equal(res.complete, false);
  assert.equal(res.adapter_failure.kind, 'unparseable');
  assert.deepEqual(res.choices, []);
  assert.equal(res.verdict, null);
  assert.equal(srv.requests.length, 2, 'one re-prompt, then give up');
});

test('HTTP 500 with retries disabled marks the batch run incomplete', async (t) => {
  const srv = await startMockServer(() => ({ status: 500, json: { error: { message: 'boom' } } }));
  t.after(srv.close);
  const out = tmp(t);
  const r = await run(['model', scenario, '--model', 'mock/down', '--base-url', srv.url, '-o', out, '-n', '2']);
  assert.equal(r.code, 2, r.out);
  const [res] = results(out);
  assert.equal(res.completed_runs, 0);
  assert.equal(res.failed_runs, 2);
  assert.ok(res.runs.every((run) => run.complete === false && run.adapter_failure.kind === 'http' && run.choices.length === 0));
});

test('invalid --num-runs is rejected', async () => {
  const r = await run(['model', scenario, '--model', 'x', '--base-url', 'http://127.0.0.1:9/v1', '-n', 'abc']);
  assert.equal(r.code, 1);
  assert.match(r.out, /num-runs/);
});

test('scripted manual run produces a verdict', async () => {
  const data = await playInkStory(scenario, { choose: async (choices) => choices.length - 1, save: false });
  assert.ok(data.choices.length > 0);
  assert.match(data.verdict, /^[A-Z]+ - /);
});
