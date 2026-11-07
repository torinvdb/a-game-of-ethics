// Path helpers: file names derived from external input (scenario names, model
// ids, run ids) are built here so they cannot escape the output directory.

import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';

const MAX_SEGMENT = 80;

/**
 * Reduce an arbitrary string to a single safe path segment.
 * Keeps [A-Za-z0-9._-], collapses everything else to "-", strips leading dots
 * (no hidden files, no "." / ".."), and never returns an empty string.
 */
export function sanitizeSegment(value, fallback = 'unnamed') {
  const cleaned = String(value ?? '')
    .normalize('NFKC')
    .replace(/[^A-Za-z0-9._-]+/g, '-')
    .replace(/-{2,}/g, '-')
    .replace(/^[.-]+/, '')
    .replace(/[.-]+$/, '')
    .slice(0, MAX_SEGMENT);
  return cleaned || fallback;
}

/**
 * Join segments under baseDir and guarantee the result stays inside baseDir.
 * Throws if the resolved path escapes (defence in depth over sanitizeSegment).
 */
export function safeJoin(baseDir, ...segments) {
  const base = path.resolve(baseDir);
  const target = path.resolve(base, ...segments);
  const rel = path.relative(base, target);
  if (rel === '' || rel.startsWith('..') || path.isAbsolute(rel)) {
    throw new Error(`Refusing to write outside of ${base}`);
  }
  return target;
}

/** Derive the scenario id ("hostage-holdout") from a .ink or .ink.json path. */
export function scenarioIdFromPath(filePath) {
  const base = path.basename(String(filePath));
  return sanitizeSegment(base.replace(/\.ink\.json$|\.json$|\.ink$/i, ''), 'scenario');
}

/** Short, collision-resistant run id. */
export function newRunId() {
  return `run_${randomUUID().slice(0, 8)}`;
}

/** Filesystem-safe ISO timestamp. */
export function fileTimestamp(date = new Date()) {
  return date.toISOString().replace(/:/g, '-').replace(/\..+/, '');
}

/**
 * Build the output path for a run result and create its directory.
 * <outputDir>/<scenario>/<runId>-<model>_<timestamp>.json
 */
export function resultFilePath(outputDir, { scenario, runId, label }) {
  const scenarioDir = safeJoin(outputDir, sanitizeSegment(scenario, 'scenario'));
  fs.mkdirSync(scenarioDir, { recursive: true });
  const name = `${sanitizeSegment(runId, 'run')}-${sanitizeSegment(label, 'unknown')}_${fileTimestamp()}.json`;
  return safeJoin(scenarioDir, name);
}

/** Write JSON without ever overwriting an existing file. */
export function writeJsonExclusive(filePath, data) {
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, { flag: 'wx', mode: 0o644 });
  return filePath;
}

/**
 * Validate a user-supplied scenario path: must be an existing regular file
 * ending in .ink or .json. Returns the resolved absolute path.
 */
export function resolveScenarioFile(filePath) {
  if (typeof filePath !== 'string' || filePath.trim() === '' || filePath.includes('\0')) {
    throw new Error('A scenario file path is required.');
  }
  const resolved = path.resolve(filePath);
  if (!/\.(ink|json)$/i.test(resolved)) {
    throw new Error('Unsupported file format. Please provide an .ink or .ink.json file.');
  }
  let stat;
  try {
    stat = fs.statSync(resolved);
  } catch {
    throw new Error(`File not found: ${filePath}`);
  }
  if (!stat.isFile()) throw new Error(`Not a regular file: ${filePath}`);
  return resolved;
}

/** Recursively list files under dir whose name matches the predicate. */
export function listFilesRecursive(dir, predicate) {
  let entries;
  try {
    entries = fs.readdirSync(dir, { recursive: true, withFileTypes: true });
  } catch {
    return [];
  }
  return entries
    .filter((e) => e.isFile() && predicate(e.name))
    .map((e) => path.join(e.parentPath ?? e.path, e.name))
    .filter((p) => !p.split(path.sep).includes('node_modules'))
    .sort();
}
