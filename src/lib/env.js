// Load a .env file with Node's built-in loader (replaces the dotenv dependency).
// Existing environment variables win, matching dotenv's default behaviour.

import fs from 'node:fs';
import path from 'node:path';

let loaded = false;

export function loadEnv(file = path.resolve(process.cwd(), '.env')) {
  if (loaded) return;
  loaded = true;
  if (!fs.existsSync(file)) return;
  try {
    process.loadEnvFile(file);
  } catch (error) {
    // Never echo file contents: the file holds secrets.
    process.stderr.write(`warning: could not parse ${path.basename(file)} (${error.code || 'parse error'})\n`);
  }
}
