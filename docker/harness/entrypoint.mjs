#!/usr/bin/env node
// Container entrypoint for benchmark/run/run.mjs.
// Adds safe defaults when the caller does not pass them:
//   --provider mock   (offline; no network, no key) unless --agent-url/--agent-cmd is given
//   --out $AGOE_OUT   (/out, the only writable path in the image)
// Each file /run/secrets/<name> is exported as <NAME> (e.g. agoe_agent_token ->
// AGOE_AGENT_TOKEN, anthropic_api_key -> ANTHROPIC_API_KEY) unless already set, so keys
// come from compose/swarm secrets rather than image layers or `docker inspect` output.
// The runner reads process.argv at import time, so everything is set before importing it.
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log(`usage: docker run [docker opts] IMAGE [run.mjs flags]
defaults: --provider mock --out ${process.env.AGOE_OUT || '/out'} --config benchmark/experiments/e1-anthropic/config.json
examples:
  IMAGE --stage smoke --budget-usd 100                     offline mock run
  IMAGE --agent-url http://agent:8080 --agent-name my-agent --stage smoke
other tools: --entrypoint python3 IMAGE benchmark/manifest.py verify`);
  process.exit(0);
}

const secretsDir = process.env.SECRETS_DIR || '/run/secrets';
try {
  for (const name of fs.readdirSync(secretsDir).sort()) {
    const file = path.join(secretsDir, name);
    const key = name.replace(/[^A-Za-z0-9]/g, '_').toUpperCase();
    if (key in process.env || !fs.statSync(file).isFile()) continue;
    process.env[key] = fs.readFileSync(file, 'utf8').trim();
  }
} catch (e) {
  if (e.code !== 'ENOENT') throw e;
}

const agent = args.includes('--agent-url') || args.includes('--agent-cmd');
if (!agent && !args.includes('--provider')) args.push('--provider', process.env.AGOE_PROVIDER || 'mock');
if (!args.includes('--out')) args.push('--out', process.env.AGOE_OUT || '/out');
process.chdir('/app');
process.argv = [process.argv[0], '/app/benchmark/run/run.mjs', ...args];
await import('/app/benchmark/run/run.mjs');
