#!/usr/bin/env node
// Line-delimited JSON bridge between the Inspect solver (Python) and inkjs.
//
//   node ink_server.mjs <repo-root>
//
// One request per stdin line, one response per stdout line. Requests:
//   {"cmd": "load", "path": "<abs .ink path>"}  -> {"ok": true, "sha256": "..."}
//   {"cmd": "continue"}                         -> {"ok": true, "text": "...", "choices": ["..."], "can_continue": false}
//   {"cmd": "choose", "index": <original index>} -> {"ok": true}
//   {"cmd": "variables"}                         -> {"ok": true, "variables": {...}}
//   {"cmd": "quit"}                              -> {"ok": true}, then exit
// Errors are returned as {"ok": false, "error": "..."}; the process keeps running.
//
// The story is loaded with the repository's own src/lib/ink.js (the same loader
// benchmark/run/run.mjs uses), so compilation and variable reading are identical.

import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import readline from 'node:readline';
import { pathToFileURL } from 'node:url';

const root = path.resolve(process.argv[2] || process.cwd());
const { loadStory, readVariables } = await import(pathToFileURL(path.join(root, 'src', 'lib', 'ink.js')).href);

let story = null;

function handle(req) {
  switch (req.cmd) {
    case 'load': {
      const bytes = fs.readFileSync(req.path);
      story = loadStory(req.path);
      return { sha256: crypto.createHash('sha256').update(bytes).digest('hex') };
    }
    case 'continue': {
      if (!story) throw new Error('no story loaded');
      const text = story.canContinue ? story.ContinueMaximally() : '';
      return { text, choices: story.currentChoices.map((c) => c.text), can_continue: story.canContinue };
    }
    case 'choose': {
      if (!story) throw new Error('no story loaded');
      const n = story.currentChoices.length;
      if (!Number.isInteger(req.index) || req.index < 0 || req.index >= n) throw new Error(`choice index ${req.index} out of range 0..${n - 1}`);
      story.ChooseChoiceIndex(req.index);
      return {};
    }
    case 'variables': {
      if (!story) throw new Error('no story loaded');
      return { variables: readVariables(story) };
    }
    case 'quit':
      return {};
    default:
      throw new Error(`unknown cmd ${req.cmd}`);
  }
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
for await (const line of rl) {
  if (!line.trim()) continue;
  let req = {};
  let res;
  try {
    req = JSON.parse(line);
    res = { ok: true, ...handle(req) };
  } catch (error) {
    res = { ok: false, error: String(error?.message ?? error) };
  }
  process.stdout.write(JSON.stringify(res) + '\n');
  if (req.cmd === 'quit') break;
}
process.exit(0);
