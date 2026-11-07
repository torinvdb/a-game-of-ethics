#!/usr/bin/env node

import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Command } from 'commander';
import { loadEnv } from './lib/env.js';
import { loadStory, readVariables } from './lib/ink.js';
import { AdapterError, askModelForChoice, resolveAdapterConfig, redact, PROMPT_VERSION } from './lib/llm.js';
import { AXES, AXIS_NAMES, summarizeScores } from './lib/scoring.js';
import { newRunId, resolveScenarioFile, resultFilePath, scenarioIdFromPath, writeJsonExclusive } from './lib/paths.js';
import { ui } from './ui/theme.js';

loadEnv();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const DEFAULT_OUTPUT_DIR = path.join(rootDir, 'results', 'runs');

function parseNumRuns(value) {
  const n = Number.parseInt(value ?? '1', 10);
  if (!Number.isInteger(n) || n < 1 || n > 1000) {
    throw new Error(`--num-runs must be an integer between 1 and 1000 (got "${value}")`);
  }
  return n;
}

/**
 * Run a scenario multiple times with an LLM
 * @param {string} filePath - Path to the ink story file
 * @param {Object} options - { llmModel, systemPrompt, numRuns, outputDir }
 * @returns {Object[]} Data from each run (failed runs have complete=false)
 */
export async function runMultipleGames(filePath, options) {
  const t = ui();
  const numRuns = parseNumRuns(options.numRuns);
  const scenarioFile = resolveScenarioFile(filePath);
  t.write(t.c.sys(`> QUEUEING ${numRuns} RUNS // ${options.llmModel}`));

  const results = [];
  for (let i = 0; i < numRuns; i++) {
    t.write();
    t.write(t.rule(`RUN ${i + 1}/${numRuns}`, t.c.info));
    try {
      const runData = await playInkStoryWithLLM(scenarioFile, { ...options, numRuns, _batch: true });
      results.push(runData);
      if (runData.complete) {
        t.write(t.c.text(`Run ${i + 1} completed with verdict: ${runData.verdict || 'Unknown'}  total ${t.signed(runData.scores.total || 0)}`));
      } else {
        t.write(t.c.alert(`Run ${i + 1} INCOMPLETE: ${runData.adapter_failure?.kind} - ${runData.adapter_failure?.message}`));
      }
    } catch (error) {
      t.write(t.c.alert(`Error in run ${i + 1}: ${redact(error.message)}`));
      results.push({ complete: false, adapter_failure: { kind: 'execution', message: redact(error.message) }, choices: [], scores: {} });
    }
  }

  const scenarioName = scenarioIdFromPath(scenarioFile);
  const runId = newRunId();
  const outputPath = resultFilePath(options.outputDir || DEFAULT_OUTPUT_DIR, {
    scenario: scenarioName,
    runId,
    label: options.llmModel.split('/').pop()
  });
  const completed = results.filter((r) => r.complete);
  writeJsonExclusive(outputPath, {
    run_id: runId,
    scenario: scenarioName,
    model: options.llmModel,
    systemPrompt: options.systemPrompt || '',
    prompt_version: PROMPT_VERSION,
    numRuns,
    completed_runs: completed.length,
    failed_runs: results.length - completed.length,
    timestamp: new Date().toISOString(),
    runs: results.map(stripTranscript)
  });

  t.write(t.c.text(`\nAll runs finished (${completed.length}/${numRuns} complete). Results saved to ${outputPath}`));
  displayAggregateStats(completed);
  if (completed.length < results.length) process.exitCode = 2;
  return results;
}

function stripTranscript(run) {
  const { text, ...rest } = run;
  return rest;
}

function stats(values) {
  const avg = values.reduce((s, v) => s + v, 0) / values.length;
  return { avg, min: Math.min(...values), max: Math.max(...values) };
}

/** Display aggregate statistics from completed runs */
function displayAggregateStats(results) {
  const t = ui();
  if (results.length === 0) {
    t.write(t.c.alert('\nNo run completed; no aggregate statistics.'));
    return;
  }
  const lines = [];
  const mean = {};
  for (const axis of [...AXES, 'average', 'total']) {
    const values = results.map((r) => r.scores?.[axis]).filter(Number.isFinite);
    if (!values.length) continue;
    const s = stats(values);
    mean[axis] = s.avg;
    lines.push(
      `${t.c.info((AXIS_NAMES[axis] || axis).padEnd(24))} ${t.c.text(t.signed(s.avg).padStart(7))}   ${t.c.dim(`${t.signed(s.min)} .. ${t.signed(s.max)}`)}`
    );
  }
  const counts = {};
  for (const r of results) {
    const key = (r.verdict || 'UNKNOWN').split(' - ')[0];
    counts[key] = (counts[key] || 0) + 1;
  }
  lines.push('', t.c.sys('VERDICT DISTRIBUTION'));
  for (const [verdict, count] of Object.entries(counts)) {
    const pct = ((count / results.length) * 100).toFixed(1);
    const tone = ['EXEMPLARY', 'RESPONSIBLE'].includes(verdict) ? t.c.good : verdict === 'AMBIGUOUS' ? t.c.warn : t.c.bad;
    lines.push(tone(`${verdict}: ${count} runs (${pct}%)`));
  }
  t.write();
  t.write(t.panel(lines, { title: 'AGGREGATE STATISTICS', footer: `${results.length} runs` }));
  t.write(t.axisStatus(mean));
}

/**
 * Play an Ink story with an LLM making the choices.
 *
 * Adapter/execution errors end the run with complete=false and `adapter_failure`;
 * no verdict is produced and errors are never recorded as choices.
 *
 * @param {string} filePath - Path to the ink story file
 * @param {Object} options - { llmModel, systemPrompt, outputDir, numRuns, adapter }
 * @returns {Object} Data collected from the story run
 */
export async function playInkStoryWithLLM(filePath, options = {}) {
  const t = ui();
  const scenarioFile = resolveScenarioFile(filePath);
  const scenarioName = scenarioIdFromPath(scenarioFile);
  // Resolve adapter config first so misconfiguration fails fast.
  const adapter = resolveAdapterConfig(options.adapter);
  const story = loadStory(scenarioFile);

  t.write(t.rule(`LINK // ${options.llmModel || 'no-model'} >> ${scenarioName}`, t.c.accent));

  const runData = { complete: false, adapter_failure: null, choices: [], scores: {}, text: [] };
  let context = '';
  let step = 0;

  while (true) {
    const texts = [];
    while (story.canContinue) {
      const text = story.Continue().trim();
      if (text) texts.push(text);
    }
    if (texts.length) {
      runData.text.push(...texts);
      context += `${texts.join('\n')}\n`;
      t.write(t.panel(texts.join('\n'), { title: `FEED ${String(step).padStart(2, '0')}`, footer: scenarioName }));
    }

    if (story.currentChoices.length === 0) break;

    const choices = story.currentChoices.map((choice) => choice.text);
    t.write(t.c.sys('OPTIONS UNDER EVALUATION:'));
    t.menuChoices(choices).forEach((c) => t.write(`  ${c.name}`));
    t.write(t.c.dim('... awaiting inference relay'));

    let decision;
    try {
      decision = await askModelForChoice(adapter, {
        context,
        choices,
        model: options.llmModel,
        systemPrompt: options.systemPrompt
      });
    } catch (error) {
      const failure =
        error instanceof AdapterError
          ? { ...error.toJSON(), at_step: step, options: choices }
          : { kind: 'execution', message: redact(error.message), at_step: step, options: choices };
      if (failure.raw_content !== undefined) failure.raw_content = redact(failure.raw_content).slice(0, 4000);
      runData.adapter_failure = failure;
      t.write(t.c.alert(`ADAPTER FAILURE [${failure.kind}] ${redact(failure.message)}`));
      t.write(t.c.alert('Run aborted: no choice recorded, no verdict issued.'));
      break;
    }

    const selected = decision.index;
    t.write(t.c.accent(`MODEL CHOSE [${String(selected + 1).padStart(2, '0')}] ${choices[selected]}`) + t.c.dim(`  (${decision.method})`));
    t.write(t.c.steel(decision.reasoning));

    runData.choices.push({
      options: choices,
      selected,
      text: choices[selected],
      reasoning: decision.reasoning,
      parse_method: decision.method,
      attempts: decision.attempts
    });
    story.ChooseChoiceIndex(selected);
    context += `\nI chose: ${choices[selected]}\n`;
    step++;
    t.write(t.axisStatus(readVariables(story)));
  }

  if (!runData.adapter_failure) {
    const summary = summarizeScores(readVariables(story));
    runData.complete = true;
    runData.scores = summary.scores;
    runData.verdict = summary.verdict.text;
    if (summary.axisCount === 0) t.write(t.c.sys('No score variables found in story.'));
    t.write(t.verdictScreen({ scores: summary.scores, average: summary.average, total: summary.total, actor: options.llmModel }));
  }

  // Single runs save their own file; batches are saved by runMultipleGames.
  if (!options._batch) {
    const runId = newRunId();
    const outputPath = resultFilePath(options.outputDir || DEFAULT_OUTPUT_DIR, {
      scenario: scenarioName,
      runId,
      label: options.llmModel ? options.llmModel.split('/').pop() : 'unknown-model'
    });
    writeJsonExclusive(outputPath, {
      run_id: runId,
      scenario: scenarioName,
      model: options.llmModel,
      systemPrompt: options.systemPrompt || '',
      prompt_version: PROMPT_VERSION,
      timestamp: new Date().toISOString(),
      complete: runData.complete,
      adapter_failure: runData.adapter_failure,
      choices: runData.choices,
      scores: runData.complete ? runData.scores : {},
      verdict: runData.verdict ?? null
    });
    t.write(t.c.text(`\nResults saved to ${outputPath}`));
    if (!runData.complete) process.exitCode = 2;
  }

  return runData;
}

/** Build the `model` commander command (shared by ethi-cli.js and direct execution). */
export function modelCommand(name = 'model') {
  return new Command(name)
    .description('Run scenarios with LLM players')
    .option('-c, --compile', 'Accepted for compatibility; .ink files are always compiled in-process')
    .requiredOption('--model <model>', 'OpenRouter model to use (required)')
    .option('--system-prompt <prompt>', "Custom system prompt for the LLM's persona/character", '')
    .option('-n, --num-runs <number>', 'Number of times to run the scenario', '1')
    .option('-o, --output-dir <dir>', 'Output directory for JSON results', './results/runs')
    .option('--generate-summary', 'Accepted for compatibility (not implemented)')
    .option('--base-url <url>', 'OpenAI-compatible API base URL (default: $ETHI_API_BASE_URL or OpenRouter)')
    .option('--no-anim', 'Disable animation (same as ETHI_REDUCED_MOTION=1)')
    .argument('<file>', 'Path to a compiled .ink.json file or an .ink file')
    .action(async (filePath, options) => {
      const t = ui();
      try {
        const numRuns = parseNumRuns(options.numRuns);
        const runOptions = {
          llmModel: options.model,
          systemPrompt: options.systemPrompt,
          outputDir: options.outputDir,
          generateSummary: options.generateSummary,
          adapter: options.baseUrl ? { baseUrl: options.baseUrl } : undefined
        };
        if (numRuns > 1) await runMultipleGames(filePath, { ...runOptions, numRuns });
        else await playInkStoryWithLLM(filePath, runOptions);
      } catch (error) {
        t.write(t.c.alert(`Error: ${redact(error.message)}`));
        process.exitCode = 1;
      }
    });
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  modelCommand('model-player').version('2.0.0').parseAsync().catch((error) => {
    process.stderr.write(`Error: ${redact(error.message)}\n`);
    process.exitCode = 1;
  });
}
