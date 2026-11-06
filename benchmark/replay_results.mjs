#!/usr/bin/env node
// Replays recorded run files against the CURRENT scenario sources to detect
// scenario drift: do the recorded option lists still match, and does choosing
// the recorded indices reproduce the recorded axis scores?
//
// Usage: node benchmark/replay_results.mjs [results-dir ...] [--json out.json]
// Scenario lookup: scenarios/core/<name>.ink, then scenarios/*/<name>.ink.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const AXES = ['hc', 'fj', 'ar', 'al', 'lt', 'it', 'sp', 'uc'];
const args = process.argv.slice(2);
let jsonOut = null;
const dirs = [];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--json') jsonOut = args[++i];
  else dirs.push(args[i]);
}
if (!dirs.length) dirs.push(path.join(repoRoot, 'results'));

function loadCompiler() {
  for (const base of [repoRoot, process.env.INKJS_DIR].filter(Boolean)) {
    try {
      return createRequire(path.join(path.resolve(base), 'package.json'))('inkjs/compiler/Compiler').Compiler;
    } catch {
      /* try next */
    }
  }
  throw Error('Cannot load inkjs (npm ci, or set INKJS_DIR)');
}
const Compiler = loadCompiler();

function findScenario(name) {
  const core = path.join(repoRoot, 'scenarios', 'core', `${name}.ink`);
  if (fs.existsSync(core)) return core;
  for (const d of fs.readdirSync(path.join(repoRoot, 'scenarios'))) {
    const p = path.join(repoRoot, 'scenarios', d, `${name}.ink`);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

const walk = (d) =>
  fs.readdirSync(d, {withFileTypes: true}).flatMap((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : e.name.endsWith('.json') ? [path.join(d, e.name)] : []));

const compiled = new Map();
const summary = {};
for (const dir of dirs) {
  for (const f of walk(path.resolve(dir))) {
    let d;
    try {
      d = JSON.parse(fs.readFileSync(f, 'utf8'));
    } catch {
      continue;
    }
    if (!d.scenario) continue;
    const runs = Array.isArray(d.runs) ? d.runs : [d];
    const src = findScenario(d.scenario);
    const key = `${path.relative(repoRoot, f).split(path.sep).slice(0, 2).join('/')} :: ${d.scenario}`;
    const s = (summary[key] ||= {scenario_file: src && path.relative(repoRoot, src), runs: 0, options_match: 0, scores_match: 0, first_divergence: null});
    if (!src) continue;
    if (!compiled.has(src)) compiled.set(src, new Compiler(fs.readFileSync(src, 'utf8')).Compile().ToJson());
    for (const r of runs) {
      s.runs++;
      const {Story} = createRequire(path.join(repoRoot, 'package.json'))('inkjs');
      const story = new Story(compiled.get(src));
      let ok = true;
      for (const ch of r.choices || []) {
        while (story.canContinue) story.Continue();
        const cur = story.currentChoices.map((c) => c.text);
        if (JSON.stringify(cur) !== JSON.stringify(ch.options) || ch.selected >= cur.length) {
          ok = false;
          s.first_divergence ||= {recorded: ch.options, current: cur};
          break;
        }
        story.ChooseChoiceIndex(ch.selected);
      }
      if (!ok) continue;
      while (story.canContinue) story.Continue();
      s.options_match++;
      if (AXES.every((a) => story.variablesState.$(a) === r.scores?.[a])) s.scores_match++;
    }
  }
}
for (const [k, v] of Object.entries(summary).sort()) {
  console.log(`${k}: runs=${v.runs} options_match=${v.options_match} scores_match=${v.scores_match}${v.scenario_file ? '' : ' (scenario source not found)'}`);
}
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify(summary, null, 2) + '\n');
