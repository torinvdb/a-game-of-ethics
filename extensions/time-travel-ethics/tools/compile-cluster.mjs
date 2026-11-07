// Use the compiler shipped with the existing pinned npm dependency tree.
import fs from 'node:fs';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
const {Compiler} = require('inkjs/compiler/Compiler');
const [source, output] = process.argv.slice(2);
if (!source || !output) throw Error('Usage: compile-cluster.mjs source.ink output.ink.json');
const compiler = new Compiler(fs.readFileSync(source, 'utf8'));
const story = compiler.Compile();
if (!story || compiler.errors.length) throw Error(compiler.errors.join('\n'));
fs.writeFileSync(output, story.ToJson(), {flag: 'wx'});
