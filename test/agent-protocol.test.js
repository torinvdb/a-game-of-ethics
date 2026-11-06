// agoe.agent/v1: external agents driven by benchmark/run/run.mjs over stdio and HTTP, checked
// against the JSON Schemas in schemas/. Offline: reference agents and fixtures run locally.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn, execFileSync } from 'node:child_process';
import http from 'node:http';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { validate, loadSchema } from '../schemas/validate.mjs';
import { checkAgentUrl, isPrivateAddress, parseAgentDecision, splitCommand, RunError } from '../benchmark/run/providers.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const schema = (n) => loadSchema(path.join(root, 'schemas', `${n}.schema.json`));
const S = Object.fromEntries(['agent-start', 'agent-decide', 'agent-end', 'agent-decision', 'agent-ack', 'results-row', 'errors-row']
  .map((n) => [n, schema(n)]));
const ok = (name, value) => assert.deepEqual(validate(S[name], value), [], `${name}: ${JSON.stringify(value).slice(0, 200)}`);
const tmp = (p) => fs.mkdtempSync(path.join(os.tmpdir(), `agoe-${p}-`));
const jsonl = (f) => (fs.existsSync(f) ? fs.readFileSync(f, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l)) : []);
const SCORE = /Ethical Score|Average Per Axis|VERDICT|\((hc|fj|ar|al|lt|it|sp|uc)\)|hard_violations|medical_disruption|recent_decisions/;

function run(args, { timeout = 60000 } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [path.join(root, 'benchmark/run/run.mjs'), '--stage', 'smoke', '--scenarios', 'hostage-holdout', ...args],
      { cwd: root, env: { PATH: process.env.PATH } });
    let out = '';
    child.stdout.on('data', (d) => (out += d));
    child.stderr.on('data', (d) => (out += d));
    const t = setTimeout(() => { child.kill('SIGKILL'); reject(new Error(`runner timed out:\n${out}`)); }, timeout);
    child.on('close', (code) => { clearTimeout(t); resolve({ code, out }); });
  });
}

function fixture(dir, name, body) {
  const f = path.join(dir, `${name}.mjs`);
  fs.writeFileSync(f, `import readline from 'node:readline';
const rl = readline.createInterface({ input: process.stdin });
const say = (o) => process.stdout.write((typeof o === 'string' ? o : JSON.stringify(o)) + '\\n');
rl.on('line', (line) => { const m = JSON.parse(line); if (m.type !== 'decide') return say({ ok: true }); ${body} });\n`);
  return `${JSON.stringify(process.execPath)} ${JSON.stringify(f)}`;
}

function checkTranscript(messages) {
  const byRun = {};
  for (const m of messages) (byRun[m.run_id] ??= []).push(m);
  assert.equal(Object.keys(byRun).length, 2);
  for (const msgs of Object.values(byRun)) {
    assert.equal(msgs[0].type, 'start');
    assert.equal(msgs.at(-1).type, 'end');
    assert.equal(msgs.at(-1).completed, true);
    msgs.forEach((m, i) => {
      ok(`agent-${m.type}`, m);
      if (m.type !== 'decide') return;
      assert.equal(m.step, i - 1);
      assert.deepEqual(m.options.map((o) => o.id), m.options.map((_, k) => k + 1));
      assert.doesNotMatch(m.observation, SCORE);
      assert.doesNotMatch(JSON.stringify(m), /"axes"|"ink_total"|"ink_verdict"/);
    });
  }
}

function checkRows(out, n) {
  const rows = jsonl(path.join(out, 'results.jsonl'));
  assert.equal(rows.length, n);
  for (const r of rows) {
    ok('results-row', r);
    for (const d of r.decisions) assert.equal(d.option_text, d.options[d.original_index]);
    // Memory: the reference agent reports how many earlier decisions it remembers in this run.
    r.decisions.forEach((d, i) => assert.match(d.rationale, new RegExp(`; ${i} earlier decisions in this run\\.$`)));
  }
  return rows;
}

test('schemas: subset checker accepts valid and rejects invalid messages', () => {
  ok('agent-decision', { choice: 2, rationale: 'r' });
  ok('agent-decision', { choice: 1, rationale: 'r', usage: { input_tokens: 3, output_tokens: 4 } });
  ok('agent-decision', { error: 'llm_unavailable' });
  ok('agent-ack', { ok: true });
  assert.ok(validate(S['agent-decision'], { choice: 0 }).length);
  assert.ok(validate(S['agent-decision'], { choice: '2' }).length);
  assert.ok(validate(S['agent-decision'], { choice: 1, error: 'x' }).length);
  assert.ok(validate(S['agent-decision'], { error: 'Has Spaces' }).length);
  assert.ok(validate(S['agent-decide'], { type: 'decide', run_id: 'r', step: 0, observation: 'o', options: [], deadline_ms: 5 }).length);
  assert.ok(validate(S['agent-start'], { type: 'start', protocol: 'agoe.agent/v2', run_id: 'r', scenario: 's', system: '' }).length);
  assert.throws(() => validate({ type: 'string', format: 'uri' }, 'x'), /unsupported schema keyword/);
});

test('decision parsing and URL policy', async () => {
  assert.deepEqual(parseAgentDecision({ choice: 2, rationale: 'r', extra: 1 }, 3), { choice: 2, rationale: 'r', usage: {} });
  const cls = (reply) => { try { parseAgentDecision(reply, 3); } catch (e) { assert.ok(e instanceof RunError); return e.failureClass; } return null; };
  assert.equal(cls({ choice: 4 }), 'schema_invalid');
  assert.equal(cls({ choice: 1.5 }), 'schema_invalid');
  assert.equal(cls([1]), 'schema_invalid');
  assert.equal(cls({ error: 'refusal' }), 'refusal');
  assert.equal(cls({ error: 'llm_down' }), 'agent_error');
  assert.equal(cls({ error: 'Bad Kind!' }), 'schema_invalid');
  assert.deepEqual(splitCommand(`python3 "my agent.py" --x 'a b' c\\ d`), ['python3', 'my agent.py', '--x', 'a b', 'c d']);

  for (const ip of ['127.0.0.1', '10.1.2.3', '172.18.0.2', '192.168.65.2', '::1', 'fd00::1', '::ffff:10.0.0.1']) assert.ok(isPrivateAddress(ip), ip);
  for (const ip of ['8.8.8.8', '172.32.0.1', '169.254.169.254', '2001:db8::1']) assert.ok(!isPrivateAddress(ip), ip);
  const lookup = async (h) => ({ agent: [{ address: '172.18.0.5' }], public: [{ address: '93.184.215.14' }] }[h] ?? (() => { throw Object.assign(new Error('x'), { code: 'ENOTFOUND' }); })());
  const c = (u, o = {}) => checkAgentUrl(u, { lookup, ...o }).then((r) => r.ok);
  assert.equal(await c('https://agents.example.com/v1'), true);
  assert.equal(await c('http://127.0.0.1:8080'), true);
  assert.equal(await c('http://[::1]:8080'), true);
  assert.equal(await c('http://localhost:8080'), true);
  assert.equal(await c('http://agent:8080'), true); // container network name resolving to a private address
  assert.equal(await c('http://public:8080'), false);
  assert.equal(await c('http://8.8.8.8'), false);
  assert.equal(await c('http://8.8.8.8', { allowInsecureHttp: true }), true);
  assert.equal(await c('https://user:pw@agents.example.com'), false);
  assert.equal(await c('file:///etc/passwd'), false);
});

test('command transport: stdio reference agent end to end, then resume', async () => {
  const out = tmp('stdio');
  const log = path.join(out, 'messages.jsonl');
  const args = ['--agent-cmd', `python3 examples/agents/stdio_agent.py --log-messages ${JSON.stringify(log)}`, '--agent-name', 'rule-stdio', '--out', out];
  const first = await run(args);
  assert.equal(first.code, 0, first.out);
  const rows = checkRows(out, 2);
  for (const r of rows) assert.deepEqual(r.agent, { protocol: 'agoe.agent/v1', transport: 'command', name: 'rule-stdio' });
  checkTranscript(jsonl(log));
  const meta = JSON.parse(fs.readFileSync(path.join(out, 'run.json'), 'utf8'));
  assert.equal(meta.provider, 'command');
  assert.equal(meta.agent.protocol, 'agoe.agent/v1');
  assert.equal(fs.readdirSync(path.join(out, 'agent-logs')).length, 2);
  const again = await run(args);
  assert.match(again.out, /^0\/2 cells to run/m);
  fs.rmSync(out, { recursive: true, force: true });
});

test('http transport: reference agent end to end', async () => {
  const out = tmp('http');
  const log = path.join(out, 'messages.jsonl');
  const agent = spawn('python3', [path.join(root, 'examples/agents/http_agent.py'), '--port', '0', '--log-messages', log]);
  try {
    const url = await new Promise((resolve, reject) => {
      agent.stdout.once('data', (d) => resolve(String(d).match(/listening on (\S+)/)[1]));
      agent.once('exit', () => reject(new Error('agent exited')));
    });
    // Replies from the reference agent conform to the reply schemas.
    const post = (r, b) => fetch(`${url}/${r}`, { method: 'POST', body: JSON.stringify(b) }).then((x) => x.json());
    ok('agent-ack', await post('start', { type: 'start', protocol: 'agoe.agent/v1', run_id: 'probe', scenario: 's', system: '' }));
    ok('agent-decision', await post('decide', { type: 'decide', run_id: 'probe', step: 0, observation: 'o',
      options: [{ id: 1, text: 'wait' }, { id: 2, text: 'Report it' }], deadline_ms: 1000 }));
    ok('agent-ack', await post('end', { type: 'end', run_id: 'probe', completed: true }));
    fs.rmSync(log);

    const res = await run(['--agent-url', url, '--agent-name', 'rule-http', '--out', out]);
    assert.equal(res.code, 0, res.out);
    for (const r of checkRows(out, 2)) assert.equal(r.agent.transport, 'http');
    checkTranscript(jsonl(log));
  } finally {
    agent.kill();
    fs.rmSync(out, { recursive: true, force: true });
  }
});

test('http transport: non-2xx is api_error; public plain http is refused', async () => {
  const srv = http.createServer((req, res) => { req.resume(); req.on('end', () => { res.writeHead(500); res.end('{}'); }); });
  await new Promise((r) => srv.listen(0, '127.0.0.1', r));
  const out = tmp('http500');
  try {
    const res = await run(['--agent-url', `http://127.0.0.1:${srv.address().port}`, '--out', out]);
    assert.equal(res.code, 0, res.out);
    const errs = jsonl(path.join(out, 'errors.jsonl'));
    assert.equal(errs.length, 2);
    for (const e of errs) { ok('errors-row', e); assert.equal(e.failure_class, 'api_error'); assert.match(e.detail, /HTTP 500/); }
    const refused = await run(['--agent-url', 'http://8.8.8.8:8080', '--out', out]);
    assert.notEqual(refused.code, 0);
    assert.match(refused.out, /refusing agent URL/);
  } finally {
    srv.close();
    fs.rmSync(out, { recursive: true, force: true });
  }
});

test('command transport failure classes: timeout, crash, bad JSON, out of range, agent error', async () => {
  const dir = tmp('fixtures');
  const cases = {
    timeout: ['/* never replies */', 'timeout'],
    crash: ['process.exit(3);', 'agent_crashed'],
    badjson: ["say('choice: 1');", 'schema_invalid'],
    range: ['say({ choice: m.options.length + 1, rationale: "x" });', 'schema_invalid'],
    agenterr: ["say({ error: 'llm_unavailable' });", 'agent_error'],
  };
  await Promise.all(Object.entries(cases).map(async ([name, [body, cls]]) => {
    const out = path.join(dir, name);
    const t0 = Date.now();
    const res = await run(['--agent-cmd', fixture(dir, name, body), '--agent-timeout-ms', '1500', '--out', out]);
    assert.equal(res.code, 0, res.out);
    assert.equal(jsonl(path.join(out, 'results.jsonl')).length, 0, name);
    const errs = jsonl(path.join(out, 'errors.jsonl'));
    assert.equal(errs.length, 2, name);
    for (const e of errs) {
      ok('errors-row', e);
      assert.equal(e.failure_class, cls, `${name}: ${e.detail}`);
      assert.equal(e.at_decision, 0);
    }
    if (name === 'timeout') assert.ok(Date.now() - t0 < 20000);
  }));

  // Resume: agent_crashed is transient, so a rerun retries the cell (new run_id); schema_invalid is terminal.
  const crashed = path.join(dir, 'crash');
  const rerun = await run(['--agent-cmd', 'python3 examples/agents/stdio_agent.py', '--out', crashed]);
  assert.match(rerun.out, /^2\/2 cells to run/m);
  const rows = checkRows(crashed, 2);
  for (const r of rows) assert.match(r.run_id, /-a1$/);
  const terminal = await run(['--agent-cmd', 'python3 examples/agents/stdio_agent.py', '--out', path.join(dir, 'badjson')]);
  assert.match(terminal.out, /^0\/2 cells to run/m);
  fs.rmSync(dir, { recursive: true, force: true });
});

test('existing mock provider rows still match results-row schema', () => {
  const out = tmp('mock');
  execFileSync(process.execPath, ['benchmark/run/run.mjs', '--provider', 'mock', '--stage', 'smoke', '--scenarios', 'hostage-holdout',
    '--models', 'claude-haiku-5-5', '--out', out], { cwd: root, encoding: 'utf8' });
  const rows = jsonl(path.join(out, 'results.jsonl'));
  assert.equal(rows.length, 2);
  for (const r of rows) { ok('results-row', r); assert.equal(r.run_id, undefined); assert.equal(r.agent, undefined); }
  fs.rmSync(out, { recursive: true, force: true });
});

test('cluster scenario: external agent through the replay bridge without extension changes', async () => {
  const dir = tmp('cluster');
  const ext = path.join(root, 'extensions/time-travel-ethics');
  const gen = path.join(dir, 'stories', 'generated');
  fs.mkdirSync(gen, { recursive: true });
  // A 3-month story keeps the test fast; the frozen E1b stories are 36 months.
  execFileSync('python3', ['-I', '-c', `import json,sys; sys.path.insert(0, sys.argv[1])
from pathlib import Path
from ethicslab.cluster import build
e = Path(sys.argv[1]); d = Path(sys.argv[2])
t = json.loads((e/'examples/cluster-telemetry.synthetic.json').read_text())
s = json.loads((e/'examples/cluster-scenario.seed.json').read_text())
src, man = build(t, dict(s, months=3))
(d/'cluster-pressure.ink').write_text(src); (d/'manifest.json').write_text(json.dumps(man))`, ext, gen]);
  execFileSync(process.execPath, [path.join(ext, 'tools/compile-cluster.mjs'), path.join(gen, 'cluster-pressure.ink'), path.join(gen, 'cluster-pressure.ink.json')]);
  const log = path.join(dir, 'messages.jsonl');
  const out = path.join(dir, 'out');
  const res = await new Promise((resolve) => {
    const child = spawn(process.execPath, [path.join(root, 'benchmark/run/cluster-agent.mjs'), '--stories', path.join(dir, 'stories'),
      '--variants', 'generated', '--out', out, '--agent-name', 'rule',
      '--agent-cmd', `python3 examples/agents/stdio_agent.py --log-messages ${JSON.stringify(log)}`], { cwd: root });
    let o = '';
    child.stdout.on('data', (d) => (o += d));
    child.stderr.on('data', (d) => (o += d));
    child.on('close', (code) => resolve({ code, out: o }));
  });
  assert.equal(res.code, 0, res.out);
  const traj = JSON.parse(fs.readFileSync(path.join(out, 'rule/generated/rep-0.json'), 'utf8'));
  assert.equal(traj.complete, true);
  assert.equal(traj.evidence_class, 'live-model');
  assert.equal(traj.records.length, traj.summary.decision_count);
  const pres = JSON.parse(fs.readFileSync(path.join(out, 'rule/generated/rep-0.presentation.json'), 'utf8'));
  assert.equal(pres.decisions.length, traj.records.length);
  traj.records.forEach((r, i) => assert.equal(r.selected, r.choices[pres.decisions[i].original_index].text));
  const msgs = jsonl(log);
  assert.equal(msgs.length, traj.records.length + 2);
  assert.equal(new Set(msgs.map((m) => m.run_id)).size, 1); // one session for the whole trajectory
  for (const m of msgs) {
    ok(`agent-${m.type}`, m);
    if (m.type === 'decide') assert.doesNotMatch(m.observation, /hard_violations|medical_disruption|exposure_windows|recent_decisions/);
  }
  // Memory persisted across the whole trajectory.
  assert.match(traj.records.at(-1).reason, new RegExp(`; ${traj.records.length - 1} earlier decisions`));
  fs.rmSync(dir, { recursive: true, force: true });
});
