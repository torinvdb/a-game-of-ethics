#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { Command } from 'commander';
import { listFilesRecursive } from './lib/paths.js';
import { fileURLToPath } from 'url';
import BaseTable from 'cli-table3';
import { detectCapabilities } from './ui/theme.js';
import { createSpinner } from 'nanospinner';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

const axisNames = {
  'hc': 'Harm/Care',
  'fj': 'Fairness/Justice',
  'ar': 'Autonomy/Respect',
  'al': 'Authority/Legitimacy',
  'lt': 'Loyalty/Trust',
  'it': 'Integrity/Truth',
  'sp': 'Sanctity/Purity',
  'uc': 'Utility/Consequences',
  'total': 'Total',
  'average': 'Average'
};

const ethicalAxes = ['hc', 'fj', 'ar', 'al', 'lt', 'it', 'sp', 'uc'];

// cli-table3 colours borders/headers on its own; honour NO_COLOR / non-TTY.
const COLOR = detectCapabilities().colorLevel > 0;
chalk.level = COLOR ? chalk.level || 1 : 0;
class Table extends BaseTable {
  constructor(options = {}) {
    super(COLOR ? options : { ...options, style: { ...(options.style || {}), head: [], border: [] } });
  }
}

// Local stand-ins for the lodash helpers used here (avoids the dependency).
const _ = {
  groupBy: (items, key) =>
    items.reduce((acc, item) => {
      const k = String(item?.[key]);
      (acc[k] ||= []).push(item);
      return acc;
    }, {}),
  sum: (xs) => xs.reduce((a, b) => a + b, 0),
  mean: (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : NaN),
  sortBy: (xs) => [...xs].sort((a, b) => a - b),
  min: (xs) => (xs.length ? Math.min(...xs) : undefined),
  max: (xs) => (xs.length ? Math.max(...xs) : undefined)
};

/** Escape one CSV field (RFC 4180) and neutralise spreadsheet formula injection. */
export function csvField(value) {
  if (value === undefined || value === null) return '';
  let s = String(value);
  if (/^[=+\-@\t\r]/.test(s) && !/^-?\d+(\.\d+)?$/.test(s)) s = `'${s}`;
  return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

/**
 * Find all result JSON files in a directory
 * @param {string} directory - The directory to search in
 * @returns {Promise<string[]>} Paths to all JSON files
 */
async function findResultFiles(directory) {
  try {
    return listFilesRecursive(directory, (name) => name.endsWith('.json'));
  } catch (error) {
    console.error(chalk.red(`Error reading directory: ${error.message}`));
    return [];
  }
}

/**
 * Check if a file is a valid run result file by examining its structure
 * @param {string} filePath - Path to the file
 * @returns {Promise<boolean>} Whether it's a valid result file
 */
async function isValidResultFile(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    
    // Runs that ended in an adapter failure have no verdict and must not be scored.
    if (data?.complete === false) return false;
    const hasSingleRunFormat = data?.choices?.length && typeof data?.scores === 'object';
    const hasMultiRunFormat = data?.runs?.some?.((run) => run?.complete !== false);
    
    return hasSingleRunFormat || hasMultiRunFormat;
  } catch (error) {
    return false;
  }
}

/**
 * Parse a run file and extract relevant data
 * @param {string} filePath - Path to the result file
 * @returns {Object[]} Extracted run data
 */
function parseRunFile(filePath) {
  try {
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const scenarioName = data.scenario || path.basename(path.dirname(filePath));
    
    if (data.runs?.length) {
      return data.runs.flatMap((run, i) => (run?.complete === false ? [] : [{
        file_path: filePath,
        run_id: `${data.run_id || 'batch'}-${i + 1}`,
        scenario: scenarioName,
        model: data.model || 'unknown',
        player_type: data.player_type ? data.player_type : (data.player === 'human' ? 'manual' : 'model'),
        system_prompt: data.systemPrompt || '',
        timestamp: data.timestamp || new Date().toISOString(),
        scores: run.scores || {},
        verdict: run.verdict || '',
        choice_count: run.choices?.length || 0
      }]));
    }
    
    return [{
      file_path: filePath,
      run_id: data.run_id || path.basename(filePath, '.json'),
      scenario: scenarioName,
      model: data.model || (data.player_type === 'human' || data.player === 'human' ? 'human' : 'unknown'),
      player_type: data.player_type === 'human' || data.player === 'human' ? 'manual' : 'model',
      system_prompt: data.systemPrompt || '',
      timestamp: data.timestamp || new Date().toISOString(),
      scores: data.scores || {},
      verdict: data.verdict || '',
      choice_count: data.choices?.length || 0
    }];
  } catch (error) {
    console.error(chalk.red(`Error parsing ${filePath}: ${error.message}`));
    return [];
  }
}

/**
 * Calculate statistics for a set of runs
 * @param {Object[]} runs - Array of run data
 * @returns {Object} Statistics object
 */
function calculateStatistics(runs) {
  const stats = {
    count: runs.length,
    by_player_type: {},
    by_model: {},
    by_scenario: {},
    by_verdict: {},
    score_stats: {},
    ethical_bias: {}
  };
  
  const allAxes = [...ethicalAxes, 'total', 'average'];
  const axisScores = {};
  const axisRanksCounter = {};
  
  allAxes.forEach(axis => {
    axisScores[axis] = [];
  });
  
  for (let i = 0; i < ethicalAxes.length; i++) {
    axisRanksCounter[`rank_${i + 1}`] = {};
    ethicalAxes.forEach(axis => {
      axisRanksCounter[`rank_${i + 1}`][axis] = 0;
    });
  }
  
  const groupedData = {
    player_type: _.groupBy(runs, 'player_type'),
    scenario: _.groupBy(runs, 'scenario'),
    verdict: _.groupBy(runs, 'verdict')
  };
  
  Object.entries(groupedData.player_type).forEach(([type, typeRuns]) => {
    stats.by_player_type[type] = typeRuns.length;
  });
  
  Object.entries(groupedData.scenario).forEach(([scenario, scenarioRuns]) => {
    stats.by_scenario[scenario] = scenarioRuns.length;
  });
  
  runs.forEach(run => {
    allAxes.forEach(axis => {
      const score = run.scores?.[axis];
      if (score !== undefined && score !== null) {
        axisScores[axis].push(score);
      }
    });
    
    if (run.player_type === 'model' && run.model) {
      stats.by_model[run.model] = (stats.by_model[run.model] || 0) + 1;
    }
    
    if (run.verdict) {
      const shortVerdict = run.verdict.split(' - ')[0];
      stats.by_verdict[shortVerdict] = (stats.by_verdict[shortVerdict] || 0) + 1;
    }
    
    if (run.scores) {
      const axisRanking = ethicalAxes
        .map(axis => ({ axis, score: run.scores[axis] || 0 }))
        .sort((a, b) => b.score - a.score);
      
      axisRanking.forEach((item, index) => {
        axisRanksCounter[`rank_${index + 1}`][item.axis]++;
      });
    }
  });
  
  allAxes.forEach(axis => {
    const scores = axisScores[axis];
    if (scores.length > 0) {
      const sortedScores = [...scores].sort((a, b) => a - b);
      const mean = _.mean(scores);
      
      stats.score_stats[axis] = {
        mean,
        median: sortedScores[Math.floor(scores.length / 2)],
        min: sortedScores[0],
        max: sortedScores[scores.length - 1],
        std_dev: Math.sqrt(_.sum(scores.map(s => Math.pow(s - mean, 2))) / scores.length)
      };
    }
  });
  
  stats.ethical_bias = axisRanksCounter;
  
  return stats;
}

/**
 * Compare different groups of runs (by scenario, model, etc.)
 * @param {Object[]} runs - All runs
 * @param {string} groupBy - Property to group by ('scenario', 'model', etc.)
 * @returns {Object} Comparison results
 */
function compareGroups(runs, groupBy) {
  const groups = _.groupBy(runs, groupBy);
  const comparison = {};
  
  for (const [groupName, groupRuns] of Object.entries(groups)) {
    if (groupRuns.length > 0) {
      comparison[groupName] = {};
      
      for (const axis of [...ethicalAxes, 'total', 'average']) {
        const scores = groupRuns.map(run => run.scores[axis]).filter(s => s !== undefined);
        if (scores.length > 0) {
          comparison[groupName][axis] = _.mean(scores);
        }
      }
      
      const verdicts = {};
      for (const run of groupRuns) {
        if (run.verdict) {
          const shortVerdict = run.verdict.split(' - ')[0];
          verdicts[shortVerdict] = (verdicts[shortVerdict] || 0) + 1;
        }
      }
      comparison[groupName].verdicts = verdicts;
      
      comparison[groupName].count = groupRuns.length;
    }
  }
  
  return comparison;
}

/**
 * Compare player types (manual vs model)
 * @param {Object[]} runs - All runs
 * @returns {Object} Comparison results
 */
function comparePlayerTypes(runs) {
  const manualRuns = runs.filter(run => run.player_type === 'manual');
  const modelRuns = runs.filter(run => run.player_type === 'model');
  
  if (manualRuns.length === 0 || modelRuns.length === 0) {
    return null;
  }
  
  const comparison = {
    manual: calculateTypeStats(manualRuns),
    model: calculateTypeStats(modelRuns)
  };
  
  return comparison;
}

/**
 * Calculate stats for a specific player type or model
 * @param {Object[]} runs - Runs to analyze
 * @returns {Object} Stats for the player type
 */
function calculateTypeStats(runs) {
  const stats = {
    count: runs.length,
    axis_scores: {},
    verdicts: {}
  };
  
  for (const axis of [...ethicalAxes, 'total', 'average']) {
    const scores = runs.map(run => run.scores[axis]).filter(s => s !== undefined);
    if (scores.length > 0) {
      stats.axis_scores[axis] = {
        mean: _.mean(scores),
        median: _.sortBy(scores)[Math.floor(scores.length / 2)],
        min: _.min(scores),
        max: _.max(scores)
      };
    }
  }
  
  for (const run of runs) {
    if (run.verdict) {
      const shortVerdict = run.verdict.split(' - ')[0];
      stats.verdicts[shortVerdict] = (stats.verdicts[shortVerdict] || 0) + 1;
    }
  }
  
  return stats;
}

/**
 * Compare models against each other (if multiple models exist)
 * @param {Object[]} runs - All runs
 * @returns {Object} Comparison results
 */
function compareModels(runs) {
  const modelRuns = runs.filter(run => run.player_type === 'model');
  
  const modelGroups = _.groupBy(modelRuns, 'model');
  const models = Object.keys(modelGroups);
  
  // Skip if not enough data (need at least 2 models)
  if (models.length < 2) {
    return null;
  }
  
  const comparison = {};
  for (const model of models) {
    comparison[model] = calculateTypeStats(modelGroups[model]);
  }
  
  return comparison;
}

/**
 * Generate an output CSV file with all run data
 * @param {Object[]} runs - Array of run data
 * @param {string} outputPath - Path to save the CSV file
 * @returns {Promise<void>}
 */
async function generateCsvOutput(runs, outputPath) {
  const header = [
    { id: 'run_id', title: 'Run ID' },
    { id: 'scenario', title: 'Scenario' },
    { id: 'model', title: 'Model' },
    { id: 'player_type', title: 'Player Type' },
    { id: 'system_prompt', title: 'System Prompt' },
    { id: 'timestamp', title: 'Timestamp' },
    { id: 'choice_count', title: 'Choice Count' },
    { id: 'verdict', title: 'Verdict' }
  ];
  
  for (const axis of ethicalAxes) {
    header.push({ id: `scores.${axis}`, title: axisNames[axis] });
  }
  
  header.push({ id: 'scores.total', title: 'Total Score' });
  header.push({ id: 'scores.average', title: 'Average Score' });
  
  
  const records = runs.map(run => {
    const record = { ...run };
    
    for (const axis of [...ethicalAxes, 'total', 'average']) {
      record[`scores.${axis}`] = run.scores[axis];
    }
    
    return record;
  });
  
  const lines = [header.map((h) => csvField(h.title)).join(',')];
  for (const record of records) {
    lines.push(header.map((h) => csvField(record[h.id])).join(','));
  }
  fs.writeFileSync(outputPath, `${lines.join('\n')}\n`);
  console.log(chalk.green(`\nCSV file successfully written to ${outputPath}`));
}

/**
 * Display statistics in console
 * @param {Object} stats - Statistics object
 */
function displayStatistics(stats) {
  console.log(chalk.cyan('\n===== ANALYSIS SUMMARY =====\n'));
  
  console.log(chalk.bold(`Total Runs: ${stats.count}`));
  
  if (Object.keys(stats.by_player_type).length > 0) {
    console.log(chalk.cyan('\nRuns by Player Type:'));
    for (const [playerType, count] of Object.entries(stats.by_player_type)) {
      console.log(`  ${playerType}: ${count} runs (${((count / stats.count) * 100).toFixed(1)}%)`);
    }
  }
  
  if (Object.keys(stats.by_model).length > 0) {
    console.log(chalk.cyan('\nRuns by Model:'));
    for (const [model, count] of Object.entries(stats.by_model)) {
      console.log(`  ${model}: ${count} runs (${((count / stats.count) * 100).toFixed(1)}%)`);
    }
  }
  
  if (Object.keys(stats.by_scenario).length > 0) {
    console.log(chalk.cyan('\nRuns by Scenario:'));
    for (const [scenario, count] of Object.entries(stats.by_scenario)) {
      console.log(`  ${scenario}: ${count} runs (${((count / stats.count) * 100).toFixed(1)}%)`);
    }
  }
  
  if (Object.keys(stats.by_verdict).length > 0) {
    console.log(chalk.cyan('\nVerdict Distribution:'));
    for (const [verdict, count] of Object.entries(stats.by_verdict)) {
      const percentage = ((count / stats.count) * 100).toFixed(1);
      const color = verdict === 'EXEMPLARY' || verdict === 'RESPONSIBLE' ? 'green' : 
                   verdict === 'AMBIGUOUS' ? 'yellow' : 'red';
      
      console.log(chalk[color](`  ${verdict}: ${count} runs (${percentage}%)`));
    }
  }
  
  console.log(chalk.cyan('\nScore Statistics:'));
  
  const scoreTable = new Table({
    head: [
      chalk.cyan('Ethical Axis'), 
      chalk.cyan('Mean'), 
      chalk.cyan('Median'),
      chalk.cyan('Min'),
      chalk.cyan('Max'), 
      chalk.cyan('Std Dev')
    ],
    colWidths: [20, 10, 10, 10, 10, 10]
  });
  
  for (const axis of ethicalAxes) {
    const stats_axis = stats.score_stats[axis];
    if (stats_axis) {
      scoreTable.push([
        axisNames[axis],
        stats_axis.mean.toFixed(2),
        stats_axis.median.toFixed(2),
        stats_axis.min.toFixed(2),
        stats_axis.max.toFixed(2),
        stats_axis.std_dev.toFixed(2)
      ]);
    }
  }
  
  for (const extraAxis of ['total', 'average']) {
    const stats_axis = stats.score_stats[extraAxis];
    if (stats_axis) {
      const row = [
        chalk.bold(axisNames[extraAxis]),
        chalk.bold(stats_axis.mean.toFixed(2)),
        chalk.bold(stats_axis.median.toFixed(2)),
        chalk.bold(stats_axis.min.toFixed(2)),
        chalk.bold(stats_axis.max.toFixed(2)),
        chalk.bold(stats_axis.std_dev.toFixed(2))
      ];
      scoreTable.push(row);
    }
  }
  
  console.log(scoreTable.toString());
  
  console.log(chalk.cyan('\nEthical Axis Ranking Frequency:'));
  console.log(chalk.yellow('(Shows how often each ethical axis appears at each rank position across all runs)'));
  console.log(chalk.yellow('(Rank 1 = highest score in a run, Rank 8 = lowest score)'));
  
  const biasTable = new Table({
    head: [
      chalk.cyan('Ethical Axis'),
      ...ethicalAxes.map((_, i) => chalk.cyan(`Rank ${i + 1}`))
    ],
    colWidths: [20, ...Array(ethicalAxes.length).fill(10)]
  });
  
  for (const axis of ethicalAxes) {
    const row = [axisNames[axis]];
    
    for (let i = 0; i < ethicalAxes.length; i++) {
      const count = stats.ethical_bias[`rank_${i + 1}`][axis] || 0;
      const percentage = ((count / stats.count) * 100).toFixed(1);
      row.push(`${count} (${percentage}%)`);
    }
    
    biasTable.push(row);
  }
  
  console.log(biasTable.toString());
  console.log(chalk.yellow('Interpretation: Higher percentages in Rank 1 indicate dimensions that frequently receive the highest scores.'));
  console.log(chalk.yellow('This reveals which ethical dimensions tend to be prioritized or de-prioritized in decisions.'));
}

/**
 * Display comparison results
 * @param {Object} comparison - Comparison results
 * @param {string} groupBy - What was compared
 */
function displayComparison(comparison, groupBy) {
  console.log(chalk.cyan(`\n===== COMPARISON BY ${groupBy.toUpperCase()} =====\n`));
  
  const comparisonTable = new Table({
    head: [
      chalk.cyan(groupBy.charAt(0).toUpperCase() + groupBy.slice(1)),
      chalk.cyan('Count'),
      ...ethicalAxes.map(axis => chalk.cyan(axisNames[axis])),
      chalk.cyan('Total'),
      chalk.cyan('Avg'),
      chalk.cyan('Top Verdict')
    ]
  });
  
  for (const [groupName, data] of Object.entries(comparison)) {
    let topVerdict = '';
    let topVerdictCount = 0;
    
    if (data.verdicts) {
      for (const [verdict, count] of Object.entries(data.verdicts)) {
        if (count > topVerdictCount) {
          topVerdict = verdict;
          topVerdictCount = count;
        }
      }
    }
    
    const percentage = data.count ? ((topVerdictCount / data.count) * 100).toFixed(1) : '0.0';
    const topVerdictDisplay = topVerdict ? `${topVerdict} (${percentage}%)` : 'N/A';
    
    const row = [
      groupName,
      data.count || 0
    ];
    
    for (const axis of ethicalAxes) {
      row.push(data[axis] !== undefined ? data[axis].toFixed(2) : 'N/A');
    }
    
    row.push(data.total !== undefined ? data.total.toFixed(2) : 'N/A');
    row.push(data.average !== undefined ? data.average.toFixed(2) : 'N/A');
    
    row.push(topVerdictDisplay);
    
    comparisonTable.push(row);
  }
  
  console.log(comparisonTable.toString());
}

/**
 * Display player type comparison (manual vs model)
 * @param {Object} comparison - Comparison results
 */
function displayPlayerTypeComparison(comparison) {
  if (!comparison) return;
  
  console.log(chalk.cyan('\n===== MANUAL VS MODEL COMPARISON =====\n'));
  
  const comparisonTable = new Table({
    head: [
      chalk.cyan('Metric'),
      chalk.cyan('Manual Players'),
      chalk.cyan('Model Players'),
      chalk.cyan('Difference')
    ],
    colWidths: [20, 15, 15, 15]
  });
  
  comparisonTable.push([
    'Run Count',
    comparison.manual.count,
    comparison.model.count,
    'N/A'
  ]);
  
  for (const axis of ethicalAxes) {
    if (comparison.manual.axis_scores[axis] && comparison.model.axis_scores[axis]) {
      const manualMean = comparison.manual.axis_scores[axis].mean;
      const modelMean = comparison.model.axis_scores[axis].mean;
      const diff = modelMean - manualMean;
      const diffFormatted = diff > 0 ? chalk.green(`+${diff.toFixed(2)}`) : 
                           diff < 0 ? chalk.red(diff.toFixed(2)) : 
                           chalk.yellow('0.00');
      
      comparisonTable.push([
        axisNames[axis],
        manualMean.toFixed(2),
        modelMean.toFixed(2),
        diffFormatted
      ]);
    }
  }
  
  if (comparison.manual.axis_scores.average && comparison.model.axis_scores.average) {
    const manualAvg = comparison.manual.axis_scores.average.mean;
    const modelAvg = comparison.model.axis_scores.average.mean;
    const diff = modelAvg - manualAvg;
    const diffFormatted = diff > 0 ? chalk.green(`+${diff.toFixed(2)}`) : 
                         diff < 0 ? chalk.red(diff.toFixed(2)) : 
                         chalk.yellow('0.00');
    
    comparisonTable.push([
      chalk.bold('Average Score'),
      chalk.bold(manualAvg.toFixed(2)),
      chalk.bold(modelAvg.toFixed(2)),
      chalk.bold(diffFormatted)
    ]);
  }
  
  console.log(comparisonTable.toString());
  
  console.log(chalk.cyan('\nVerdict Distribution Comparison:'));
  
  const verdictTable = new Table({
    head: [
      chalk.cyan('Verdict'),
      chalk.cyan('Manual (%)'),
      chalk.cyan('Model (%)')
    ],
    colWidths: [15, 15, 15]
  });
  
  const allVerdicts = new Set([
    ...Object.keys(comparison.manual.verdicts || {}),
    ...Object.keys(comparison.model.verdicts || {})
  ]);
  
  for (const verdict of allVerdicts) {
    const manualCount = comparison.manual.verdicts[verdict] || 0;
    const modelCount = comparison.model.verdicts[verdict] || 0;
    
    const manualPct = ((manualCount / comparison.manual.count) * 100).toFixed(1);
    const modelPct = ((modelCount / comparison.model.count) * 100).toFixed(1);
    
    verdictTable.push([
      verdict,
      manualCount > 0 ? `${manualPct}%` : '0.0%',
      modelCount > 0 ? `${modelPct}%` : '0.0%'
    ]);
  }
  
  console.log(verdictTable.toString());
  
  console.log(chalk.yellow('\nInterpretation:'));
  console.log('- Score differences show how model ethical priorities compare to human players');
  console.log('- Positive differences (green) indicate models score higher on that dimension than humans');
  console.log('- Negative differences (red) show dimensions where humans score higher than models');
  console.log('- Verdict distribution reveals how often models vs humans reach different ethical conclusions');
  console.log('- Large differences may indicate model alignment gaps with human ethical intuitions');
}

/**
 * Display model comparison
 * @param {Object} comparison - Comparison results
 */
function displayModelComparison(comparison) {
  if (!comparison) return;
  
  console.log(chalk.cyan('\n===== MODEL COMPARISON =====\n'));
  
  console.log(chalk.cyan('Ethical Axis Scores by Model:'));
  
  const models = Object.keys(comparison);
  const scoreTable = new Table({
    head: [
      chalk.cyan('Ethical Axis'),
      ...models.map(model => chalk.cyan(model.split('/').pop()))
    ],
    colWidths: [20, ...Array(models.length).fill(Math.max(15, Math.floor(80 / (models.length + 1))))]
  });
  
  for (const axis of ethicalAxes) {
    const row = [axisNames[axis]];
    
    for (const model of models) {
      const modelStats = comparison[model];
      if (modelStats.axis_scores[axis]) {
        row.push(modelStats.axis_scores[axis].mean.toFixed(2));
      } else {
        row.push('N/A');
      }
    }
    
    scoreTable.push(row);
  }
  
  const avgRow = [chalk.bold('Average Score')];
  for (const model of models) {
    const modelStats = comparison[model];
    if (modelStats.axis_scores.average) {
      avgRow.push(chalk.bold(modelStats.axis_scores.average.mean.toFixed(2)));
    } else {
      avgRow.push(chalk.bold('N/A'));
    }
  }
  scoreTable.push(avgRow);
  
  console.log(scoreTable.toString());
  
  console.log(chalk.cyan('\nVerdict Distribution by Model:'));
  
  const allVerdicts = new Set();
  for (const model of models) {
    Object.keys(comparison[model].verdicts || {}).forEach(v => allVerdicts.add(v));
  }
  
  const verdictTable = new Table({
    head: [
      chalk.cyan('Verdict'),
      ...models.map(model => chalk.cyan(model.split('/').pop()))
    ],
    colWidths: [15, ...Array(models.length).fill(Math.max(15, Math.floor(80 / (models.length + 1))))]
  });
  
  for (const verdict of allVerdicts) {
    const row = [verdict];
    
    for (const model of models) {
      const modelStats = comparison[model];
      const count = modelStats.verdicts[verdict] || 0;
      const percentage = ((count / modelStats.count) * 100).toFixed(1);
      row.push(count > 0 ? `${percentage}% (${count})` : '0.0%');
    }
    
    verdictTable.push(row);
  }
  
  console.log(verdictTable.toString());
  
  console.log(chalk.yellow('\nInterpretation:'));
  console.log('- Higher axis scores indicate the model prioritizes that ethical dimension more strongly');
  console.log('- Verdict distribution shows each model\'s tendency toward different ethical judgments');
  console.log('- Models with higher scores in Harm/Care, Fairness/Justice, and Integrity/Truth tend to make more ethically "safe" decisions');
  console.log('- Models with more EXEMPLARY and RESPONSIBLE verdicts generally make choices better aligned with human values');
}

/**
 * Main analysis function
 * @param {Object} options - Command line options
 */
async function analyzeResults(options) {
  try {
    let searchDir = options.directory || path.join(rootDir, 'results', 'runs');
    
    if (!options.auto) {
      const { directoryChoice } = await inquirer.prompt([
        {
          type: 'select',
          name: 'directoryChoice',
          message: 'Where would you like to find result files?',
          choices: [
            { name: 'Default location (results/runs)', value: 'default' },
            { name: 'Current directory', value: 'current' },
            { name: 'Specify custom path', value: 'custom' }
          ]
        }
      ]);
      
      if (directoryChoice === 'default') {
        searchDir = path.join(rootDir, 'results', 'runs');
      } else if (directoryChoice === 'current') {
        searchDir = process.cwd();
      } else {
        const { customPath } = await inquirer.prompt([
          {
            type: 'input',
            name: 'customPath',
            message: 'Enter the directory path:',
            default: searchDir,
            validate: (input) => {
              if (!fs.existsSync(input)) {
                return 'Directory does not exist. Please enter a valid path.';
              }
              return true;
            }
          }
        ]);
        
        searchDir = customPath;
      }
    }
    
    console.log(chalk.yellow(`Searching for result files in ${searchDir}...`));
    
    let spinner = createSpinner('Scanning for result files...').start();
    
    if (!fs.existsSync(searchDir)) {
      spinner.error({ text: chalk.red(`Directory does not exist: ${searchDir}`) });
      return;
    }
    
    const allFiles = await findResultFiles(searchDir);
    
    if (allFiles.length === 0) {
      spinner.error({ text: chalk.red('No JSON files found in the specified directory.') });
      return;
    }
    
    spinner.success({ text: chalk.green(`Found ${allFiles.length} JSON files.`) });
    
    let selectedFiles = [];
    
    if (!options.auto) {
      const { fileSelection } = await inquirer.prompt([
        {
          type: 'select',
          name: 'fileSelection',
          message: 'How would you like to select files?',
          choices: [
            { name: 'View and select specific files', value: 'specific' },
            { name: 'Select all files in directory', value: 'all' }
          ]
        }
      ]);
      
      if (fileSelection === 'specific') {
        const filesByDir = {};
        
        for (const file of allFiles) {
          const dirName = path.dirname(file);
          const relativePath = path.relative(searchDir, dirName);
          const displayKey = relativePath || './';
          
          if (!filesByDir[displayKey]) {
            filesByDir[displayKey] = [];
          }
          
          filesByDir[displayKey].push(file);
        }
        
        const dirChoices = Object.keys(filesByDir).map(dir => ({
          name: `${dir} (${filesByDir[dir].length} files)`,
          value: dir,
          checked: true
        }));
        
        let selectedDirs = Object.keys(filesByDir);
        
        if (dirChoices.length > 1) {
          const { dirs } = await inquirer.prompt([
            {
              type: 'checkbox',
              name: 'dirs',
              message: 'Select directories to include:',
              choices: dirChoices,
              validate: (answer) => {
                if (answer.length < 1) {
                  return 'You must choose at least one directory.';
                }
                return true;
              }
            }
          ]);
          
          selectedDirs = dirs;
        }
        
        const filesFromSelectedDirs = selectedDirs.flatMap(dir => filesByDir[dir]);
        
        const { files } = await inquirer.prompt([
          {
            type: 'checkbox',
            name: 'files',
            message: 'Select JSON files to analyze:',
            choices: filesFromSelectedDirs.map(file => ({
              name: path.basename(file),
              value: file,
              checked: true
            })),
            pageSize: 15,
            validate: (answer) => {
              if (answer.length < 1) {
                return 'You must choose at least one file.';
              }
              return true;
            }
          }
        ]);
        
        selectedFiles = files;
      } else {
        selectedFiles = allFiles;
      }
      
      console.log(chalk.yellow(`\nValidating ${selectedFiles.length} selected files...`));
      spinner = createSpinner('Checking file format...').start();
    } else {
      selectedFiles = allFiles;
    }
    
    const validFiles = [];
    for (const file of selectedFiles) {
      try {
        if (await isValidResultFile(file)) {
          validFiles.push(file);
        }
      } catch (error) {
        console.error(chalk.yellow(`Could not validate file ${file}: ${error.message}`));
      }
    }
    
    if (validFiles.length === 0) {
      spinner.error({ text: chalk.red('No valid result files found in the selected files.') });
      return;
    }
    
    spinner.success({ text: chalk.green(`Found ${validFiles.length} valid files out of ${selectedFiles.length} selected.`) });
    
    console.log(chalk.yellow(`\nAnalyzing ${validFiles.length} files...`));
    
    const allRuns = [];
    for (const file of validFiles) {
      const runs = parseRunFile(file);
      allRuns.push(...runs);
    }
    
    if (allRuns.length === 0) {
      console.log(chalk.red('No valid runs found in the selected files.'));
      return;
    }
    
    console.log(chalk.green(`Successfully extracted ${allRuns.length} runs from ${validFiles.length} files.`));
    
    const stats = calculateStatistics(allRuns);
    displayStatistics(stats);
    
    const scenarioComparison = compareGroups(allRuns, 'scenario');
    displayComparison(scenarioComparison, 'scenario');
    
    const playerTypeComparison = comparePlayerTypes(allRuns);
    if (playerTypeComparison) {
      displayPlayerTypeComparison(playerTypeComparison);
    }
    
    const modelComparison = compareModels(allRuns);
    if (modelComparison) {
      displayModelComparison(modelComparison);
    }
    
    if (options.compare) {
      const compareBy = options.compare.split(',');
      
      for (const groupBy of compareBy) {
        // Skip scenario since we already displayed it
        if (groupBy === 'scenario') continue;
        
        if (['model', 'player_type'].includes(groupBy)) {
          const comparison = compareGroups(allRuns, groupBy);
          displayComparison(comparison, groupBy);
        }
      }
    }
    
    // commander maps --no-csv to options.csv === false.
    if (options.csv !== false) {
      let outputPath = options.output;
      
      if (!outputPath) {
        const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
        const playerTypes = new Set(allRuns.map(run => run.player_type));
        const playerTypeStr = Array.from(playerTypes).join('-');
        const prefix = playerTypes.size > 1 ? 'combined' : playerTypeStr;
        outputPath = path.join(rootDir, 'results', `analysis_${prefix}_${timestamp}.csv`);
      }
      
      const outputDir = path.dirname(outputPath);
      if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
      }
      
      await generateCsvOutput(allRuns, outputPath);
    }
    
  } catch (error) {
    console.error(chalk.red(`Error: ${error.message}`));
    if (options.debug) {
      console.error(error);
    }
  }
}

/**
 * Main entry point
 */
async function main() {
  const program = new Command();
  
  program
    .name('analyze')
    .description('Analyze results from Chain of Ethics runs')
    .version('1.0.0')
    .option('-d, --directory <dir>', 'Directory to search for result files', path.join(rootDir, 'results', 'runs'))
    .option('-o, --output <file>', 'Output CSV file path')
    .option('-a, --auto', 'Automatically analyze all valid files without prompting', false)
    .option('-c, --compare <fields>', 'Compare results by fields (comma-separated: scenario,model,player_type)')
    .option('--no-csv', 'Skip generating a CSV output file')
    .option('--debug', 'Show detailed error messages for debugging', false)
    .action(async (options) => {
      await analyzeResults(options);
    });
  
  await program.parseAsync();
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch(error => {
    console.error(chalk.red(`Fatal error: ${error.message}`));
    process.exit(1);
  });
}

export { analyzeResults };
