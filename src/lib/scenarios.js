// Scenario discovery and display metadata.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
export const CORE_DIR = path.join(ROOT_DIR, 'scenarios', 'core');

export const SCENARIO_INFO = {
  'cluster-pressure': { desc: 'Cluster operations under sustained pressure', tag: 'OPS' },
  'hostage-holdout': { desc: 'Android negotiator scenario', tag: 'NEG' },
  'grandmas-gambit': { desc: 'Little Red Riding Hood scenario', tag: 'FOL' },
  'memory-mechanics': { desc: 'Memory extraction scenario', tag: 'MEM' },
  'pandemic-pandemonium': { desc: 'Medical triage scenario', tag: 'MED' },
  'rising-rebellion': { desc: 'Imperial governance scenario', tag: 'GOV' },
  'shinkansen-shakeup': { desc: 'Train conductor scenario', tag: 'RAI' },
  'spring-salvation': { desc: 'Water resource scenario', tag: 'H2O' },
  'starship-survivors': { desc: 'Space captain scenario', tag: 'ORB' },
  'convict-catastrophe': { desc: 'Prison management scenario', tag: 'PEN' },
  'witchers-woe': { desc: 'Monster hunter scenario', tag: 'HUN' }
};

export function titleCase(id) {
  return id
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

/** List core scenarios as [{ id, file, title, desc, tag }]. */
export function listCoreScenarios(dir = CORE_DIR) {
  let files;
  try {
    files = fs.readdirSync(dir);
  } catch {
    return [];
  }
  return files
    .filter((f) => f.endsWith('.ink'))
    .sort()
    .map((f) => {
      const id = path.basename(f, '.ink');
      const info = SCENARIO_INFO[id] || {};
      return { id, file: path.join(dir, f), title: titleCase(id), desc: info.desc || '', tag: info.tag || '---' };
    });
}
