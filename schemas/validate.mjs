#!/usr/bin/env node
// Minimal JSON Schema (draft 2020-12) checker for the subset used by the schemas in this
// directory. No dependencies. Unsupported keywords throw, so a schema cannot silently rely on
// something this checker ignores.
//
//   node schemas/validate.mjs schemas/agent-decision.schema.json replies.jsonl
//
// Library use: validate(schema, value) -> array of error strings (empty when valid).

import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const ANNOTATIONS = new Set(['$schema', '$id', 'title', 'description', '$comment', 'examples', 'default', '$defs']);
const KEYWORDS = new Set(['type', 'const', 'enum', 'properties', 'required', 'additionalProperties', 'items', 'minItems',
  'maxItems', 'minimum', 'maximum', 'minLength', 'maxLength', 'pattern', 'oneOf', 'anyOf', 'not', '$ref']);

const typeOf = (v) => (v === null ? 'null' : Array.isArray(v) ? 'array' : typeof v);
const isType = (v, t) => (t === 'integer' ? Number.isInteger(v) : t === 'number' ? typeof v === 'number' && Number.isFinite(v) : typeOf(v) === t);
const equal = (a, b) => JSON.stringify(a) === JSON.stringify(b);

export function validate(schema, value, root = schema, at = '$') {
  const errs = [];
  if (schema === true) return errs;
  if (schema === false) return [`${at}: not allowed`];
  for (const k of Object.keys(schema)) {
    if (!KEYWORDS.has(k) && !ANNOTATIONS.has(k)) throw new Error(`unsupported schema keyword "${k}" at ${at}`);
  }
  if (schema.$ref) {
    const m = schema.$ref.match(/^#\/\$defs\/([^/]+)$/);
    if (!m || !root.$defs?.[m[1]]) throw new Error(`unsupported $ref ${schema.$ref}`);
    errs.push(...validate(root.$defs[m[1]], value, root, at));
  }
  if (schema.type) {
    const types = [].concat(schema.type);
    if (!types.some((t) => isType(value, t))) return [...errs, `${at}: expected ${types.join('|')}, got ${typeOf(value)}`];
  }
  if ('const' in schema && !equal(schema.const, value)) errs.push(`${at}: expected ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.some((e) => equal(e, value))) errs.push(`${at}: not one of ${JSON.stringify(schema.enum)}`);
  if (typeof value === 'number') {
    if (schema.minimum !== undefined && value < schema.minimum) errs.push(`${at}: below minimum ${schema.minimum}`);
    if (schema.maximum !== undefined && value > schema.maximum) errs.push(`${at}: above maximum ${schema.maximum}`);
  }
  if (typeof value === 'string') {
    const n = [...value].length;
    if (schema.minLength !== undefined && n < schema.minLength) errs.push(`${at}: shorter than ${schema.minLength}`);
    if (schema.maxLength !== undefined && n > schema.maxLength) errs.push(`${at}: longer than ${schema.maxLength}`);
    if (schema.pattern && !new RegExp(schema.pattern, 'u').test(value)) errs.push(`${at}: does not match ${schema.pattern}`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) errs.push(`${at}: fewer than ${schema.minItems} items`);
    if (schema.maxItems !== undefined && value.length > schema.maxItems) errs.push(`${at}: more than ${schema.maxItems} items`);
    if (schema.items !== undefined) value.forEach((v, i) => errs.push(...validate(schema.items, v, root, `${at}[${i}]`)));
  }
  if (typeOf(value) === 'object') {
    for (const r of schema.required ?? []) if (!(r in value)) errs.push(`${at}: missing required "${r}"`);
    const props = schema.properties ?? {};
    for (const [k, v] of Object.entries(value)) {
      if (k in props) errs.push(...validate(props[k], v, root, `${at}.${k}`));
      else if (schema.additionalProperties !== undefined) errs.push(...validate(schema.additionalProperties, v, root, `${at}.${k}`));
    }
  }
  if (schema.anyOf && !schema.anyOf.some((s) => !validate(s, value, root, at).length)) errs.push(`${at}: matches no anyOf branch`);
  if (schema.oneOf) {
    const n = schema.oneOf.filter((s) => !validate(s, value, root, at).length).length;
    if (n !== 1) errs.push(`${at}: matches ${n} oneOf branches, expected 1`);
  }
  if (schema.not !== undefined && !validate(schema.not, value, root, at).length) errs.push(`${at}: matches "not"`);
  return errs;
}

export function loadSchema(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const [schemaFile, dataFile] = process.argv.slice(2);
  if (!schemaFile || !dataFile) {
    console.error('usage: node schemas/validate.mjs <schema.json> <file.json|file.jsonl>');
    process.exit(64);
  }
  const schema = loadSchema(schemaFile);
  const text = fs.readFileSync(dataFile, 'utf8');
  const docs = dataFile.endsWith('.jsonl') ? text.split('\n').filter(Boolean).map((l) => JSON.parse(l)) : [JSON.parse(text)];
  let bad = 0;
  docs.forEach((d, i) => {
    const errs = validate(schema, d);
    if (errs.length) { bad++; console.log(`#${i}: ${errs.slice(0, 5).join('; ')}`); }
  });
  console.log(`${docs.length - bad}/${docs.length} valid`);
  process.exit(bad ? 1 : 0);
}
