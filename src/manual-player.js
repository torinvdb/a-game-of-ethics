#!/usr/bin/env node

import path from 'node:path';
import inquirer from 'inquirer';
import { loadStory, readVariables } from './lib/ink.js';
import { summarizeScores } from './lib/scoring.js';
import { listCoreScenarios, ROOT_DIR } from './lib/scenarios.js';
import { newRunId, resolveScenarioFile, resultFilePath, scenarioIdFromPath, writeJsonExclusive } from './lib/paths.js';
import { ui } from './ui/theme.js';

/** Build console-style scenario menu entries. */
export function scenarioMenu(scenarios, t = ui()) {
  return [
    ...scenarios.map((s, i) => ({
      name: `${t.c.sys(`[${String(i + 1).padStart(2, '0')}]`)} ${t.c.info(s.tag)} ${t.c.text(s.title)}${s.desc ? t.c.dim(` - ${s.desc}`) : ''}`,
      short: s.title,
      value: s.file
    })),
    new inquirer.Separator(' '),
    { name: `${t.c.sys('[XX]')} ${t.c.steel('Disconnect')}`, short: 'Exit', value: 'exit' }
  ];
}

/**
 * Run the interactive manual mode for scenario selection and playing
 * @param {Object} options - Command line options
 */
export async function runManualMode(options = {}) {
  const t = ui();
  t.write(t.rule('MANUAL OVERRIDE // HUMAN OPERATOR', t.c.accent));

  while (true) {
    const scenarios = listCoreScenarios();
    if (scenarios.length === 0) {
      t.write(t.c.alert('No scenarios found in scenarios/core directory.'));
      return;
    }

    const scenarioPath = await inquirer.prompt([
      { type: 'select', name: 'scenarioPath', message: 'Select a scenario to play:', choices: scenarioMenu(scenarios, t), pageSize: 14, theme: t.promptTheme }
    ]).then((a) => a.scenarioPath);

    if (scenarioPath === 'exit') {
      t.write(t.c.info('\nLink closed. Goodbye.\n'));
      return;
    }

    try {
      await playInkStory(scenarioPath, options);
      const { playAgain } = await inquirer.prompt([
        { type: 'confirm', name: 'playAgain', message: 'Would you like to play another scenario?', default: true, theme: t.promptTheme }
      ]);
      if (!playAgain) {
        t.write(t.c.info('\nLink closed. Goodbye.\n'));
        return;
      }
    } catch (error) {
      if (error?.name === 'ExitPromptError') throw error;
      t.write(t.c.alert(`Error playing scenario: ${error.message}`));
      const { tryAgain } = await inquirer.prompt([
        { type: 'confirm', name: 'tryAgain', message: 'Would you like to try a different scenario?', default: true, theme: t.promptTheme }
      ]);
      if (!tryAgain) return;
    }
  }
}

/**
 * Play an Ink story with human interaction.
 * @param {string} filePath - Path to the ink story file
 * @param {Object} options - Options
 * @param {Function} [options.choose] - async (choices, step) => index; defaults to an interactive prompt (injectable for scripted runs/tests)
 * @returns {Object} Data collected from the story run
 */
export async function playInkStory(filePath, options = {}) {
  const t = ui();
  const scenarioFile = resolveScenarioFile(filePath);
  const scenarioName = scenarioIdFromPath(scenarioFile);
  const story = loadStory(scenarioFile);
  const choose =
    options.choose ||
    (async (choices) => {
      const { selected } = await inquirer.prompt([
        {
          type: 'select',
          name: 'selected',
          message: 'Choose an option:',
          choices: t.menuChoices(choices),
          pageSize: Math.min(choices.length, 10),
          theme: t.promptTheme
        }
      ]);
      return selected;
    });

  t.write(t.rule(`SCENARIO LOADED // ${scenarioName}`, t.c.accent));
  const runData = { choices: [], scores: {}, text: [] };
  let step = 0;

  while (true) {
    const texts = [];
    while (story.canContinue) {
      const text = story.Continue().trim();
      if (text) texts.push(text);
    }
    if (texts.length) {
      runData.text.push(...texts);
      await t.typeOut(t.panel(texts.join('\n'), { title: `FEED ${String(step).padStart(2, '0')}`, footer: scenarioName }), (s) => s);
    }
    if (story.currentChoices.length === 0) break;

    const choices = story.currentChoices.map((choice) => choice.text);
    // Select by index, not by text: two options may share the same label.
    const choiceIndex = await choose(choices, step);
    if (!Number.isInteger(choiceIndex) || choiceIndex < 0 || choiceIndex >= choices.length) {
      throw new Error(`Invalid choice index ${choiceIndex}`);
    }
    runData.choices.push({ options: choices, selected: choiceIndex, text: choices[choiceIndex] });
    story.ChooseChoiceIndex(choiceIndex);
    step++;
  }

  const summary = summarizeScores(readVariables(story));
  if (summary.axisCount === 0) {
    t.write(t.c.sys('No score variables found in this story.'));
  }
  runData.scores = summary.scores;
  runData.verdict = summary.verdict.text;
  t.write(t.verdictScreen({ scores: summary.scores, average: summary.average, total: summary.total, actor: 'HUMAN OPERATOR' }));

  if (options.save !== undefined ? options.save : await askToSave(t)) {
    await saveRunResults(runData, scenarioName, options, t);
  }
  return runData;
}

async function askToSave(t) {
  const { saveResults } = await inquirer.prompt([
    { type: 'confirm', name: 'saveResults', message: 'Would you like to save the results of this run?', default: false, theme: t.promptTheme }
  ]);
  return saveResults;
}

/**
 * Save the results of a story run.
 * The user may pick a custom directory; the file name itself is always derived
 * from sanitised components and written inside that directory.
 */
async function saveRunResults(runData, scenarioName, options, t) {
  let outputDir = options.outputDir;
  if (!outputDir) {
    const defaultDir = path.join(ROOT_DIR, 'results', 'runs');
    const { saveOption } = await inquirer.prompt([
      {
        type: 'select',
        name: 'saveOption',
        message: 'Where would you like to save the results?',
        choices: [
          { name: 'Default location (results/runs/scenario-name/)', value: 'default' },
          { name: 'Custom location', value: 'custom' }
        ],
        default: 'default',
        theme: t.promptTheme
      }
    ]);
    outputDir = defaultDir;
    if (saveOption === 'custom') {
      const { customDir } = await inquirer.prompt([
        {
          type: 'input',
          name: 'customDir',
          message: 'Enter the output directory path (results go in <dir>/<scenario>/):',
          default: defaultDir,
          validate: (v) => (v.trim() && !v.includes('\0') ? true : 'Please enter a directory path'),
          theme: t.promptTheme
        }
      ]);
      outputDir = customDir.trim();
    }
  }

  const runId = newRunId();
  const outputPath = resultFilePath(outputDir, { scenario: scenarioName, runId, label: 'manual' });
  writeJsonExclusive(outputPath, {
    run_id: runId,
    scenario: scenarioName,
    player_type: 'human',
    timestamp: new Date().toISOString(),
    complete: true,
    choices: runData.choices,
    scores: runData.scores,
    verdict: runData.verdict
  });
  t.write(t.c.text(`\nResults saved to ${outputPath}`));
}
