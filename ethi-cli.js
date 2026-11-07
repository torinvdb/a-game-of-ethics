#!/usr/bin/env node

import { Command } from 'commander';
import inquirer from 'inquirer';
import { runManualMode } from './src/manual-player.js';
import { playInkStoryWithLLM, runMultipleGames, modelCommand } from './src/model-player.js';
import { listCoreScenarios } from './src/lib/scenarios.js';
import { redact } from './src/lib/llm.js';
import { ui } from './src/ui/theme.js';

const VERSION = '2.0.0';

function displayWelcomeBanner() {
  const t = ui();
  if (t.caps.tty) console.clear();
  t.write(t.banner({ version: VERSION.replace(/\.0$/, '') }));
}

/**
 * Display help information
 */
function displayHelp() {
  const t = ui();
  const h = (s) => t.c.sys(s);
  const lines = [
    h('COMMANDS'),
    '  manual                    Run in interactive manual mode to select and play scenarios',
    '  model <file>              Run scenarios with LLM players',
    '  list                      List the core scenarios',
    '  --interactive, -i         Launch the interactive menu interface',
    '  --no-anim                 Disable animation (or set ETHI_REDUCED_MOTION=1)',
    '  --help, -h                Display help information',
    '  --version, -V             Display version information',
    '',
    h('MANUAL MODE OPTIONS'),
    '  --compile                 Accepted for compatibility (.ink is compiled in-process)',
    '',
    h('MODEL MODE OPTIONS'),
    '  --model <model>           OpenRouter model to use (required)',
    "  --system-prompt <prompt>  Custom system prompt for the LLM's persona/character",
    '  -n, --num-runs <number>   Number of times to run the scenario (default: 1)',
    '  -o, --output-dir <dir>    Output directory for JSON results (default: ./results/runs)',
    '  --base-url <url>          OpenAI-compatible API base URL (default: OpenRouter)',
    '',
    h('ENVIRONMENT'),
    '  OPENROUTER_API_KEY        API key (read from env or .env; never printed)',
    '  ETHI_API_BASE_URL         Alternative OpenAI-compatible endpoint',
    '  ETHI_TIMEOUT_MS / ETHI_MAX_RETRIES / ETHI_PARSE_RETRIES',
    '  NO_COLOR, ETHI_REDUCED_MOTION, ETHI_ASCII',
    '',
    h('EXAMPLES'),
    '  node ethi-cli.js                     # interactive console',
    '  node ethi-cli.js manual',
    '  node ethi-cli.js list',
    '  node ethi-cli.js model scenarios/core/hostage-holdout.ink --model openai/gpt-4o',
    '  node ethi-cli.js model scenarios/core/rising-rebellion.ink --model openai/gpt-4o -n 5'
  ];
  t.write(t.panel(lines.map((l) => (l.startsWith('  ') ? t.c.text(l) : l)), { title: 'A GAME OF ETHICS // HELP' }));
}

const MODEL_OPTIONS = [
  { name: 'Claude 3.7 Sonnet (Anthropic)', value: 'anthropic/claude-3-7-sonnet:beta' },
  { name: 'GPT-4o (OpenAI)', value: 'openai/gpt-4o' },
  { name: 'Gemini 2.5 Flash (Google)', value: 'google/gemini-2.5-flash-preview' },
  { name: 'Llama 4 Scout (Meta)', value: 'meta-llama/llama-4-scout' },
  { name: 'Other (advanced)', value: 'other' }
];

function formatScenarioOptions(scenarios) {
  const t = ui();
  return [
    ...scenarios.map((s, i) => ({
      name: `${t.c.sys(`[${String(i + 1).padStart(2, '0')}]`)} ${t.c.info(s.tag)} ${t.c.text(s.title)}${s.desc ? t.c.dim(` - ${s.desc}`) : ''}`,
      short: s.title,
      value: s.file
    })),
    new inquirer.Separator(' '),
    { name: `${t.c.sys('[XX]')} ${t.c.steel('Back')}`, short: 'Back', value: 'exit' }
  ];
}

async function askToContinue() {
  const t = ui();
  const { continueRunning } = await inquirer.prompt([
    { type: 'confirm', name: 'continueRunning', message: 'Would you like to return to the main menu?', default: true, theme: t.promptTheme }
  ]);
  if (!continueRunning) t.write(t.c.info('\nLink closed. Goodbye.\n'));
  return continueRunning;
}

/**
 * Main interactive CLI mode
 */
async function runInteractiveMode() {
  const t = ui();
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    t.write('Interactive mode needs a terminal. Use a subcommand instead, e.g. `ethi-cli model <file> --model <id>`, or see --help.');
    process.exitCode = 1;
    return;
  }
  const scenarios = listCoreScenarios();
  displayWelcomeBanner();
  await t.boot({ scenarios: scenarios.length });

  while (true) {
    const { mode } = await inquirer.prompt([
      {
        type: 'select',
        name: 'mode',
        message: 'Select operation:',
        theme: t.promptTheme,
        choices: [
          { name: `${t.c.sys('[01]')} ${t.c.text('Run scenarios interactively')} ${t.c.dim('(human operator)')}`, short: 'Manual', value: 'manual' },
          { name: `${t.c.sys('[02]')} ${t.c.text('Run scenarios automatically')} ${t.c.dim('(model player)')}`, short: 'Model', value: 'model' },
          { name: `${t.c.sys('[03]')} ${t.c.text('Help and command reference')}`, short: 'Help', value: 'help' },
          { name: `${t.c.sys('[XX]')} ${t.c.steel('Disconnect')}`, short: 'Exit', value: 'exit' }
        ]
      }
    ]);

    if (mode === 'exit') {
      t.write(t.c.info('\nLink closed. Goodbye.\n'));
      return;
    }
    if (mode === 'help') {
      displayHelp();
      if (!(await askToContinue())) return;
      displayWelcomeBanner();
      continue;
    }

    try {
      if (mode === 'manual') {
        await runManualMode();
      } else if (mode === 'model') {
        if (scenarios.length === 0) {
          t.write(t.c.alert('No scenarios found in scenarios/core directory.'));
        } else {
          await runModelFromMenu(scenarios);
        }
      }
    } catch (error) {
      if (error?.name === 'ExitPromptError') throw error;
      t.write(t.c.alert(`Error: ${redact(error.message)}`));
    }

    if (!(await askToContinue())) return;
    displayWelcomeBanner();
  }
}

async function runModelFromMenu(scenarios) {
  const t = ui();
  const { scenarioPath } = await inquirer.prompt([
    { type: 'select', name: 'scenarioPath', message: 'Select a scenario to run:', choices: formatScenarioOptions(scenarios), pageSize: 14, theme: t.promptTheme }
  ]);
  if (scenarioPath === 'exit') return;

  const { model, numRuns, systemPrompt, otherModel } = await inquirer.prompt([
    { type: 'select', name: 'model', message: 'Select a model to use:', choices: MODEL_OPTIONS, theme: t.promptTheme },
    {
      type: 'input',
      name: 'otherModel',
      message: 'Enter the model identifier (e.g., openai/gpt-4o-2024-05-13):',
      when: (answers) => answers.model === 'other',
      validate: (input) => (input.trim() !== '' ? true : 'Please enter a valid model identifier'),
      theme: t.promptTheme
    },
    {
      type: 'input',
      name: 'numRuns',
      message: 'Number of runs to perform:',
      default: '1',
      validate: (input) => (/^\d+$/.test(input.trim()) && Number(input) > 0 && Number(input) <= 1000 ? true : 'Please enter a number between 1 and 1000'),
      theme: t.promptTheme
    },
    { type: 'input', name: 'systemPrompt', message: 'Custom system prompt (leave empty for default):', default: '', theme: t.promptTheme }
  ]);

  const selectedModel = (model === 'other' ? otherModel : model)?.trim();
  if (!selectedModel) {
    t.write(t.c.alert('Error: No model specified. Please select a valid model.'));
    return;
  }
  t.write(t.c.info(`\nStarting scenario with ${selectedModel}...\n`));
  const runs = Number.parseInt(numRuns, 10);
  const runOptions = { llmModel: selectedModel, systemPrompt, outputDir: './results/runs', generateSummary: false };
  if (runs > 1) await runMultipleGames(scenarioPath, { ...runOptions, numRuns: runs });
  else await playInkStoryWithLLM(scenarioPath, runOptions);
}

function listScenarios(options) {
  const t = ui();
  const scenarios = listCoreScenarios();
  if (options.json) {
    process.stdout.write(`${JSON.stringify(scenarios.map(({ id, file, title, desc }) => ({ id, file, title, desc })), null, 2)}\n`);
    return;
  }
  if (scenarios.length === 0) {
    t.write(t.c.alert('No scenarios found in scenarios/core directory.'));
    process.exitCode = 1;
    return;
  }
  const rows = scenarios.map((s, i) => `${t.c.sys(`[${String(i + 1).padStart(2, '0')}]`)} ${t.c.info(s.tag)} ${t.c.text(s.id.padEnd(22))} ${t.c.dim(s.desc)}`);
  t.write(t.panel(rows, { title: 'SCENARIO CORE', footer: `${scenarios.length} modules` }));
}

const program = new Command();
program
  .name('ethi-cli')
  .description('A Game of Ethics - Scenario-based alignment benchmark for LLMs')
  .version(VERSION)
  .option('-i, --interactive', 'Run in interactive menu mode')
  .option('--no-anim', 'Disable animation (same as ETHI_REDUCED_MOTION=1)')
  .option('--no-color', 'Disable colour output (same as NO_COLOR=1)')
  .action(() => runInteractiveMode())
  .addCommand(
    new Command('manual')
      .description('Run in interactive manual mode to select and play scenarios')
      .option('--compile', 'Accepted for compatibility; .ink files are always compiled in-process')
      .option('--no-anim', 'Disable animation')
      .action(async (options) => {
        if (!process.stdin.isTTY) {
          ui().write('Manual mode needs an interactive terminal.');
          process.exitCode = 1;
          return;
        }
        await runManualMode(options);
      })
  )
  .addCommand(modelCommand('model'))
  .addCommand(
    new Command('list')
      .description('List the core scenarios')
      .option('--json', 'Output machine-readable JSON')
      .action(listScenarios)
  );

program.parseAsync().catch((error) => {
  if (error?.name === 'ExitPromptError') {
    // Ctrl-C inside a prompt: exit quietly.
    process.stdout.write('\n');
    process.exitCode = 130;
    return;
  }
  process.stderr.write(`Error: ${redact(error?.message ?? String(error))}\n`);
  process.exitCode = 1;
});
