#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { Command } from 'commander';
import { createObjectCsvWriter } from 'csv-writer';
import { glob } from 'glob';
import _ from 'lodash';
import { fileURLToPath } from 'url';
import Table from 'cli-table3';
import { createSpinner } from 'nanospinner';

// Get directory paths
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

// Define ethical axes names for better display
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

// Define the full list of ethical axes
const ethicalAxes = ['hc', 'fj', 'ar', 'al', 'lt', 'it', 'sp', 'uc'];

/**
 * Find all result JSON files in a directory
 * @param {string} directory - The directory to search in
 * @returns {Promise<string[]>} Paths to all JSON files
 */
async function findResultFiles(directory) {
  try {
    // Use fs.readdirSync for more reliable file discovery
    const getAllFiles = function(dirPath, arrayOfFiles = []) {
      const files = fs.readdirSync(dirPath);
      
      files.forEach(function(file) {
        const filePath = path.join(dirPath, file);
        if (fs.statSync(filePath).isDirectory()) {
          arrayOfFiles = getAllFiles(filePath, arrayOfFiles);
        } else if (path.extname(file) === '.json') {
          arrayOfFiles.push(filePath);
        }
      });
      
      return arrayOfFiles;
    };
    
    return getAllFiles(directory);
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
    
    // Check for minimum required structure
    // Single run file format
    if (data.choices && Array.isArray(data.choices) && data.scores && typeof data.scores === 'object') {
      return true;
    }
    
    // Multi-run file format
    if (data.runs && Array.isArray(data.runs) && data.runs.length > 0) {
      return true;
    }
    
    return false;
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
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const data = JSON.parse(fileContent);
    const runs = [];
    
    // Get the scenario name from the path or file data
    const scenarioName = data.scenario || path.basename(path.dirname(filePath));
    
    // Handle multi-run files
    if (data.runs && Array.isArray(data.runs)) {
      for (let i = 0; i < data.runs.length; i++) {
        const run = data.runs[i];
        runs.push({
          file_path: filePath,
          run_id: `${data.run_id || 'batch'}-${i + 1}`,
          scenario: scenarioName,
          model: data.model || 'unknown',
          player_type: data.model ? 'model' : 'manual',
          system_prompt: data.systemPrompt || '',
          timestamp: data.timestamp || new Date().toISOString(),
          scores: run.scores || {},
          verdict: run.verdict || '',
          choice_count: run.choices ? run.choices.length : 0
        });
      }
    } else {
      // Handle single run files
      runs.push({
        file_path: filePath,
        run_id: data.run_id || path.basename(filePath, '.json'),
        scenario: scenarioName,
        model: data.model || (data.player === 'human' ? 'human' : 'unknown'),
        player_type: data.player === 'human' ? 'manual' : 'model',
        system_prompt: data.systemPrompt || '',
        timestamp: data.timestamp || new Date().toISOString(),
        scores: data.scores || {},
        verdict: data.verdict || '',
        choice_count: data.choices ? data.choices.length : 0
      });
    }
    
    return runs;
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
    by_player_type: {},  // Changed order: player_type first
    by_model: {},        // Then model
    by_scenario: {},     // Then scenario
    by_verdict: {},
    score_stats: {},
    ethical_bias: {}
  };
  
  // Group by player type first
  const playerTypeGroups = _.groupBy(runs, 'player_type');
  for (const [playerType, playerTypeRuns] of Object.entries(playerTypeGroups)) {
    stats.by_player_type[playerType] = playerTypeRuns.length;
  }
  
  // Group by model, but only include actual models (not "human")
  const modelRuns = runs.filter(run => run.player_type === 'model');
  const modelGroups = _.groupBy(modelRuns, 'model');
  for (const [model, modelRuns] of Object.entries(modelGroups)) {
    stats.by_model[model] = modelRuns.length;
  }
  
  // Group by scenario
  const scenarioGroups = _.groupBy(runs, 'scenario');
  for (const [scenario, scenarioRuns] of Object.entries(scenarioGroups)) {
    stats.by_scenario[scenario] = scenarioRuns.length;
  }
  
  // Group by verdict
  const verdictGroups = _.groupBy(runs, 'verdict');
  for (const [verdict, verdictRuns] of Object.entries(verdictGroups)) {
    if (verdict) {
      // Extract the first part of the verdict (e.g., "EXEMPLARY" from "EXEMPLARY - Model of moral conscience...")
      const shortVerdict = verdict.split(' - ')[0];
      stats.by_verdict[shortVerdict] = (stats.by_verdict[shortVerdict] || 0) + verdictRuns.length;
    }
  }
  
  // Calculate score statistics for each axis
  const allAxes = [...ethicalAxes, 'total', 'average'];
  
  for (const axis of allAxes) {
    const scores = runs
      .map(run => run.scores[axis])
      .filter(score => score !== undefined && score !== null);
    
    if (scores.length > 0) {
      stats.score_stats[axis] = {
        mean: _.mean(scores),
        median: _.sortBy(scores)[Math.floor(scores.length / 2)],
        min: _.min(scores),
        max: _.max(scores),
        std_dev: Math.sqrt(_.sum(scores.map(s => Math.pow(s - _.mean(scores), 2))) / scores.length)
      };
    }
  }
  
  // Calculate ethical bias (which ethical axes tend to score highest/lowest)
  // For each run, rank the ethical axes from highest to lowest score
  const axisRanks = runs.map(run => {
    const axisScores = ethicalAxes.map(axis => ({
      axis,
      score: run.scores[axis] || 0
    }));
    
    return _.orderBy(axisScores, ['score'], ['desc']);
  });
  
  // Count how often each axis appears in each rank position
  for (let i = 0; i < ethicalAxes.length; i++) {
    stats.ethical_bias[`rank_${i + 1}`] = {};
    
    for (const axis of ethicalAxes) {
      stats.ethical_bias[`rank_${i + 1}`][axis] = axisRanks.filter(rank => 
        rank[i] && rank[i].axis === axis
      ).length;
    }
  }
  
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
      
      // Calculate average scores for each axis
      for (const axis of [...ethicalAxes, 'total', 'average']) {
        const scores = groupRuns.map(run => run.scores[axis]).filter(s => s !== undefined);
        if (scores.length > 0) {
          comparison[groupName][axis] = _.mean(scores);
        }
      }
      
      // Count verdicts
      const verdicts = {};
      for (const run of groupRuns) {
        if (run.verdict) {
          const shortVerdict = run.verdict.split(' - ')[0];
          verdicts[shortVerdict] = (verdicts[shortVerdict] || 0) + 1;
        }
      }
      comparison[groupName].verdicts = verdicts;
      
      // Count runs
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
  
  // Skip if not enough data
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
  
  // Calculate average scores for each axis
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
  
  // Count verdicts
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
  // Filter to model runs only (not manual)
  const modelRuns = runs.filter(run => run.player_type === 'model');
  
  // Group by model
  const modelGroups = _.groupBy(modelRuns, 'model');
  const models = Object.keys(modelGroups);
  
  // Skip if not enough data (need at least 2 models)
  if (models.length < 2) {
    return null;
  }
  
  // Calculate stats for each model
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
  
  // Add a column for each ethical axis
  for (const axis of ethicalAxes) {
    header.push({ id: `scores.${axis}`, title: axisNames[axis] });
  }
  
  // Add total and average
  header.push({ id: 'scores.total', title: 'Total Score' });
  header.push({ id: 'scores.average', title: 'Average Score' });
  
  const csvWriter = createObjectCsvWriter({
    path: outputPath,
    header
  });
  
  // Transform data for CSV format
  const records = runs.map(run => {
    const record = { ...run };
    
    // Flatten scores object
    for (const axis of [...ethicalAxes, 'total', 'average']) {
      record[`scores.${axis}`] = run.scores[axis];
    }
    
    return record;
  });
  
  await csvWriter.writeRecords(records);
  console.log(chalk.green(`\nCSV file successfully written to ${outputPath}`));
}

/**
 * Display statistics in console
 * @param {Object} stats - Statistics object
 */
function displayStatistics(stats) {
  console.log(chalk.cyan('\n===== ANALYSIS SUMMARY =====\n'));
  
  // Display run counts
  console.log(chalk.bold(`Total Runs: ${stats.count}`));
  
  // Display player type breakdown first
  if (Object.keys(stats.by_player_type).length > 0) {
    console.log(chalk.cyan('\nRuns by Player Type:'));
    for (const [playerType, count] of Object.entries(stats.by_player_type)) {
      console.log(`  ${playerType}: ${count} runs (${((count / stats.count) * 100).toFixed(1)}%)`);
    }
  }
  
  // Display model breakdown (excluding human)
  if (Object.keys(stats.by_model).length > 0) {
    console.log(chalk.cyan('\nRuns by Model:'));
    for (const [model, count] of Object.entries(stats.by_model)) {
      console.log(`  ${model}: ${count} runs (${((count / stats.count) * 100).toFixed(1)}%)`);
    }
  }
  
  // Display scenario breakdown
  if (Object.keys(stats.by_scenario).length > 0) {
    console.log(chalk.cyan('\nRuns by Scenario:'));
    for (const [scenario, count] of Object.entries(stats.by_scenario)) {
      console.log(`  ${scenario}: ${count} runs (${((count / stats.count) * 100).toFixed(1)}%)`);
    }
  }
  
  // Display verdict breakdown
  if (Object.keys(stats.by_verdict).length > 0) {
    console.log(chalk.cyan('\nVerdict Distribution:'));
    for (const [verdict, count] of Object.entries(stats.by_verdict)) {
      const percentage = ((count / stats.count) * 100).toFixed(1);
      const color = verdict === 'EXEMPLARY' || verdict === 'RESPONSIBLE' ? 'green' : 
                   verdict === 'AMBIGUOUS' ? 'yellow' : 'red';
      
      console.log(chalk[color](`  ${verdict}: ${count} runs (${percentage}%)`));
    }
  }
  
  // Display score statistics
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
  
  // Add total and average rows if they exist
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
  
  // Display ethical bias (which axes tend to rank highest) with better explanation
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
  
  // Create a table for the comparison
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
    // Find the most common verdict
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
    
    // Construct the row
    const row = [
      groupName,
      data.count || 0
    ];
    
    // Add each ethical axis score
    for (const axis of ethicalAxes) {
      row.push(data[axis] !== undefined ? data[axis].toFixed(2) : 'N/A');
    }
    
    // Add total and average
    row.push(data.total !== undefined ? data.total.toFixed(2) : 'N/A');
    row.push(data.average !== undefined ? data.average.toFixed(2) : 'N/A');
    
    // Add top verdict
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
  
  // Create a table for comparison
  const comparisonTable = new Table({
    head: [
      chalk.cyan('Metric'),
      chalk.cyan('Manual Players'),
      chalk.cyan('Model Players'),
      chalk.cyan('Difference')
    ],
    colWidths: [20, 15, 15, 15]
  });
  
  // Add count
  comparisonTable.push([
    'Run Count',
    comparison.manual.count,
    comparison.model.count,
    'N/A'
  ]);
  
  // Add average scores by axis
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
  
  // Add average of all axes
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
  
  // Display verdict distribution comparison
  console.log(chalk.cyan('\nVerdict Distribution Comparison:'));
  
  const verdictTable = new Table({
    head: [
      chalk.cyan('Verdict'),
      chalk.cyan('Manual (%)'),
      chalk.cyan('Model (%)')
    ],
    colWidths: [15, 15, 15]
  });
  
  // Collect all possible verdicts
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
  
  // Add interpretation text
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
  
  // Create axis score comparison table
  console.log(chalk.cyan('Ethical Axis Scores by Model:'));
  
  const models = Object.keys(comparison);
  const scoreTable = new Table({
    head: [
      chalk.cyan('Ethical Axis'),
      ...models.map(model => chalk.cyan(model.split('/').pop()))
    ],
    colWidths: [20, ...Array(models.length).fill(Math.max(15, Math.floor(80 / (models.length + 1))))]
  });
  
  // Add rows for each ethical axis
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
  
  // Add average row
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
  
  // Create verdict distribution comparison table
  console.log(chalk.cyan('\nVerdict Distribution by Model:'));
  
  // Collect all possible verdicts across all models
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
  
  // Add rows for each verdict
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
  
  // Add interpretation text
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
    // Ask for directory to search if not in auto mode
    let searchDir = options.directory || path.join(rootDir, 'results', 'runs');
    
    if (!options.auto) {
      const { directoryChoice } = await inquirer.prompt([
        {
          type: 'list',
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
        // Ask for custom directory
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
    
    // Find all JSON files in the directory
    console.log(chalk.yellow(`Searching for result files in ${searchDir}...`));
    
    let spinner = createSpinner('Scanning for result files...').start();
    
    // Make sure the directory exists
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
    
    // Let the user select any JSON files to analyze
    let selectedFiles = [];
    
    // If not in auto mode, let user select files
    if (!options.auto) {
      // Let user select any JSON files
      const { fileSelection } = await inquirer.prompt([
        {
          type: 'list',
          name: 'fileSelection',
          message: 'How would you like to select files?',
          choices: [
            { name: 'View and select specific files', value: 'specific' },
            { name: 'Select all files in directory', value: 'all' }
          ]
        }
      ]);
      
      if (fileSelection === 'specific') {
        // Organize files by directory for easier selection
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
        
        // First let user select directories
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
        
        // Flatten the files from selected directories
        const filesFromSelectedDirs = selectedDirs.flatMap(dir => filesByDir[dir]);
        
        // Let user select specific files
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
        // Use all files
        selectedFiles = allFiles;
      }
      
      console.log(chalk.yellow(`\nValidating ${selectedFiles.length} selected files...`));
      spinner = createSpinner('Checking file format...').start();
    } else {
      // In auto mode, use all files but validate them
      selectedFiles = allFiles;
    }
    
    // Validate the selected files
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
    
    // Parse all valid files
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
    
    // Continue with existing analysis code
    const stats = calculateStatistics(allRuns);
    displayStatistics(stats);
    
    // Generate manual vs model comparison if both exist
    const playerTypeComparison = comparePlayerTypes(allRuns);
    if (playerTypeComparison) {
      displayPlayerTypeComparison(playerTypeComparison);
    }
    
    // Generate model comparison if multiple models exist
    const modelComparison = compareModels(allRuns);
    if (modelComparison) {
      displayModelComparison(modelComparison);
    }
    
    // Generate comparisons if requested
    if (options.compare) {
      const compareBy = options.compare.split(',');
      
      for (const groupBy of compareBy) {
        if (['scenario', 'model', 'player_type'].includes(groupBy)) {
          const comparison = compareGroups(allRuns, groupBy);
          displayComparison(comparison, groupBy);
        }
      }
    }
    
    // Generate CSV output
    if (!options.noCsv) {
      let outputPath = options.output;
      
      if (!outputPath) {
        // Generate a default output path
        const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
        const playerTypes = new Set(allRuns.map(run => run.player_type));
        const playerTypeStr = Array.from(playerTypes).join('-');
        const prefix = playerTypes.size > 1 ? 'combined' : playerTypeStr;
        outputPath = path.join(rootDir, 'results', `analysis_${prefix}_${timestamp}.csv`);
      }
      
      // Ensure the output directory exists
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

// Run the main function if this script is executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(error => {
    console.error(chalk.red(`Fatal error: ${error.message}`));
    process.exit(1);
  });
}

export { analyzeResults };
