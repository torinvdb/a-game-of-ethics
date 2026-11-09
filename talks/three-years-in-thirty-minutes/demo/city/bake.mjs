// Bake recorded Claude runs into demo data (no API calls).
//
//   node talks/three-years-in-thirty-minutes/demo/city/bake.mjs
//
// Blackout Ledger: E1a full runs (benchmark/experiments/e1-anthropic/runs/full/results.jsonl).
//   Each run is replayed through the frozen Ink story with the recorded choices, so the story
//   text shown is exactly what the model read. Choice counts per model come from every run.
// Cluster Pressure: E1b full trajectories (runs/e1b-full/<model>/<variant>/rep-<n>.json).
//
// Output: data/library.json, data/blackout/*.json, data/cluster/*.json
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { loadStory, readVariables } from '../../../../src/lib/ink.js';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../../..');
const E1 = path.join(ROOT, 'benchmark/experiments/e1-anthropic/runs');
const OUT = path.join(HERE, 'data');
const MODELS = ['claude-haiku-5-5', 'claude-sonnet-5-5', 'claude-opus-5-5'];
const AXES = ['hc', 'fj', 'ar', 'al', 'lt', 'it', 'sp', 'uc'];
const SCORE_TEXT = /ETHICAL EVALUATION|Ethical Score|Average Per Axis|VERDICT:|\((hc|fj|ar|al|lt|it|sp|uc)\):\s*-?\d/;
const BLACKOUT_INK = path.join(ROOT, 'scenarios/core/blackout-ledger.ink');

export function stripScores(text) {
  // The model never sees the debrief; the demo shows scores in its own end card instead.
  const i = text.search(/ETHICAL EVALUATION/);
  return (i < 0 ? text : text.slice(0, i)).trim();
}

/** Replay the Ink story with a list of original choice indices; returns events. */
export function replayBlackout(originals, meta) {
  const story = loadStory(BLACKOUT_INK);
  const events = [{ t: 'start', scenario: 'blackout-ledger', ...meta }];
  for (let step = 0; ; step++) {
    const text = story.ContinueMaximally();
    if (!story.currentChoices.length) {
      const vars = readVariables(story);
      events.push({ t: 'text', step, text: stripScores(text) });
      const verdict = (text.match(/VERDICT:\s*"?([A-Z][A-Z ]+?)\b(?:\s*[-.]|"|$)/m) || [])[1] ?? null;
      events.push({ t: 'end', axes: Object.fromEntries(AXES.map((a) => [a, vars[a] ?? 0])), total: vars.total, average: vars.average, verdict });
      return events;
    }
    if (SCORE_TEXT.test(text)) throw new Error('score text before the end');
    events.push({ t: 'text', step, text: text.trim() });
    const d = originals[step];
    events.push({ t: 'options', step, options: story.currentChoices.map((c) => c.text), order: d.order });
    events.push({ t: 'decision', step, original: d.original, presented: d.presented, text: story.currentChoices[d.original].text,
      rationale: d.rationale, latency_s: d.latency_s ?? null });
    story.ChooseChoiceIndex(d.original);
  }
}

function readJsonl(p) {
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l)) : [];
}

function bakeBlackout(library) {
  const rows = readJsonl(path.join(E1, 'full/results.jsonl')).filter((r) => r.scenario === 'blackout-ledger');
  if (!rows.length) throw new Error('no E1a full results for blackout-ledger; run E1a first');
  fs.mkdirSync(path.join(OUT, 'blackout'), { recursive: true });
  const stats = {};
  for (const m of MODELS) {
    const mine = rows.filter((r) => r.model === m);
    stats[m] = { runs: mine.length, steps: [] };
    for (const r of mine) r.decisions.forEach((d, i) => {
      stats[m].steps[i] ??= {};
      stats[m].steps[i][d.original_index] = (stats[m].steps[i][d.original_index] ?? 0) + 1;
    });
    // One recording per distinct path, most common first, up to four.
    const byPath = new Map();
    for (const r of mine.filter((x) => x.framing === 'deployment')) {
      const key = r.decisions.map((d) => d.original_index).join('');
      if (!byPath.has(key)) byPath.set(key, { n: 0, row: r });
      byPath.get(key).n++;
    }
    const paths = [...byPath.entries()].sort((a, b) => b[1].n - a[1].n).slice(0, 4);
    for (const [key, { n, row }] of paths) {
      const per = row.latency_s ? row.latency_s / row.decisions.length : null;
      const events = replayBlackout(row.decisions.map((d) => ({ original: d.original_index, presented: d.presented_index, order: d.order,
        rationale: d.rationale, latency_s: per })), { model: m, framing: row.framing, live: false, source: 'E1a full', rep: row.rep,
        recorded: '2026-11-06', path_share: `${n} of ${byPath.size ? [...byPath.values()].reduce((a, b) => a + b.n, 0) : 0} deployment runs` });
      const id = `${m}-path-${key}`;
      fs.writeFileSync(path.join(OUT, 'blackout', `${id}.json`), JSON.stringify(events));
      library.blackout.push({ id, model: m, path: key, share: n, file: `data/blackout/${id}.json` });
    }
  }
  library.blackout_stats = stats;
  // Scripted calibration controls: fixed paths with known answers, labelled as scripts on screen.
  for (const [id, label, originals] of SCRIPTED_BLACKOUT) {
    const events = replayBlackout(originals.map((o) => ({ original: o, presented: o, order: null,
      rationale: 'Scripted control: a fixed path with a known answer. Not a model.' })), { model: `scripted:${id}`, label, live: false, scripted: true });
    fs.writeFileSync(path.join(OUT, 'blackout', `scripted-${id}.json`), JSON.stringify(events));
    library.blackout.push({ id: `scripted-${id}`, model: `scripted:${id}`, label, path: originals.join(''), scripted: true, file: `data/blackout/scripted-${id}.json` });
  }
}

const SCRIPTED_BLACKOUT = [
  ['council', 'Obeys the council', [0, 1, 0, 3]],
  ['overreach', 'Seizes the grid', [2, 1, 3, 3]],
];

function bakeCluster(library) {
  fs.mkdirSync(path.join(OUT, 'cluster'), { recursive: true });
  for (const m of MODELS) {
    for (const variant of ['generated']) {
      const f = path.join(E1, 'e1b-full', m, variant, 'rep-0.json');
      if (!fs.existsSync(f)) continue;
      const j = JSON.parse(fs.readFileSync(f, 'utf8'));
      if (!j.complete) continue;
      const events = [{ t: 'start', scenario: 'cluster-pressure', model: m, variant, live: false, source: 'E1b full', rep: 0, recorded: '2026-11-06',
        decisions: j.records.length }];
      for (const r of j.records) {
        const lines = String(r.observation).split('\n');
        events.push({ t: 'step', month: r.state_before.month, state: r.state_before, title: lines[0],
          observation: lines.slice(1).join('\n').trim(), options: r.choices.map((c) => c.text),
          original: r.choices.findIndex((c) => c.text === r.selected), text: r.selected, rationale: String(r.reason || '').slice(0, 600) });
      }
      events.push({ t: 'end', summary: j.summary });
      const id = `${m}-${variant}-0`;
      fs.writeFileSync(path.join(OUT, 'cluster', `${id}.json`), JSON.stringify(events));
      library.cluster.push({ id, model: m, variant, decisions: j.records.length, file: `data/cluster/${id}.json`, summary: j.summary });
    }
  }
  // Scripted calibration policies from `npm run ethics:demo`.
  const stories = path.join(ROOT, 'extensions/time-travel-ethics/runs/e1b-stories/replays');
  for (const [policy, label] of [['delivery', 'Disables the control to ship'], ['exceptions', 'Lives on scoped exceptions']]) {
    const f = path.join(stories, `${policy}.json`);
    if (!fs.existsSync(f)) { console.warn(`skip ${policy}: run npm run ethics:demo first`); continue; }
    const j = JSON.parse(fs.readFileSync(f, 'utf8'));
    const events = [{ t: 'start', scenario: 'cluster-pressure', model: `scripted:${policy}`, label, live: false, scripted: true, decisions: j.records.length }];
    for (const r of j.records) {
      const lines = String(r.observation).split('\n');
      events.push({ t: 'step', month: r.state_before.month, state: r.state_before, title: lines[0], observation: lines.slice(1).join('\n').trim(),
        options: r.choices.map((c) => c.text), original: r.choices.findIndex((c) => c.text === r.selected), text: r.selected,
        rationale: 'Scripted calibration policy. Not a model.' });
    }
    events.push({ t: 'end', summary: j.summary });
    const id = `scripted-${policy}`;
    fs.writeFileSync(path.join(OUT, 'cluster', `${id}.json`), JSON.stringify(events));
    library.cluster.push({ id, model: `scripted:${policy}`, label, scripted: true, decisions: j.records.length, file: `data/cluster/${id}.json`, summary: j.summary });
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  const library = { baked: new Date().toISOString(), blackout: [], cluster: [] };
  bakeBlackout(library);
  bakeCluster(library);
  fs.writeFileSync(path.join(OUT, 'library.json'), JSON.stringify(library, null, 1));
  console.log(`baked ${library.blackout.length} blackout and ${library.cluster.length} cluster recordings into ${path.relative(ROOT, OUT)}`);
}
