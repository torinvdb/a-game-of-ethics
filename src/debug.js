#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import inquirer from 'inquirer';
import chalk from 'chalk';
import { glob } from 'glob';
import { createSpinner } from 'nanospinner';
import { fileURLToPath } from 'url';

// Get current file directory (equivalent to __dirname in CommonJS)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Constants for validation
const REQUIRED_ETHICAL_AXES = [
  { name: 'hc', full: 'Harm / Care' },
  { name: 'fj', full: 'Fairness / Justice' },
  { name: 'ar', full: 'Autonomy / Respect' },
  { name: 'al', full: 'Authority / Legitimacy' },
  { name: 'lt', full: 'Loyalty / Trust' },
  { name: 'it', full: 'Integrity / Truth' },
  { name: 'sp', full: 'Sanctity / Purity' },
  { name: 'uc', full: 'Utility / Consequences' },
  { name: 'total', full: 'Total Score' },
  { name: 'average', full: 'Average Score' },
  { name: 'returnPath', full: 'Return Path' }
];

const MIN_AXES_PER_CHOICE = 3;
const MAX_AXES_PER_CHOICE = 5;
const EXTREME_SCORE_THRESHOLD = 0.2; // Maximum percentage of +3/-3 scores

// Validate if inklecate is installed
function checkInklecate() {
  try {
    execSync('inklecate', { encoding: 'utf8', stderr: 'pipe' });
    return true;
  } catch (error) {
    // Check error output for usage information, which indicates inklecate exists
    if ((error.stderr && (error.stderr.includes('Usage: inklecate') || error.stderr.includes('ink file'))) ||
        (error.stdout && (error.stdout.includes('Usage: inklecate') || error.stdout.includes('ink file')))) {
      return true;
    }
    
    // Display installation instructions if inklecate is not found
    console.error(chalk.red('Error: inklecate is not installed or not in PATH.'));
    console.log(chalk.yellow('Please install inklecate from: https://github.com/inkle/ink/releases'));
    console.log(chalk.yellow('For macOS, you can also use:'));
    console.log(chalk.cyan('  npm install -g inklecate'));
    console.log(chalk.yellow('or:'));
    console.log(chalk.cyan('  brew install inklecate'));
    
    return false;
  }
}

// Function to find all ink files in a directory
function findInkFiles(directory) {
  return glob.sync(`${directory}/**/*.ink`);
}

// Find and clean up compiled ink.json files
function cleanupCompiledFiles(directory) {
  const compiledFiles = glob.sync(`${directory}/**/*.ink.json`);
  
  if (compiledFiles.length === 0) {
    return { success: true, count: 0 };
  }
  
  const results = compiledFiles.reduce((acc, file) => {
    try {
      fs.unlinkSync(file);
      acc.count++;
    } catch (error) {
      acc.errors.push({ file, error: error.message });
    }
    return acc;
  }, { count: 0, errors: [] });
  
  return { 
    success: results.errors.length === 0, 
    count: results.count, 
    errors: results.errors 
  };
}

// Function to check if a file has all required ethical axes variables
function checkEthicalAxes(content) {
  const missingAxes = [];
  
  for (const axis of REQUIRED_ETHICAL_AXES) {
    // Check for either VAR name = 0 or VAR name = "" style declarations
    const pattern = new RegExp(`VAR\\s+${axis.name}\\s*=\\s*(0|"")`, 'i');
    if (!pattern.test(content)) {
      missingAxes.push(axis);
    }
  }
  
  return missingAxes;
}

function analyzeChoices(content) {
  const lines = content.split('\n');
  const choiceBlocks = [];
  let currentChoice = null;
  const impactRegex = /~\s*(\w+)\s*=\s*\w+\s*([+-])\s*(\d+)/;
  
  lines.forEach((line, i) => {
    const trimmedLine = line.trim();
    
    // Detect start of a choice
    if (trimmedLine.startsWith('*') && !trimmedLine.startsWith('**')) {
      if (currentChoice) {
        choiceBlocks.push(currentChoice);
      }
      currentChoice = { 
        line: i + 1, 
        text: trimmedLine,
        impacts: [],
        affectedAxes: new Set()
      };
    }
    
    // If we're in a choice block, look for ethical impacts
    if (currentChoice && trimmedLine.startsWith('~')) {
      const match = trimmedLine.match(impactRegex);
      if (match) {
        const [_, axis, operation, value] = match;
        const numericValue = parseInt(value);
        const finalValue = operation === '+' ? numericValue : -numericValue;
        
        currentChoice.impacts.push({
          axis,
          value: finalValue,
          line: i + 1
        });
        
        currentChoice.affectedAxes.add(axis);
      }
    }
  });
  
  // Add the last choice if there is one
  if (currentChoice) {
    choiceBlocks.push(currentChoice);
  }
  
  return choiceBlocks;
}

function validateChoiceImpacts(choices) {
  const issues = [];
  
  for (const choice of choices) {
    const numAxes = choice.affectedAxes.size;
    
    if (numAxes < MIN_AXES_PER_CHOICE) {
      issues.push({
        line: choice.line,
        message: `Choice affects only ${numAxes} ethical axes, minimum required is ${MIN_AXES_PER_CHOICE}`,
        text: choice.text,
        severity: 'error'
      });
    }
  }
  
  return issues;
}

function checkExtremeScores(choices) {
  const counts = choices.reduce((acc, choice) => {
    let hasExtreme = false;
    
    for (const impact of choice.impacts) {
      acc.totalImpacts++;
      if (Math.abs(impact.value) === 3) {
        acc.extremeImpacts++;
        hasExtreme = true;
      }
    }
    
    if (hasExtreme) {
      acc.extremeChoices.push(choice);
    }
    
    return acc;
  }, { totalImpacts: 0, extremeImpacts: 0, extremeChoices: [] });
  
  const extremeRatio = counts.totalImpacts > 0 ? counts.extremeImpacts / counts.totalImpacts : 0;
  
  if (extremeRatio > EXTREME_SCORE_THRESHOLD) {
    return {
      isBalanced: false,
      ratio: extremeRatio,
      choices: counts.extremeChoices,
      message: `Too many extreme scores (${(extremeRatio * 100).toFixed(1)}% are +3/-3, threshold is ${EXTREME_SCORE_THRESHOLD * 100}%)`
    };
  }
  
  return { isBalanced: true, ratio: extremeRatio };
}

// Function to validate if a scenario compiles with inklecate
function validateScenarioCompilation(filePath) {
  try {
    const result = execSync(`inklecate -c "${filePath}"`, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return { success: true, output: result };
  } catch (error) {
    return { 
      success: false, 
      output: error.stderr || error.stdout || error.message 
    };
  }
}

// General linting function
function lintScenario(content) {
  const issues = [];
  const lines = content.split('\n');
  const ethicalImpactRegex = /~\s*\w+\s*=\s*\w+\s*[+-]\s*\d+/;
  
  // Check for various issues in a single pass through the content
  const checks = {
    hasDebrief: content.includes('=== debrief ===') || content.includes('===debrief==='),
    hasTotalScore: content.includes('~ total = '),
    hasVerdict: !!content.match(/VERDICT|verdict/i) && 
                !!content.match(/EXEMPLARY|RESPONSIBLE|AMBIGUOUS|QUESTIONABLE|HARMFUL/i)
  };
  
  // Process line by line for per-line checks
  lines.forEach((line, i) => {
    const trimmedLine = line.trim();
    
    // Check for ethical impact lines without comments
    if (trimmedLine.startsWith('~') && ethicalImpactRegex.test(trimmedLine) && !trimmedLine.includes('//')) {
      issues.push({
        line: i + 1,
        message: 'Ethical impact is missing a comment explaining the rationale',
        text: trimmedLine,
        severity: 'warning'
      });
    }
  });
  
  // Add structural issues
  if (!checks.hasDebrief) {
    issues.push({
      line: null,
      message: 'Scenario is missing a debrief section',
      severity: 'error'
    });
  }
  
  if (!checks.hasTotalScore) {
    issues.push({
      line: null,
      message: 'Scenario does not calculate total ethical score',
      severity: 'error'
    });
  }
  
  if (!checks.hasVerdict) {
    issues.push({
      line: null,
      message: 'Scenario might be missing verdict bands',
      severity: 'warning'
    });
  }
  
  return issues;
}

// Main function to debug a scenario
async function debugScenario(filePath) {
  console.log(chalk.cyan(`\nAnalyzing scenario: ${filePath}`));
  
  const spinner = createSpinner('Reading file...').start();
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    spinner.success({ text: 'File read successfully' });
    
    // Run all analysis steps in parallel where possible
    spinner.start({ text: 'Analyzing scenario structure and content...' });
    
    // Separate synchronous analysis steps
    const missingAxes = checkEthicalAxes(content);
    const choices = analyzeChoices(content);
    const lintIssues = lintScenario(content);
    
    // Process the results of each analysis
    const axesResult = processMissingAxesResult(missingAxes);
    
    let impactIssues = [];
    let scoreBalance = { isBalanced: true, ratio: 0 };
    
    if (choices.length === 0) {
      spinner.error({ text: 'No choices found in the scenario' });
    } else {
      spinner.success({ text: `Found ${choices.length} choices in the scenario` });
      
      // Process choice impacts
      const choiceResults = processChoiceResults(choices);
      impactIssues = choiceResults.impactIssues;
      scoreBalance = choiceResults.scoreBalance;
    }
    
    // Process linting results
    processLintResults(lintIssues);
    
    // Validate compilation (this must be done separately as it's async)
    spinner.start({ text: 'Validating scenario compilation with inklecate...' });
    const validation = validateScenarioCompilation(filePath);
    
    if (validation.success) {
      spinner.success({ text: 'Scenario compiles successfully with inklecate' });
    } else {
      spinner.error({ text: 'Scenario failed to compile with inklecate' });
      console.log(chalk.red('  Compilation errors:'));
      console.log(chalk.red(`  ${validation.output}`));
    }
    
    // Generate summary
    const hasErrors = 
      missingAxes.length > 0 || 
      impactIssues.some(i => i.severity === 'error') || 
      !scoreBalance.isBalanced || 
      lintIssues.some(i => i.severity === 'error') || 
      !validation.success;
                     
    const hasWarnings = 
      impactIssues.some(i => i.severity === 'warning') ||
      lintIssues.some(i => i.severity === 'warning');
    
    outputSummary(hasErrors, hasWarnings);
    
    // Return the results for the summary table
    return {
      filename: path.basename(filePath),
      path: filePath,
      hasErrors,
      hasWarnings,
      issues: {
        missingAxes: missingAxes.length, 
        impactIssues: impactIssues.filter(i => i.severity === 'error').length,
        impactWarnings: impactIssues.filter(i => i.severity === 'warning').length,
        scoreBalance: !scoreBalance.isBalanced ? 1 : 0,
        lintErrors: lintIssues.filter(i => i.severity === 'error').length,
        lintWarnings: lintIssues.filter(i => i.severity === 'warning').length,
        compilation: !validation.success ? 1 : 0
      }
    };
    
  } catch (error) {
    spinner.error({ text: `Error analyzing scenario: ${error.message}` });
    return {
      filename: path.basename(filePath),
      path: filePath,
      hasErrors: true,
      hasWarnings: false,
      error: error.message
    };
  }
}

// Helper functions for debugScenario
function processMissingAxesResult(missingAxes) {
  if (missingAxes.length > 0) {
    console.log(chalk.red('  Missing axes:'));
    for (const axis of missingAxes) {
      console.log(chalk.red(`  - ${axis.name} (${axis.full})`));
    }
    return false;
  }
  return true;
}

function processChoiceResults(choices) {
  // Validate number of impacts per choice
  const impactIssues = validateChoiceImpacts(choices);
  
  if (impactIssues.length > 0) {
    console.log(chalk.yellow('  Choice impact issues:'));
    for (const issue of impactIssues) {
      const color = issue.severity === 'error' ? chalk.red : chalk.yellow;
      console.log(color(`  - Line ${issue.line}: ${issue.message}`));
      console.log(color(`    "${issue.text}"`));
    }
  } else {
    console.log(chalk.green('  All choices have the appropriate number of ethical impacts'));
  }
  
  // Check for balanced scoring
  const scoreBalance = checkExtremeScores(choices);
  
  if (!scoreBalance.isBalanced) {
    console.log(chalk.yellow(`  ${scoreBalance.message}`));
    console.log(chalk.yellow(`  Choices with extreme scores:`));
    for (const choice of scoreBalance.choices) {
      console.log(chalk.yellow(`  - Line ${choice.line}: "${choice.text}"`));
    }
  } else {
    console.log(chalk.green(`  Ethical scoring is balanced (${(scoreBalance.ratio * 100).toFixed(1)}% extreme scores)`));
  }
  
  return { impactIssues, scoreBalance };
}

function processLintResults(lintIssues) {
  if (lintIssues.length > 0) {
    console.log(chalk.yellow('  Linting issues:'));
    for (const issue of lintIssues) {
      const color = issue.severity === 'error' ? chalk.red : chalk.yellow;
      const lineInfo = issue.line ? `Line ${issue.line}: ` : '';
      console.log(color(`  - ${lineInfo}${issue.message}`));
      if (issue.text) {
        console.log(color(`    "${issue.text}"`));
      }
    }
  } else {
    console.log(chalk.green('  No linting issues found'));
  }
}

function outputSummary(hasErrors, hasWarnings) {
  console.log('\n' + chalk.cyan('Summary:'));
  if (hasErrors) {
    console.log(chalk.red('❌ This scenario has issues that need to be addressed'));
  } else if (hasWarnings) {
    console.log(chalk.yellow('⚠️ This scenario has warnings but may still function correctly'));
  } else {
    console.log(chalk.green('✅ This scenario passes all checks'));
  }
}

// Function to display help text
function showHelp() {
  console.log(chalk.blue('=== A Game of Ethics - Scenario Debug Utility ==='));
  console.log('\nUsage:');
  console.log('  node src/debug.js [options] [files]');
  
  console.log('\nOptions:');
  console.log('  -h, --help              Show this help information');
  console.log('  --cleanup [directory]   Clean up compiled .ink.json files in the specified directory');
  console.log('                          (defaults to ./scenarios if not specified)');
  console.log('  --auto-validate <files> Automatically validate one or more .ink files');
  
  console.log('\nExamples:');
  console.log('  node src/debug.js                            # Run in interactive mode');
  console.log('  node src/debug.js --help                     # Show this help');
  console.log('  node src/debug.js --cleanup                  # Clean up compiled files in default directory');
  console.log('  node src/debug.js --cleanup ./my-scenarios   # Clean up compiled files in custom directory');
  console.log('  node src/debug.js --auto-validate scenarios/core/*.ink  # Validate multiple scenarios');
}

// Validate command-line arguments
function validateArgs(args) {
  // Skip validation if no arguments provided (will run in interactive mode)
  if (args.length === 0) {
    return true;
  }
  
  const validArgs = ['--help', '-h', '--cleanup', '--auto-validate'];
  
  // Check for help flag first
  if (args.includes('-h') || args.includes('--help')) {
    return true;
  }
  
  // Check for auto-validate mode
  if (args.includes('--auto-validate')) {
    const inkFiles = args.filter(arg => arg.endsWith('.ink'));
    if (inkFiles.length === 0) {
      console.error(chalk.red('Error: --auto-validate requires at least one .ink file path'));
      return false;
    }
    return true;
  }
  
  // Check for cleanup mode
  if (args.includes('--cleanup')) {
    return true;
  }
  
  // If we get here, there are unknown arguments
  const unknownArgs = args.filter(arg => !validArgs.includes(arg) && !arg.endsWith('.ink'));
  if (unknownArgs.length > 0) {
    console.error(chalk.red(`Error: Unknown argument(s): ${unknownArgs.join(', ')}`));
    return false;
  }
  
  return true;
}

// Function to run the debug utility
async function run() {
  // Check for command line arguments
  const args = process.argv.slice(2);
  
  // Check for help flag
  if (args.includes('-h') || args.includes('--help')) {
    showHelp();
    return;
  }
  
  // Validate arguments
  if (!validateArgs(args)) {
    console.log('\nFor help, use: node src/debug.js --help');
    process.exit(1);
  }
  
  console.log(chalk.blue('=== A Game of Ethics - Scenario Debug Utility ==='));
  
  // Check if inklecate is installed
  if (!checkInklecate()) {
    return;
  }
  
  // Handle cleanup mode
  if (args.includes('--cleanup')) {
    await handleCleanupMode(args);
    return;
  }
  
  // Handle auto-validate mode
  if (args.includes('--auto-validate')) {
    await handleAutoValidateMode(args);
    return;
  }
  
  // Handle interactive mode
  await handleInteractiveMode();
}

// Handle cleanup mode
async function handleCleanupMode(args) {
  const cleanupIndex = args.indexOf('--cleanup');
  
  // Get directory from argument after --cleanup or use default
  let cleanupDir = args[cleanupIndex + 1];
  
  // If no directory specified or it's another flag, use current directory
  if (!cleanupDir || cleanupDir.startsWith('--')) {
    cleanupDir = path.resolve(process.cwd(), 'scenarios');
  }
  
  console.log(chalk.cyan(`Cleaning up compiled .ink.json files in: ${cleanupDir}`));
  
  const spinner = createSpinner('Searching for compiled files...').start();
  const result = cleanupCompiledFiles(cleanupDir);
  
  if (result.success) {
    if (result.count > 0) {
      spinner.success({ text: `Successfully deleted ${result.count} compiled .ink.json files` });
    } else {
      spinner.warn({ text: 'No compiled .ink.json files found' });
    }
  } else {
    spinner.error({ text: `Encountered errors while deleting some files` });
    console.log(chalk.red('  Errors:'));
    for (const err of result.errors) {
      console.log(chalk.red(`  - ${err.file}: ${err.error}`));
    }
    console.log(chalk.green(`  Successfully deleted: ${result.count} files`));
  }
}

// Handle auto-validate mode
async function handleAutoValidateMode(args) {
  const autoValidateIndex = args.indexOf('--auto-validate');
  const filesToAnalyze = args.slice(autoValidateIndex + 1).filter(arg => arg.endsWith('.ink'));
  
  console.log(chalk.cyan(`Auto-validating ${filesToAnalyze.length} .ink files...`));
  
  // Array to store analysis results
  const results = [];
  
  // Analyze each specified file
  for (const file of filesToAnalyze) {
    const result = await debugScenario(file);
    results.push(result);
  }
  
  // Output summary table
  if (results.length > 0) {
    outputSummaryTable(results);
    
    // Exit with an error code if there are errors
    const hasErrors = results.some(r => r.hasErrors);
    if (hasErrors) {
      process.exit(1);
    }
  }
}

// Handle interactive mode
async function handleInteractiveMode() {
  // Prompt for directory path
  const { targetPathInput } = await inquirer.prompt([
    {
      type: 'input',
      name: 'targetPathInput',
      message: 'Enter directory or scenario path to analyze (or press Enter for default):',
      default: path.resolve(process.cwd(), 'scenarios', 'core')
    }
  ]);
  
  let targetPath = targetPathInput;
  
  // Validate path existence
  let stats;
  try {
    stats = fs.statSync(targetPath);
  } catch (error) {
    console.error(chalk.red(`Error: The path "${targetPath}" does not exist.`));
    return;
  }
  
  // Get files to analyze based on whether path is directory or file
  let filesToAnalyze = [];
  
  if (stats.isDirectory()) {
    console.log(chalk.cyan(`Searching for .ink files in: ${targetPath}`));
    filesToAnalyze = findInkFiles(targetPath);
    
    if (filesToAnalyze.length === 0) {
      console.log(chalk.yellow(`No .ink files found in ${targetPath}`));
      return;
    }
    
    console.log(chalk.cyan(`Found ${filesToAnalyze.length} .ink files`));
  } else if (path.extname(targetPath) === '.ink') {
    filesToAnalyze = [targetPath];
  } else {
    console.error(chalk.red(`Error: The file "${targetPath}" is not an .ink file.`));
    return;
  }
  
  // Select files to analyze if multiple files were found
  let selectedFiles = await selectFilesToAnalyze(filesToAnalyze);
  
  // Analyze selected files
  const results = [];
  for (const file of selectedFiles) {
    const result = await debugScenario(file);
    results.push(result);
  }
  
  // Output summary table for multiple files
  if (results.length > 1) {
    outputSummaryTable(results);
  }
  
  // Ask about cleanup
  await promptForCleanup(stats.isDirectory() ? targetPath : path.dirname(targetPath));
}

// Helper function to select files for analysis
async function selectFilesToAnalyze(filesToAnalyze) {
  if (filesToAnalyze.length === 1) {
    return filesToAnalyze;
  }
  
  const { action } = await inquirer.prompt([
    {
      type: 'list',
      name: 'action',
      message: 'How would you like to proceed?',
      choices: [
        { name: 'Analyze all files', value: 'all' },
        { name: 'Select specific files', value: 'select' }
      ]
    }
  ]);
  
  if (action === 'all') {
    return filesToAnalyze;
  }
  
  const { files } = await inquirer.prompt([
    {
      type: 'checkbox',
      name: 'files',
      message: 'Select files to analyze:',
      choices: filesToAnalyze.map(file => ({
        name: path.basename(file),
        value: file
      })),
      validate: (answer) => answer.length > 0 ? true : 'You must select at least one file'
    }
  ]);
  
  return files;
}

// Helper function to prompt for cleanup
async function promptForCleanup(cleanupDir) {
  console.log('\n');
  const { shouldCleanup } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'shouldCleanup',
      message: 'Do you want to clean up compiled .ink.json files?',
      default: true
    }
  ]);
  
  if (shouldCleanup) {
    console.log(chalk.cyan(`Cleaning up compiled .ink.json files in: ${cleanupDir}`));
    
    const spinner = createSpinner('Searching for compiled files...').start();
    const result = cleanupCompiledFiles(cleanupDir);
    
    if (result.success) {
      if (result.count > 0) {
        spinner.success({ text: `Successfully deleted ${result.count} compiled .ink.json files` });
      } else {
        spinner.warn({ text: 'No compiled .ink.json files found' });
      }
    } else {
      spinner.error({ text: `Encountered errors while deleting some files` });
      console.log(chalk.red('  Errors:'));
      for (const err of result.errors) {
        console.log(chalk.red(`  - ${err.file}: ${err.error}`));
      }
      console.log(chalk.green(`  Successfully deleted: ${result.count} files`));
    }
  }
}

// Helper function to output summary table
function outputSummaryTable(results) {
  console.log('\n' + chalk.blue('=== Summary of All Scenarios ==='));
  
  // Define table parameters
  const params = {
    maxFilenameLength: 25,
    statusWidth: 15,  // Enough for emoji + space
    numericWidth: 8,
    dividerChar: '─'
  };
  
  const totalWidth = params.maxFilenameLength + params.statusWidth + params.numericWidth * 2;
  
  // Create header row
  console.log(
    chalk.cyan('\n' + 'Scenario'.padEnd(params.maxFilenameLength)) +
    chalk.cyan('Status'.padEnd(params.statusWidth)) +
    chalk.cyan('Errors'.padEnd(params.numericWidth)) +
    chalk.cyan('Warnings'.padEnd(params.numericWidth))
  );
  
  // Print divider
  console.log(params.dividerChar.repeat(totalWidth));
  
  // Process and print each result
  results.forEach(result => {
    // Determine status with appropriate color and emoji
    const status = result.hasErrors 
      ? chalk.red('❌ Error') 
      : result.hasWarnings 
        ? chalk.yellow('⚠️ Warning')
        : chalk.green('✅ Pass');
    
    // Calculate counts
    const errorCount = result.error ? 1 : (
      (result.issues?.missingAxes || 0) + 
      (result.issues?.impactIssues || 0) + 
      (result.issues?.scoreBalance || 0) + 
      (result.issues?.lintErrors || 0) + 
      (result.issues?.compilation || 0)
    );
    
    const warningCount = result.issues 
      ? ((result.issues.impactWarnings || 0) + (result.issues.lintWarnings || 0))
      : 0;
    
    // Truncate filename if too long
    let displayName = result.filename;
    if (displayName.length > params.maxFilenameLength - 3) {
      displayName = displayName.substring(0, params.maxFilenameLength - 3) + '...';
    }
    
    // Format counts with proper alignment
    const errorCountStr = String(errorCount).padStart(params.numericWidth - 2).padEnd(params.numericWidth);
    const warningCountStr = String(warningCount).padStart(params.numericWidth - 2).padEnd(params.numericWidth);
    
    console.log(
      displayName.padEnd(params.maxFilenameLength) +
      status.padEnd(params.statusWidth) +
      errorCountStr +
      warningCountStr
    );
  });
  
  console.log(params.dividerChar.repeat(totalWidth));
  
  // Generate and display summary statistics
  const stats = {
    total: results.length,
    pass: results.filter(r => !r.hasErrors && !r.hasWarnings).length,
    warning: results.filter(r => !r.hasErrors && r.hasWarnings).length,
    error: results.filter(r => r.hasErrors).length
  };
  
  console.log(
    chalk.bold(`Total: ${stats.total}`) + '  ' +
    chalk.green(`✅ Pass: ${stats.pass}`) + '  ' +
    chalk.yellow(`⚠️ Warning: ${stats.warning}`) + '  ' +
    chalk.red(`❌ Error: ${stats.error}`)
  );
}

// Run the program
run().catch(error => {
  console.error(chalk.red(`An unexpected error occurred: ${error.message}`));
  process.exit(1);
});
