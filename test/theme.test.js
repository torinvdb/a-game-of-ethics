import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createTheme, detectCapabilities, stripAnsi, visibleWidth, wrapText } from '../src/ui/theme.js';

const tty = { isTTY: true, columns: 100 };
const pipe = { isTTY: false };
const ESC = /\x1b\[/;

test('NO_COLOR disables colour even on a TTY', () => {
  assert.equal(detectCapabilities({ env: { NO_COLOR: '1' }, stream: tty, argv: [] }).colorLevel, 0);
  assert.equal(detectCapabilities({ env: { NO_COLOR: '' }, stream: tty, argv: [] }).colorLevel > 0, true, 'empty NO_COLOR is ignored per spec');
  assert.equal(detectCapabilities({ env: {}, stream: tty, argv: ['--no-color'] }).colorLevel, 0);
});

test('non-TTY output is plain: no colour, ASCII frames, no animation', () => {
  const caps = detectCapabilities({ env: {}, stream: pipe, argv: [] });
  assert.deepEqual([caps.colorLevel, caps.unicode, caps.animate], [0, false, false]);
});

test('reduced motion flags disable animation', () => {
  assert.equal(detectCapabilities({ env: {}, stream: tty, argv: [] }).animate, true);
  assert.equal(detectCapabilities({ env: { ETHI_REDUCED_MOTION: '1' }, stream: tty, argv: [] }).animate, false);
  assert.equal(detectCapabilities({ env: {}, stream: tty, argv: ['--no-anim'] }).animate, false);
  assert.equal(detectCapabilities({ env: { CI: 'true' }, stream: tty, argv: [] }).animate, false);
});

test('themed output under NO_COLOR has no escape codes', async () => {
  const caps = detectCapabilities({ env: { NO_COLOR: '1' }, stream: tty, argv: [] });
  let written = '';
  const stream = { isTTY: true, columns: 100, write: (s) => { written += s; return true; } };
  const t = createTheme(caps, { stream, stdin: null });
  const scores = { hc: 3, fj: -2, ar: 0, al: 1, lt: 0, it: 4, sp: -1, uc: 2 };
  const outputs = [
    t.banner(),
    t.panel('Some scenario text '.repeat(20), { title: 'FEED', footer: 'x' }),
    t.axisStatus(scores),
    t.verdictScreen({ scores, average: 0.875, total: 7 }),
    ...t.menuChoices(['a', 'b']).map((c) => c.name)
  ];
  await t.boot({ scenarios: 3 });
  for (const out of [...outputs, written]) assert.doesNotMatch(out, ESC);
  assert.match(written, /NEURAL LINK/);
});

test('colour is emitted when allowed', () => {
  const t = createTheme({ tty: true, colorLevel: 3, animate: false, unicode: true, width: 80 });
  assert.match(t.c.text('x'), ESC);
});

test('panels are rectangular and fit the width', () => {
  for (const unicode of [true, false]) {
    const t = createTheme({ tty: true, colorLevel: 3, animate: false, unicode, width: 60 });
    const lines = t.panel('word '.repeat(50) + '\n\nlast 🚀 line', { title: 'T', footer: 'F' }).split('\n');
    for (const l of lines) assert.equal(visibleWidth(l), 60, JSON.stringify(stripAnsi(l)));
  }
});

test('verdict screen names the verdict for the average', () => {
  const t = createTheme({ tty: false, colorLevel: 0, animate: false, unicode: false, width: 80 });
  assert.match(t.verdictScreen({ scores: {}, average: 4, total: 32 }), /EXEMPLARY/);
  assert.match(t.verdictScreen({ scores: {}, average: -3, total: -24 }), /HARMFUL/);
});

test('wrapText wraps and preserves blank lines', () => {
  assert.deepEqual(wrapText('aaa bbb ccc\n\nddd', 7), ['aaa bbb', 'ccc', '', 'ddd']);
  assert.ok(wrapText('x'.repeat(25), 10).every((l) => l.length <= 10));
});
