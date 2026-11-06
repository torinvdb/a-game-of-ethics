// Ashgrove Reach demo server: static files, recorded runs, and live Claude runs of Blackout Ledger.
//
//   node --env-file=.env talks/three-years-in-thirty-minutes/demo/city/server.mjs [--port 8787]
//   open http://127.0.0.1:8787
//
// Without ANTHROPIC_API_KEY the page still plays every recorded run. Live runs use the benchmark's
// own Anthropic provider and the E1 config's prompts and settings, so a live request is the same
// request the E1a experiment sent. Every live run is saved to recordings/ and appears in the
// library as a recording. Spend is capped by DEMO_BUDGET_USD (default 15), kept in
// recordings/.spend.json across restarts. The server binds to 127.0.0.1 only.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { loadStory, readVariables } from '../../../../src/lib/ink.js';
import { anthropicProvider, RunError } from '../../../../benchmark/run/providers.mjs';
import { stripScores } from './bake.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const ROOT = path.resolve(HERE, '../../../..');
const FONTS = path.resolve(HERE, '../../assets/fonts');
const REC = path.join(HERE, 'recordings');
const CFG = JSON.parse(fs.readFileSync(path.join(ROOT, 'benchmark/experiments/e1-anthropic/config.json'), 'utf8'));
const PRICES = Object.fromEntries(CFG.models.map((m) => [m.id, m.price_per_mtok]));
const BUDGET = Number(process.env.DEMO_BUDGET_USD ?? 15);
const PORT = Number(process.argv.includes('--port') ? process.argv[process.argv.indexOf('--port') + 1] : 8787);
const INK = path.join(ROOT, 'scenarios/core/blackout-ledger.ink');
const AXES = ['hc', 'fj', 'ar', 'al', 'lt', 'it', 'sp', 'uc'];
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.ttf': 'font/ttf', '.png': 'image/png' };

fs.mkdirSync(REC, { recursive: true });
const spendFile = path.join(REC, '.spend.json');
const spent = () => (fs.existsSync(spendFile) ? JSON.parse(fs.readFileSync(spendFile, 'utf8')).spent_usd : 0);
const addSpend = (c) => fs.writeFileSync(spendFile, JSON.stringify({ spent_usd: spent() + c, budget_usd: BUDGET }));
const cost = (model, u = {}) => {
  const p = PRICES[model];
  return ((u.input_tokens ?? 0) * p.in + (u.output_tokens ?? 0) * p.out + (u.cache_creation_input_tokens ?? 0) * p.in * 1.25
    + (u.cache_read_input_tokens ?? 0) * p.in * 0.1) / 1e6;
};

// Same PRNG and shuffle as benchmark/run/run.mjs.
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

let busy = false;
const provider = process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN ? anthropicProvider() : null;

async function liveBlackout(res, model, framingId) {
  const framing = CFG.framings.find((f) => f.id === framingId) ?? CFG.framings[0];
  const system = [CFG.prompts.system_common, framing.system_prefix].join('\n\n');
  const seed = crypto.randomBytes(16).toString('hex');
  const rand = rng(seed);
  const story = loadStory(INK);
  const events = [];
  const send = (e) => { events.push(e); res.write(`data: ${JSON.stringify(e)}\n\n`); };
  const at = new Date().toISOString();
  send({ t: 'start', scenario: 'blackout-ledger', model, framing: framing.id, live: true, seed, at });
  const messages = [];
  let total = 0;
  try {
    for (let step = 0; step < CFG.settings.max_decisions; step++) {
      const text = story.ContinueMaximally();
      const choices = story.currentChoices;
      if (!choices.length) {
        const vars = readVariables(story);
        send({ t: 'text', step, text: stripScores(text) });
        const verdict = (text.match(/VERDICT:\s*"?([A-Z][A-Z ]+?)\b(?:\s*[-.]|"|$)/m) || [])[1] ?? null;
        send({ t: 'end', axes: Object.fromEntries(AXES.map((a) => [a, vars[a] ?? 0])), total: vars.total, average: vars.average, verdict, cost_usd: total });
        break;
      }
      const order = permutation(choices.length, rand);
      send({ t: 'text', step, text: text.trim() });
      send({ t: 'options', step, options: choices.map((c) => c.text), order });
      messages.push({ role: 'user', content: `${text.trim()}\n\nOptions:\n${order.map((o, k) => `${k + 1}. ${choices[o].text}`).join('\n')}` });
      send({ t: 'thinking', step });
      const t0 = Date.now();
      let out;
      try {
        out = await provider.decide({ system, messages, numChoices: choices.length, model, settings: CFG.settings });
      } catch (error) {
        if (error instanceof RunError) { const c = cost(model, error.usage); total += c; addSpend(c); }
        throw error;
      }
      const c = cost(model, out.usage);
      total += c;
      addSpend(c);
      const original = order[out.choice - 1];
      send({ t: 'decision', step, original, presented: out.choice - 1, text: choices[original].text, rationale: out.rationale,
        latency_s: (Date.now() - t0) / 1000, served_model: out.servedModel, cost_usd: c });
      messages.push({ role: 'assistant', content: out.assistantContent });
      story.ChooseChoiceIndex(original);
    }
  } catch (error) {
    // Execution failures are shown as failures, never as a choice.
    send({ t: 'error', kind: error.failureClass ?? 'error', detail: String(error.detail ?? error.message).slice(0, 200) });
  }
  const id = `${at.replace(/[:.]/g, '-')}-${model}`;
  fs.writeFileSync(path.join(REC, `${id}.json`), JSON.stringify(events));
  res.write('event: done\ndata: {}\n\n');
  res.end();
}

function library() {
  const lib = JSON.parse(fs.readFileSync(path.join(HERE, 'data/library.json'), 'utf8'));
  for (const f of fs.readdirSync(REC).filter((x) => x.endsWith('.json') && !x.startsWith('.')).sort().reverse()) {
    const first = JSON.parse(fs.readFileSync(path.join(REC, f), 'utf8'))[0];
    lib.blackout.unshift({ id: `rec-${f.slice(0, -5)}`, model: first.model, recordedLive: first.at, file: `recordings/${f}` });
  }
  lib.live = { available: Boolean(provider), spent_usd: spent(), budget_usd: BUDGET, models: CFG.models.map((m) => m.id) };
  return lib;
}

function serveFile(res, file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end('not found'); return; }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] ?? 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(file).pipe(res);
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, 'http://127.0.0.1');
  if (url.pathname === '/api/library') {
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' });
    res.end(JSON.stringify(library()));
    return;
  }
  if (url.pathname === '/api/live/blackout') {
    const model = url.searchParams.get('model');
    const why = !provider ? 'no ANTHROPIC_API_KEY: start the server with --env-file=.env'
      : !PRICES[model] ? 'unknown model' : busy ? 'a live run is already in progress'
      : spent() >= BUDGET ? `demo budget of $${BUDGET} is used up (recordings/.spend.json)` : null;
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-store', Connection: 'keep-alive' });
    if (why) { res.write(`data: ${JSON.stringify({ t: 'error', kind: 'unavailable', detail: why })}\n\nevent: done\ndata: {}\n\n`); res.end(); return; }
    busy = true;
    try { await liveBlackout(res, model, url.searchParams.get('framing') ?? 'deployment'); } finally { busy = false; }
    return;
  }
  // Static: the page, baked data, recordings and the talk's fonts. No path escapes these roots.
  const rel = decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname);
  const [rootDir, sub] = rel.startsWith('/fonts/') ? [FONTS, rel.slice(7)] : [HERE, rel.slice(1)];
  const file = path.resolve(rootDir, sub);
  if (!file.startsWith(rootDir + path.sep) || /(^|\/)\./.test(sub) || file.endsWith('.mjs')) { res.writeHead(403); res.end(); return; }
  serveFile(res, file);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`Ashgrove Reach demo on http://127.0.0.1:${PORT}  live: ${provider ? 'on' : 'off (no API key)'}  spent $${spent().toFixed(4)} of $${BUDGET}`);
});
