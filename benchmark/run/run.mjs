#!/usr/bin/env node
// Experiment runner: plays frozen Ink scenarios as multi-turn conversations.
//
//   node benchmark/run/run.mjs --config benchmark/experiments/e1-anthropic/config.json \
//        --out benchmark/experiments/e1-anthropic/runs/<stage> [--provider mock|anthropic|openai-compatible]
//        [--stage pilot|full] [--models a,b] [--scenarios x,y] [--reps N] [--concurrency N]
//        [--budget-usd X] [--estimate]
//
// External agents (protocol agoe.agent/v1, docs/AGENT-PROTOCOL.md):
//        --agent-cmd "python3 examples/agents/stdio_agent.py"   (provider "command")
//        --agent-url http://127.0.0.1:8080                      (provider "http")
//        [--agent-name NAME] [--agent-timeout-ms N] [--allow-insecure-http]
//
// Output (append-only, resumable at the (cell, rep) key):
//   results.jsonl  one row per completed scenario run
//   errors.jsonl   one row per failed attempt (failure class, usage if billed)
//   run.json       config hash, scenario hashes, git commit, SDK version, provider
// Failures are never scored as choices.

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { loadStory, readVariables } from '../../src/lib/ink.js';
import { AXES } from '../../src/lib/scoring.js';
import { makeProvider, RunError } from './providers.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', '..');
const argv = process.argv.slice(2);
const arg = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
const flag = (k) => argv.includes(k);

const sha256 = (buf) => crypto.createHash('sha256').update(buf).digest('hex');

// Seeded PRNG (mulberry32) for option permutations.
function rng(seedHex) {
  let a = parseInt(seedHex.slice(0, 8), 16) >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function permutation(n, rand) {
  const p = Array.from({ length: n }, (_, i) => i);
  for (let i = n - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
    [p[i], p[j]] = [p[j], p[i]];
  }
  return p;
}

function priceOf(prices, model, usage) {
  const p = prices[model];
  if (!p || !usage) return 0;
  const inT = usage.input_tokens ?? usage.prompt_tokens ?? 0;
  const outT = usage.output_tokens ?? usage.completion_tokens ?? 0;
  const cr = usage.cache_read_input_tokens ?? 0;
  const cw = usage.cache_creation_input_tokens ?? 0;
  return (inT * p.in + outT * p.out + cr * p.in * 0.1 + cw * p.in * 1.25) / 1e6;
}

function readJsonl(file) {
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l));
}

// Text that would reveal the rubric to an agent. The frozen scenarios print it only after the last
// choice; this guard keeps a future scenario from leaking it mid-story to an external agent.
const SCORE_TEXT = /Ethical Score|Average Per Axis|VERDICT:|\((hc|fj|ar|al|lt|it|sp|uc)\):\s*-?\d/;

// One scenario run. Returns a results row or throws RunError (with partial usage).
// External agents get a session (start ... end) around the story; model providers do not.
async function playOnce({ provider, cell, rep, scenarioFile, system, settings, prices, runId }) {
  const session = provider.openRun ? await provider.openRun({ runId, scenario: cell.scenario.id, system }) : null;
  let completed = false;
  try {
    const row = await playStory({ provider, session, cell, scenarioFile, system, settings, prices });
    completed = true;
    return row;
  } finally {
    if (session) await session.close({ completed });
  }
}

async function playStory({ provider, session, cell, scenarioFile, system, settings, prices }) {
  const story = loadStory(scenarioFile);
  const rand = rng(cell.seed);
  const messages = [];
  const decisions = [];
  const usageTotal = { input_tokens: 0, output_tokens: 0, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 };
  let cost = 0;
  let pending = '';
  const add = (u) => {
    for (const k of Object.keys(usageTotal)) usageTotal[k] += u?.[k] ?? 0;
    cost += priceOf(prices, cell.model, u);
  };
  for (let step = 0; step < settings.max_decisions; step++) {
    pending += story.ContinueMaximally();
    const choices = story.currentChoices;
    if (!choices.length) break;
    const order = permutation(choices.length, rand); // presented position k shows original option order[k]
    const lines = order.map((orig, k) => `${k + 1}. ${choices[orig].text}`);
    const observation = pending.trim();
    messages.push({ role: 'user', content: `${pending.trim()}\n\nOptions:\n${lines.join('\n')}` });
    pending = '';
    let out;
    try {
      if (session) {
        if (SCORE_TEXT.test(observation)) throw new RunError('harness_error', 'score text in observation; not sent to agent');
        out = await session.decide({ step, observation, options: order.map((orig, k) => ({ id: k + 1, text: choices[orig].text })) });
      } else {
        out = await provider.decide({ system, messages, numChoices: choices.length, model: cell.model, settings });
      }
    } catch (error) {
      if (error instanceof RunError) {
        add(error.usage);
        error.atDecision = step;
        error.usageTotal = usageTotal;
        error.cost = cost;
      }
      throw error;
    }
    add(out.usage);
    const presented = out.choice - 1;
    const original = order[presented];
    decisions.push({ step, n_options: choices.length, options: choices.map((c) => c.text), order, presented_index: presented, original_index: original,
      option_text: choices[original].text, rationale: out.rationale.slice(0, 2000), stop_reason: out.stopReason,
      served_model: out.servedModel ?? null });
    messages.push({ role: 'assistant', content: out.assistantContent });
    story.ChooseChoiceIndex(original);
  }
  pending += story.canContinue ? story.ContinueMaximally() : '';
  if (story.currentChoices.length) throw new RunError('max_decisions', `exceeded ${settings.max_decisions}`, { usageTotal, cost });
  const vars = readVariables(story);
  const axes = Object.fromEntries(AXES.map((a) => [a, typeof vars[a] === 'number' ? vars[a] : 0]));
  const verdictLine = (pending.match(/VERDICT:\s*"?([A-Z][A-Z ]+?)\b(?:\s*[-.]|"|$)/m) || [])[1] ?? null;
  return { axes, ink_total: vars.total ?? null, ink_average: vars.average ?? null, ink_verdict: verdictLine,
    decisions, usage: usageTotal, cost_usd: Number(cost.toFixed(6)) };
}

async function main() {
  const configPath = path.resolve(arg('--config', 'benchmark/experiments/e1-anthropic/config.json'));
  const cfgBytes = fs.readFileSync(configPath);
  const cfg = JSON.parse(cfgBytes);
  const stage = arg('--stage', 'pilot');
  const agentCmd = arg('--agent-cmd');
  const agentUrl = arg('--agent-url');
  if (agentCmd && agentUrl) throw new Error('use either --agent-cmd or --agent-url, not both');
  const providerName = agentCmd ? 'command' : agentUrl ? 'http' : arg('--provider', cfg.provider);
  const isAgent = providerName === 'command' || providerName === 'http';
  if (isAgent && !agentCmd && !agentUrl) throw new Error(`--provider ${providerName} needs --agent-cmd or --agent-url`);
  const agentName = arg('--agent-name', 'agent');
  if (!/^[A-Za-z0-9._:-]{1,64}$/.test(agentName)) throw new Error('--agent-name must match ^[A-Za-z0-9._:-]{1,64}$');
  const agentTimeoutMs = Number(arg('--agent-timeout-ms', 60000));
  if (!(agentTimeoutMs > 0)) throw new Error('--agent-timeout-ms must be a positive number');
  const out = path.resolve(arg('--out', path.join(path.dirname(configPath), 'runs', `${stage}-${providerName}`)));
  fs.mkdirSync(out, { recursive: true });
  const reps = Number(arg('--reps', cfg.stages[stage].reps));
  // An external agent is one "model" in the cell grid; its name is the model id in keys and rows.
  const models = isAgent ? [agentName] : (arg('--models') || cfg.models.map((m) => m.id).join(',')).split(',').filter(Boolean);
  if (!models.length || models.some((m) => /REPLACE|^<|>$/.test(m))) throw new Error('no models selected: fill config.models or pass --models');
  const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, cfg.benchmark_manifest), 'utf8'));
  const wanted = arg('--scenarios') ? arg('--scenarios').split(',') : cfg.scenarios;
  const scenarios = manifest.scenarios.filter((s) => wanted.includes(s.id));
  // Frozen inputs: refuse to run against drifted scenario files.
  for (const s of scenarios) {
    const h = sha256(fs.readFileSync(path.join(ROOT, s.path)));
    if (h !== s.sha256) throw new Error(`scenario drift: ${s.id} ${h.slice(0, 12)} != manifest ${s.sha256.slice(0, 12)}`);
  }
  const prices = isAgent ? {} : Object.fromEntries(cfg.models.map((m) => [m.id, m.price_per_mtok]));
  const budget = Number(arg('--budget-usd', cfg.stages[stage].budget_usd));
  const concurrency = Number(arg('--concurrency', cfg.concurrency));

  const cells = [];
  for (const model of models) for (const s of scenarios) for (const framing of cfg.framings) for (let rep = 0; rep < reps; rep++) {
    const key = `${model}|${s.id}|${framing.id}|${rep}`;
    cells.push({ key, model, scenario: s, framing, rep, seed: sha256(`${cfg.experiment_id}|${key}`) });
  }

  const resultsFile = path.join(out, 'results.jsonl');
  const errorsFile = path.join(out, 'errors.jsonl');
  // Terminal failure classes are outcomes of the cell (recorded once, not retried);
  // transient ones (api_error, timeout, harness_error, agent_crashed, agent_error) are retried
  // up to max_attempts on a later invocation (resume).
  const TERMINAL = new Set(['refusal', 'truncated', 'schema_invalid', 'served_model_mismatch', 'max_decisions']);
  const done = new Set(readJsonl(resultsFile).map((r) => r.key));
  const attempts = {};
  for (const e of readJsonl(errorsFile)) {
    attempts[e.key] = (attempts[e.key] || 0) + 1;
    if (TERMINAL.has(e.failure_class) || attempts[e.key] >= cfg.settings.max_attempts) done.add(e.key);
  }
  let spent = readJsonl(resultsFile).reduce((a, r) => a + r.cost_usd, 0) + readJsonl(errorsFile).reduce((a, r) => a + (r.cost_usd || 0), 0);
  const todo = cells.filter((c) => !done.has(c.key));

  let git = null;
  try { git = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); } catch { /* not a checkout */ }
  const agentProvider = isAgent
    ? makeProvider(providerName, { cmd: agentCmd, url: agentUrl, timeoutMs: agentTimeoutMs, cwd: process.cwd(),
      logDir: path.join(out, 'agent-logs'), allowInsecureHttp: flag('--allow-insecure-http') })
    : null;
  const sdkVersion = JSON.parse(fs.readFileSync(path.join(ROOT, 'node_modules/@anthropic-ai/sdk/package.json'), 'utf8')).version;
  fs.writeFileSync(path.join(out, 'run.json'), JSON.stringify({ experiment_id: cfg.experiment_id, stage, provider: providerName,
    config_sha256: sha256(cfgBytes), git_commit: git, anthropic_sdk: sdkVersion, node: process.version,
    scenarios: scenarios.map((s) => ({ id: s.id, sha256: s.sha256, split: s.split })), models, reps,
    cells_total: cells.length, ...(isAgent ? { agent: { ...agentProvider.agent, name: agentName, timeout_ms: agentTimeoutMs } } : {}),
    started_at: new Date().toISOString() }, null, 1) + '\n');

  if (flag('--estimate')) {
    console.log(JSON.stringify({ cells: cells.length, remaining: todo.length, note: 'run with --provider mock to measure tokens, then scale' }));
    return;
  }
  if (providerName === 'anthropic' && !process.env.ANTHROPIC_API_KEY && !process.env.ANTHROPIC_AUTH_TOKEN) {
    console.error('Set ANTHROPIC_API_KEY (or use an ant auth profile) before a live run.');
  }
  const provider = agentProvider ?? makeProvider(providerName, { seed: 1 });
  if (provider.init) await provider.init();
  console.log(`${todo.length}/${cells.length} cells to run · provider ${providerName} · budget $${budget} · spent $${spent.toFixed(4)}`);

  let stop = false;
  let idx = 0;
  const worker = async () => {
    while (!stop && idx < todo.length) {
      const cell = todo[idx++];
      const t0 = Date.now();
      const system = [cfg.prompts.system_common, cell.framing.system_prefix].join('\n\n');
      // Agent runs carry a run id (one per attempt) that the agent uses to key its memory.
      const runId = isAgent ? `${cell.seed.slice(0, 16)}-a${attempts[cell.key] || 0}` : undefined;
      const agentFields = isAgent ? { run_id: runId, agent: { protocol: provider.agent.protocol, transport: provider.agent.transport, name: agentName } } : {};
      try {
        const res = await playOnce({ provider, cell, rep: cell.rep, scenarioFile: path.join(ROOT, cell.scenario.path), system,
          settings: cfg.settings, prices, runId });
        spent += res.cost_usd;
        fs.appendFileSync(resultsFile, JSON.stringify({ key: cell.key, model: cell.model, scenario: cell.scenario.id,
          split: cell.scenario.split, framing: cell.framing.id, rep: cell.rep, seed: cell.seed, ...agentFields, ...res,
          latency_s: (Date.now() - t0) / 1000 }) + '\n');
      } catch (error) {
        const fc = error instanceof RunError ? error.failureClass : 'harness_error';
        spent += error.cost || 0;
        fs.appendFileSync(errorsFile, JSON.stringify({ key: cell.key, model: cell.model, scenario: cell.scenario.id,
          framing: cell.framing.id, rep: cell.rep, ...(isAgent ? { run_id: runId } : {}), failure_class: fc, detail: String(error.detail ?? error.message).slice(0, 300),
          at_decision: error.atDecision ?? null, usage: error.usageTotal ?? null, cost_usd: error.cost || 0, at: new Date().toISOString() }) + '\n');
      }
      if (spent > budget) {
        stop = true;
        console.error(`budget cap reached: $${spent.toFixed(4)} > $${budget}; stopping (resume with a higher --budget-usd)`);
      }
    }
  };
  await Promise.all(Array.from({ length: Math.max(1, concurrency) }, worker));
  const rows = readJsonl(resultsFile);
  const errs = readJsonl(errorsFile);
  console.log(JSON.stringify({ completed: rows.length, errors: errs.length, spent_usd: Number(spent.toFixed(4)), out }));
}

main().catch((e) => { console.error(e.message); process.exit(1); });
