// Provider adapters for benchmark/run/run.mjs.
// Each adapter: decide({system, messages, numChoices, model, settings}) ->
//   { choice (1-based), rationale, assistantContent, usage, servedModel, stopReason }
// or throws RunError with a failure class. A failure is never converted into a choice.

import Anthropic from '@anthropic-ai/sdk';
import { requestCompletion, resolveAdapterConfig, parseChoice } from '../../src/lib/llm.js';

export class RunError extends Error {
  constructor(failureClass, detail, extra = {}) {
    super(`${failureClass}: ${detail}`);
    this.failureClass = failureClass; // refusal | truncated | schema_invalid | api_error | timeout | served_model_mismatch
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
  throw new Error(`unknown provider ${name}`);
}
