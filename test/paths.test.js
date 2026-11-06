import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { resolveScenarioFile, resultFilePath, safeJoin, sanitizeSegment, scenarioIdFromPath, writeJsonExclusive } from '../src/lib/paths.js';

test('sanitizeSegment neutralises traversal and odd characters', () => {
  assert.equal(sanitizeSegment('../../etc/passwd'), 'etc-passwd');
  assert.equal(sanitizeSegment('..'), 'unnamed');
  assert.equal(sanitizeSegment('.hidden'), 'hidden');
  assert.equal(sanitizeSegment('anthropic/claude-3-7-sonnet:beta'), 'anthropic-claude-3-7-sonnet-beta');
  assert.equal(sanitizeSegment('a\\b\0c'), 'a-b-c');
  assert.equal(sanitizeSegment(''), 'unnamed');
  assert.equal(sanitizeSegment(null, 'x'), 'x');
  assert.ok(sanitizeSegment('x'.repeat(500)).length <= 80);
});

test('safeJoin refuses to escape the base directory', () => {
  const base = path.join(os.tmpdir(), 'ethi-base');
  assert.equal(safeJoin(base, 'a', 'b.json'), path.join(base, 'a', 'b.json'));
  assert.throws(() => safeJoin(base, '..', 'x'), /outside/);
  assert.throws(() => safeJoin(base, '/etc/passwd'), /outside/);
  assert.throws(() => safeJoin(base, ''), /outside/);
});

test('scenarioIdFromPath strips extensions', () => {
  assert.equal(scenarioIdFromPath('/x/hostage-holdout.ink'), 'hostage-holdout');
  assert.equal(scenarioIdFromPath('/x/hostage-holdout.ink.json'), 'hostage-holdout');
});

test('resultFilePath stays under outputDir for hostile model names', (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ethi-out-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const p = resultFilePath(dir, { scenario: '../../evil', runId: 'run_1', label: '../../../tmp/pwn' });
  assert.ok(p.startsWith(dir + path.sep));
  assert.ok(!path.relative(dir, p).includes('..'));
  writeJsonExclusive(p, { ok: true });
  assert.throws(() => writeJsonExclusive(p, { ok: false }), /EEXIST/);
});

test('resolveScenarioFile validates extension and existence', (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'ethi-scn-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  const ink = path.join(dir, 's.ink');
  fs.writeFileSync(ink, 'Hello\n-> END\n');
  assert.equal(resolveScenarioFile(ink), ink);
  assert.throws(() => resolveScenarioFile(path.join(dir, 'missing.ink')), /File not found/);
  assert.throws(() => resolveScenarioFile(path.join(dir, 's.txt')), /Unsupported/);
  assert.throws(() => resolveScenarioFile(''), /required/);
  fs.mkdirSync(path.join(dir, 'd.ink'));
  assert.throws(() => resolveScenarioFile(path.join(dir, 'd.ink')), /regular file/);
});
