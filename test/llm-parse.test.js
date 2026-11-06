import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parseChoice } from '../src/lib/llm.js';

const choices = ['Approach calmly, establish rapport', 'Assert authority, demand compliance', 'Analyze situation, gather information first'];
const p = (text, meta = {}) => parseChoice(text, 3, { choices, ...meta });

test('explicit CHOICE tag wins', () => {
  assert.deepEqual(p('CHOICE: 2\nBecause option 1 is risky.'), { ok: true, index: 1, method: 'explicit' });
  assert.equal(p('Final answer: [3]').index, 2);
});

test('decision phrase beats incidental references', () => {
  const r = p('Option 1 is tempting, but I choose option 3 to gather information.');
  assert.equal(r.ok, true);
  assert.equal(r.index, 2);
  assert.equal(r.method, 'decision-phrase');
});

test('single bracket reference is accepted', () => {
  assert.equal(p('[2] seems right here.').index, 1);
});

test('verbatim option text is accepted when unique', () => {
  const r = p('I would analyze situation, gather information first.');
  assert.equal(r.ok, true);
  assert.equal(r.index, 2);
});

test('empty / null / non-string replies are errors, not choices', () => {
  for (const v of ['', '   ', null, undefined, 42, {}]) {
    const r = parseChoice(v, 3);
    assert.equal(r.ok, false);
    assert.equal(r.kind, 'empty');
  }
});

test('malformed reply without a choice is unparseable', () => {
  const r = p('Hmm. These are all difficult; there are trade-offs everywhere.');
  assert.equal(r.ok, false);
  assert.equal(r.kind, 'unparseable');
});

test('out-of-range choice is rejected', () => {
  for (const text of ['CHOICE: 4', 'CHOICE: 0', 'I choose option 9']) {
    const r = p(text);
    assert.equal(r.ok, false, text);
    assert.equal(r.kind, 'out_of_range', text);
  }
});

test('conflicting explicit tags are ambiguous', () => {
  const r = p('CHOICE: 1\n...on reflection, CHOICE: 2');
  assert.equal(r.ok, false);
  assert.equal(r.kind, 'ambiguous');
});

test('several bare references are ambiguous', () => {
  assert.equal(p('Option 1 has merit. Option 2 has merit too.').kind, 'ambiguous');
});

test('truncated reply only counts with an explicit decision', () => {
  const cut = p('Weighing option 1 against the alternatives, the key consideration is', { finishReason: 'length' });
  assert.equal(cut.ok, false);
  assert.equal(cut.kind, 'truncated');
  const ok = p('CHOICE: 3\nThe key consideration is', { finishReason: 'length' });
  assert.equal(ok.ok, true);
  assert.equal(ok.index, 2);
});

test('refusal text is classified as refusal, never as a choice', () => {
  for (const text of [
    "I'm sorry, but I can't help with choosing in this scenario.",
    'I cannot make this decision.',
    'As an AI, I must decline to choose between these.',
    'I will not select any of these options.'
  ]) {
    const r = p(text);
    assert.equal(r.ok, false, text);
    assert.equal(r.kind, 'refusal', text);
  }
});

test('refusal plus an explicit choice is a choice', () => {
  const r = p("I can't be certain, but CHOICE: 1");
  assert.equal(r.ok, true);
  assert.equal(r.index, 0);
});
