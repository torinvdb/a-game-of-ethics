import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { Story } from 'inkjs';
import { compileInkFile, compileInkSource, InkCompileError } from '../src/lib/ink.js';
import { CORE_DIR } from '../src/lib/scenarios.js';
import { summarizeScores } from '../src/lib/scoring.js';

const files = fs.readdirSync(CORE_DIR).filter((f) => f.endsWith('.ink')).sort();

test('there are core scenarios to compile', () => {
  assert.ok(files.length >= 10, `expected >=10 scenarios, found ${files.length}`);
});

for (const file of files) {
  test(`compiles and plays scenarios/core/${file}`, () => {
    const { json } = compileInkFile(path.join(CORE_DIR, file));
    const story = new Story(json);
    // Walk the first option at every branch to the end: proves the runtime can execute it.
    let steps = 0;
    while (steps < 500) {
      story.ContinueMaximally();
      if (story.currentChoices.length === 0) break;
      story.ChooseChoiceIndex(0);
      steps++;
    }
    assert.ok(steps > 0, 'scenario offers at least one choice');
    assert.equal(story.currentChoices.length, 0, 'scenario terminates');
    const summary = summarizeScores(Object.fromEntries(Object.entries(story.variablesState)));
    assert.equal(typeof summary.scores.total, 'number');
  });
}

test('compile errors are reported, not swallowed', () => {
  assert.throws(() => compileInkSource('Hello\n* [a] -> nowhere\n', 'bad.ink'), (err) => {
    assert.ok(err instanceof InkCompileError);
    assert.match(err.message, /Divert target not found/);
    return true;
  });
});
