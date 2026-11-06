// Provider adapters for benchmark/run/run.mjs.
// Each adapter: decide({system, messages, numChoices, model, settings}) ->
//   { choice (1-based), rationale, assistantContent, usage, servedModel, stopReason }
// or throws RunError with a failure class. A failure is never converted into a choice.

import Anthropic from '@anthropic-ai/sdk';
import { spawn } from 'node:child_process';
import dns from 'node:dns/promises';
import fs from 'node:fs';
import net from 'node:net';
import path from 'node:path';
import { requestCompletion, resolveAdapterConfig, parseChoice } from '../../src/lib/llm.js';

export class RunError extends Error {
  constructor(failureClass, detail, extra = {}) {
    super(`${failureClass}: ${detail}`);
    // refusal | truncated | schema_invalid | api_error | timeout | served_model_mismatch
    // | agent_crashed | agent_error (external agents, see docs/AGENT-PROTOCOL.md)
    this.failureClass = failureClass;
    this.detail = detail;
    Object.assign(this, extra);
  }
}

export function choiceSchema(numChoices) {
  return {
    type: 'object',
    properties: {
      choice: { type: 'integer', enum: Array.from({ length: numChoices }, (_, i) => i + 1) },
      rationale: { type: 'string' },
    },
    required: ['choice', 'rationale'],
    additionalProperties: false,
  };
}

// ---------------------------------------------------------------- Anthropic (official SDK)
// Sampling parameters are not sent (current models reject temperature/top_p/top_k).
// Server-side fallbacks are deliberately NOT enabled: a fallback would change the model under test.
export function anthropicProvider({ timeoutMs = 120000, maxRetries = 4 } = {}) {
  const client = new Anthropic({ timeout: timeoutMs, maxRetries });
  return {
    name: 'anthropic',
    async decide({ system, messages, numChoices, model, settings }) {
      let response;
      try {
        response = await client.messages.create({
          model,
          max_tokens: settings.max_tokens,
          system,
          messages,
          thinking: { type: 'adaptive' },
          output_config: { effort: settings.effort, format: { type: 'json_schema', schema: choiceSchema(numChoices) } },
          cache_control: { type: 'ephemeral' },
        });
      } catch (error) {
        if (error instanceof Anthropic.APIConnectionTimeoutError) throw new RunError('timeout', 'request timed out');
        if (error instanceof Anthropic.APIError) throw new RunError('api_error', `HTTP ${error.status ?? '?'} ${error.name}`);
        throw new RunError('api_error', error.name || 'unknown');
      }
      const usage = response.usage;
      const base = { usage, servedModel: response.model, stopReason: response.stop_reason };
      if (response.model !== model) throw new RunError('served_model_mismatch', `${response.model} != ${model}`, base);
      if (response.stop_reason === 'refusal') {
        throw new RunError('refusal', response.stop_details?.category ?? 'uncategorised', base);
      }
      if (response.stop_reason === 'max_tokens') throw new RunError('truncated', 'hit max_tokens', base);
      const text = response.content.filter((b) => b.type === 'text').map((b) => b.text).join('');
      let parsed;
      try {
        parsed = JSON.parse(text);
      } catch {
        throw new RunError('schema_invalid', 'non-JSON text', base);
      }
      if (!Number.isInteger(parsed.choice) || parsed.choice < 1 || parsed.choice > numChoices) {
        throw new RunError('schema_invalid', 'choice out of range', base);
      }
      // Full content (incl. thinking blocks) goes back unchanged on the next turn.
      return { choice: parsed.choice, rationale: String(parsed.rationale ?? ''), assistantContent: response.content, ...base };
    },
  };
}

// ---------------------------------------------------------------- OpenAI-compatible (GPT, open-weights servers)
// Uses the existing redacting/retrying client in src/lib/llm.js. JSON is requested in the
// prompt; parse failures are recorded as schema_invalid, never as a choice.
export function openaiCompatibleProvider(options = {}) {
  const config = resolveAdapterConfig(options);
  return {
    name: 'openai-compatible',
    async decide({ system, messages, numChoices, model }) {
      const flat = [{ role: 'system', content: system }, ...messages.map((m) => ({
        role: m.role,
        content: typeof m.content === 'string' ? m.content
          : m.content.filter((b) => b.type === 'text').map((b) => b.text).join(''),
      }))];
      let reply;
      try {
        reply = await requestCompletion(config, { model, messages: flat });
      } catch (error) {
        throw new RunError(error.kind === 'timeout' ? 'timeout' : 'api_error', error.kind || error.name);
      }
      if (reply.refusal) throw new RunError('refusal', 'provider refusal field');
      if (reply.finishReason === 'length') throw new RunError('truncated', 'finish_reason=length');
      const content = reply.content ?? '';
      let choice = null;
      let rationale = '';
      try {
        const j = JSON.parse(content.replace(/^```(json)?|```$/g, '').trim());
        choice = j.choice; rationale = String(j.rationale ?? '');
      } catch {
        const p = parseChoice(content, numChoices);
        if (p.ok) choice = p.choice;
      }
      if (!Number.isInteger(choice) || choice < 1 || choice > numChoices) throw new RunError('schema_invalid', 'no valid choice');
      return { choice, rationale, assistantContent: content, usage: reply.usage ?? {}, servedModel: reply.servedModel ?? model, stopReason: reply.finishReason ?? null };
    },
  };
}

// ---------------------------------------------------------------- Mock (offline dry runs)
// Deterministic pseudo-model: no network. Token usage is estimated from characters so the
// cost estimator can be calibrated before any paid call.
export function mockProvider({ seed = 1, refuseEvery = 0 } = {}) {
  let n = 0;
  return {
    name: 'mock',
    async decide({ system, messages, numChoices, model }) {
      n++;
      const chars = system.length + JSON.stringify(messages).length;
      const usage = { input_tokens: Math.ceil(chars / 3.6), output_tokens: 420, cache_read_input_tokens: 0, cache_creation_input_tokens: 0 };
      if (refuseEvery && n % refuseEvery === 0) throw new RunError('refusal', 'mock', { usage, servedModel: model, stopReason: 'refusal' });
      const h = [...`${seed}:${model}:${chars}`].reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 7);
      const choice = 1 + (h % numChoices);
      const text = JSON.stringify({ choice, rationale: 'mock rationale' });
      return { choice, rationale: 'mock rationale', assistantContent: [{ type: 'text', text }], usage, servedModel: model, stopReason: 'end_turn' };
    },
  };
}

export function makeProvider(name, opts = {}) {
  if (name === 'anthropic') return anthropicProvider(opts);
  if (name === 'openai-compatible') return openaiCompatibleProvider(opts);
  if (name === 'mock') return mockProvider(opts);
  if (name === 'command') return commandAgentProvider(opts);
  if (name === 'http') return httpAgentProvider(opts);
  throw new Error(`unknown provider ${name}`);
}

// ---------------------------------------------------------------- External agents (agoe.agent/v1)
// Stateful adapters for agents built with any framework. Unlike the model adapters above, an
// agent adapter exposes openRun({runId, scenario, system}) -> session, and the session receives
// only the story text since the last decision plus the presented options. The agent keeps its own
// memory between decides. Scores, axis values and verdicts are never sent. See docs/AGENT-PROTOCOL.md.

export const AGENT_PROTOCOL = 'agoe.agent/v1';
const MAX_MESSAGE_BYTES = 1024 * 1024;
const MAX_LOG_BYTES = 1024 * 1024;
const ERROR_KIND = /^[a-z][a-z0-9_]{0,39}$/;

// Split a command line into argv without a shell: whitespace separates words, single and double
// quotes group, backslash escapes the next character outside single quotes.
export function splitCommand(cmd) {
  const out = [];
  let cur = '';
  let quote = null;
  let has = false;
  for (let i = 0; i < cmd.length; i++) {
    const c = cmd[i];
    if (quote === "'") { if (c === "'") quote = null; else cur += c; continue; }
    if (c === '\\' && i + 1 < cmd.length) { cur += cmd[++i]; has = true; continue; }
    if (quote === '"') { if (c === '"') quote = null; else cur += c; continue; }
    if (c === '"' || c === "'") { quote = c; has = true; continue; }
    if (/\s/.test(c)) { if (has) { out.push(cur); cur = ''; has = false; } continue; }
    cur += c; has = true;
  }
  if (quote) throw new Error('unterminated quote in agent command');
  if (has) out.push(cur);
  if (!out.length) throw new Error('empty agent command');
  return out;
}

// Validate an agent reply to a decide message. Returns {choice, rationale, usage} or throws RunError.
export function parseAgentDecision(reply, numOptions) {
  if (!reply || typeof reply !== 'object' || Array.isArray(reply)) throw new RunError('schema_invalid', 'reply is not a JSON object');
  if ('error' in reply) {
    const kind = typeof reply.error === 'string' && ERROR_KIND.test(reply.error) ? reply.error : null;
    if (!kind) throw new RunError('schema_invalid', 'error kind must match ^[a-z][a-z0-9_]{0,39}$');
    if (kind === 'refusal') throw new RunError('refusal', 'agent reported refusal');
    throw new RunError('agent_error', kind);
  }
  if (!Number.isInteger(reply.choice)) throw new RunError('schema_invalid', 'choice is not an integer');
  if (reply.choice < 1 || reply.choice > numOptions) throw new RunError('schema_invalid', `choice ${reply.choice} out of range 1..${numOptions}`);
  if (reply.rationale !== undefined && typeof reply.rationale !== 'string') throw new RunError('schema_invalid', 'rationale is not a string');
  let usage = {};
  if (reply.usage && typeof reply.usage === 'object') {
    for (const k of ['input_tokens', 'output_tokens']) if (Number.isInteger(reply.usage[k]) && reply.usage[k] >= 0) usage[k] = reply.usage[k];
  }
  return { choice: reply.choice, rationale: reply.rationale ?? '', usage };
}

function checkAck(reply, phase) {
  if (!reply || typeof reply !== 'object' || Array.isArray(reply)) throw new RunError('schema_invalid', `${phase}: reply is not a JSON object`);
  if (reply.ok === true) return;
  if (typeof reply.error === 'string' && ERROR_KIND.test(reply.error)) throw new RunError('agent_error', `${phase}: ${reply.error}`);
  throw new RunError('schema_invalid', `${phase}: expected {"ok":true}`);
}

function sessionFor(runId, timeoutMs, request, shutdown) {
  return {
    async decide({ step, observation, options }) {
      const reply = await request({ type: 'decide', run_id: runId, step, observation, options, deadline_ms: timeoutMs });
      const d = parseAgentDecision(reply, options.length);
      return { ...d, assistantContent: JSON.stringify({ choice: d.choice, rationale: d.rationale }), servedModel: null, stopReason: null };
    },
    // Best effort: a failed end message does not change the outcome of a completed run.
    async close({ completed }) {
      try { await request({ type: 'end', run_id: runId, completed: Boolean(completed) }); } catch { /* recorded nowhere: run outcome is already fixed */ }
      await shutdown();
    },
  };
}

// ---- command transport: one long-lived process per run, newline-delimited JSON on stdin/stdout.
export function commandAgentProvider({ cmd, cwd = process.cwd(), env = process.env, logDir = null, timeoutMs = 60000 } = {}) {
  const argv = splitCommand(cmd);
  return {
    name: 'command',
    agent: { protocol: AGENT_PROTOCOL, transport: 'command', cmd },
    async openRun({ runId, scenario, system }) {
      const child = spawn(argv[0], argv.slice(1), { cwd, env, stdio: ['pipe', 'pipe', 'pipe'] });
      let log = null;
      let logged = 0;
      if (logDir) {
        fs.mkdirSync(logDir, { recursive: true });
        log = fs.createWriteStream(path.join(logDir, `${runId.replace(/[^A-Za-z0-9._-]/g, '_')}.stderr.log`));
      }
      child.stderr.on('data', (d) => {
        if (!log || logged >= MAX_LOG_BYTES) return;
        const chunk = d.subarray(0, MAX_LOG_BYTES - logged);
        logged += chunk.length;
        log.write(chunk);
        if (logged >= MAX_LOG_BYTES) log.write('\n[agoe: stderr log truncated]\n');
      });
      let buf = '';
      const lines = [];
      let waiter = null;
      let closed = null; // {detail} once stdout closed or the process failed to spawn
      let overflow = false;
      const wake = () => { if (waiter) { const w = waiter; waiter = null; w(); } };
      child.stdout.setEncoding('utf8');
      child.stdout.on('data', (d) => {
        buf += d;
        let i;
        while ((i = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, i).trim();
          buf = buf.slice(i + 1);
          if (line) lines.push(line);
        }
        if (buf.length > MAX_MESSAGE_BYTES) { overflow = true; child.kill('SIGKILL'); }
        wake();
      });
      child.on('error', (e) => { closed = { detail: `spawn failed: ${e.code || e.message}` }; wake(); });
      child.on('close', (code, signal) => { closed ??= { detail: `exited code=${code} signal=${signal}` }; wake(); });
      child.stdin.on('error', () => { /* EPIPE after a crash is reported through 'close' */ });

      const nextLine = () => new Promise((resolve, reject) => {
        const timer = setTimeout(() => { waiter = null; child.kill('SIGKILL'); reject(new RunError('timeout', `no reply within ${timeoutMs} ms`)); }, timeoutMs);
        const check = () => {
          if (overflow) { clearTimeout(timer); return reject(new RunError('schema_invalid', 'reply line exceeds 1 MiB')); }
          if (lines.length) { clearTimeout(timer); return resolve(lines.shift()); }
          if (closed) { clearTimeout(timer); return reject(new RunError('agent_crashed', closed.detail)); }
          waiter = check;
        };
        check();
      });
      const request = async (msg) => {
        if (closed) throw new RunError('agent_crashed', closed.detail);
        child.stdin.write(JSON.stringify(msg) + '\n');
        const line = await nextLine();
        try { return JSON.parse(line); } catch { throw new RunError('schema_invalid', 'reply is not valid JSON'); }
      };
      const shutdown = async () => {
        child.stdin.end();
        if (!closed) {
          await new Promise((resolve) => {
            const t = setTimeout(() => { child.kill('SIGKILL'); resolve(); }, 2000);
            child.once('close', () => { clearTimeout(t); resolve(); });
            if (closed) { clearTimeout(t); resolve(); }
          });
        }
        if (log) await new Promise((resolve) => log.end(resolve));
      };
      try {
        checkAck(await request({ type: 'start', protocol: AGENT_PROTOCOL, run_id: runId, scenario, system }), 'start');
      } catch (error) {
        child.kill('SIGKILL');
        await shutdown();
        throw error;
      }
      return sessionFor(runId, timeoutMs, request, shutdown);
    },
  };
}

// ---- http transport: POST {base}/start, {base}/decide, {base}/end.
export function isPrivateAddress(ip) {
  let a = ip.toLowerCase().replace(/^\[|\]$/g, '');
  const mapped = a.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/);
  if (mapped) a = mapped[1];
  if (net.isIPv4(a)) {
    const [p, q] = a.split('.').map(Number);
    return p === 127 || p === 10 || (p === 172 && q >= 16 && q <= 31) || (p === 192 && q === 168);
  }
  if (net.isIPv6(a)) return a === '::1' || /^f[cd][0-9a-f]{2}:/.test(a);
  return false;
}

// https to any host; plain http only to loopback or private (RFC 1918 / ULA) addresses, which
// covers localhost and container networks. --allow-insecure-http lifts the restriction.
export async function checkAgentUrl(raw, { allowInsecureHttp = false, lookup = dns.lookup } = {}) {
  let u;
  try { u = new URL(raw); } catch { return { ok: false, reason: 'not a valid URL' }; }
  if (u.username || u.password) return { ok: false, reason: 'credentials in the URL are not accepted; set AGOE_AGENT_TOKEN instead' };
  if (u.protocol === 'https:') return { ok: true };
  if (u.protocol !== 'http:') return { ok: false, reason: `unsupported scheme ${u.protocol}` };
  if (allowInsecureHttp) return { ok: true };
  const host = u.hostname.replace(/^\[|\]$/g, '');
  if (net.isIP(host)) return isPrivateAddress(host) ? { ok: true } : { ok: false, reason: `plain http to public address ${host}` };
  if (host === 'localhost' || host.endsWith('.localhost')) return { ok: true };
  let addrs;
  try { addrs = await lookup(host, { all: true }); } catch (e) { return { ok: false, reason: `cannot resolve ${host}: ${e.code || e.message}` }; }
  if (addrs.length && addrs.every((x) => isPrivateAddress(x.address))) return { ok: true };
  return { ok: false, reason: `plain http to ${host}, which resolves to a non-private address` };
}

export function httpAgentProvider({ url, timeoutMs = 60000, allowInsecureHttp = false, token = process.env.AGOE_AGENT_TOKEN } = {}) {
  const base = url.replace(/\/+$/, '');
  const post = async (route, body) => {
    let res;
    try {
      res = await fetch(`${base}/${route}`, {
        method: 'POST',
        redirect: 'manual',
        headers: { 'content-type': 'application/json', ...(token ? { authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch (e) {
      if (e.name === 'TimeoutError' || e.name === 'AbortError') throw new RunError('timeout', `no reply within ${timeoutMs} ms`);
      throw new RunError('api_error', `${route}: ${e.cause?.code || e.name}`);
    }
    let text;
    try { text = await res.text(); } catch (e) {
      throw new RunError(e.name === 'TimeoutError' ? 'timeout' : 'api_error', `${route}: body read failed`);
    }
    if (res.status < 200 || res.status > 299) throw new RunError('api_error', `${route}: HTTP ${res.status}`);
    if (Buffer.byteLength(text) > MAX_MESSAGE_BYTES) throw new RunError('schema_invalid', `${route}: reply exceeds 1 MiB`);
    try { return JSON.parse(text); } catch { throw new RunError('schema_invalid', `${route}: reply is not valid JSON`); }
  };
  return {
    name: 'http',
    agent: { protocol: AGENT_PROTOCOL, transport: 'http', url: base },
    async init() {
      const c = await checkAgentUrl(base, { allowInsecureHttp });
      if (!c.ok) throw new Error(`refusing agent URL: ${c.reason} (use https, a private address, or --allow-insecure-http)`);
    },
    async openRun({ runId, scenario, system }) {
      checkAck(await post('start', { type: 'start', protocol: AGENT_PROTOCOL, run_id: runId, scenario, system }), 'start');
      return sessionFor(runId, timeoutMs, (msg) => post(msg.type, msg), async () => {});
    },
  };
}
