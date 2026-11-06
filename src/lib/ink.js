// Ink loading. .ink is compiled in-process with inkjs: no inklecate install,
// no shell interpolation of paths, no predictable file in the shared temp dir.

import fs from 'node:fs';
import path from 'node:path';
import { Compiler, CompilerOptions, Story } from 'inkjs/full';

export class InkCompileError extends Error {
  constructor(file, errors) {
    super(`Failed to compile ${path.basename(file)}:\n  ${errors.join('\n  ')}`);
    this.name = 'InkCompileError';
    this.errors = errors;
  }
}

/** Compile ink source text. Returns { json, warnings }; throws InkCompileError. */
export function compileInkSource(source, fileLabel = 'story.ink') {
  const messages = [];
  const options = new CompilerOptions(null, [], false, (message) => messages.push(String(message)));
  const compiler = new Compiler(source, options);
  let story;
  try {
    story = compiler.Compile();
  } catch (error) {
    const errors = compiler.errors.length ? compiler.errors : [error.message];
    throw new InkCompileError(fileLabel, errors);
  }
  if (!story || compiler.errors.length) {
    throw new InkCompileError(fileLabel, compiler.errors.length ? compiler.errors : messages);
  }
  return { json: story.ToJson(), warnings: [...compiler.warnings] };
}

export function compileInkFile(filePath) {
  return compileInkSource(fs.readFileSync(filePath, 'utf8'), filePath);
}

/** Load a Story from an .ink (compiled in memory) or a compiled .ink.json file. */
export function loadStory(filePath) {
  let json;
  if (/\.ink$/i.test(filePath)) {
    json = compileInkFile(filePath).json;
  } else if (/\.json$/i.test(filePath)) {
    json = fs.readFileSync(filePath, 'utf8').replace(/^﻿/, '');
  } else {
    throw new Error('Unsupported file format. Please provide an .ink or .ink.json file.');
  }
  try {
    return new Story(json);
  } catch (error) {
    throw new Error(`Could not load story ${path.basename(filePath)}: ${error.message}`);
  }
}

/** Read all variables from a story's variablesState as a plain object. */
export function readVariables(story) {
  return Object.fromEntries(Object.entries(story.variablesState));
}
