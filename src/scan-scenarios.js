#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import inquirer from 'inquirer';
import chalk from 'chalk';
import glob from 'glob';
import ora from 'ora';
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

// Function to validate if inklecate is installed
function checkInklecate() {
  try {
    // Just try to run inklecate without arguments - it will error but in a predictable way if installed
    const result = execSync('inklecate', { encoding: 'utf8', stderr: 'pipe' });
    return true; // If no error is thrown, inklecate is installed
  } catch (error) {
    // Check if the error output contains usage information - this means inklecate exists but errors without arguments
    if (error.stderr && (error.stderr.includes('Usage: inklecate') || error.stderr.includes('ink file'))) {
      return true; // inklecate is installed, it just exited with an error code as expected
    }
    
    if (error.stdout && (error.stdout.includes('Usage: inklecate') || error.stdout.includes('ink file'))) {
      return true; // On some systems, usage info might go to stdout instead
    }
    
    // If we got here, inklecate is not installed
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

// Function to parse all choices and their ethical impacts
function analyzeChoices(content) {
  const lines = content.split('\n');
  let choiceBlocks = [];
  let currentChoice = null;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Detect start of a choice
    if (line.startsWith('*') && !line.startsWith('**')) {
      if (currentChoice) {
        choiceBlocks.push(currentChoice);
      }
      currentChoice = { 
        line: i + 1, 
        text: line,
        impacts: [],
        affectedAxes: new Set()
      };
    }
    
    // If we're in a choice block, look for ethical impacts
    if (currentChoice && line.startsWith('~')) {
      // Extract the axis and value from lines like: ~ hc = hc + 2
      const match = line.match(/~\s*(\w+)\s*=\s*\w+\s*([+-])\s*(\d+)/);
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
  }
  
  // Add the last choice if there is one
  if (currentChoice) {
    choiceBlocks.push(currentChoice);
  }
  
  return choiceBlocks;
}

// Function to check if choices have appropriate number of ethical impacts
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
    } else if (numAxes > MAX_AXES_PER_CHOICE) {
      issues.push({
        line: choice.line,
        message: `Choice affects ${numAxes} ethical axes, recommended maximum is ${MAX_AXES_PER_CHOICE}`,
        text: choice.text,
        severity: 'warning'
      });
    }
  }
  
  return issues;
}

// Function to check for extreme scores (+3/-3)
function checkExtremeScores(choices) {
  let totalImpacts = 0;
  let extremeImpacts = 0;
  const extremeChoices = [];
  
  for (const choice of choices) {
    let hasExtreme = false;
    
    for (const impact of choice.impacts) {
      totalImpacts++;
      if (Math.abs(impact.value) === 3) {
        extremeImpacts++;
        hasExtreme = true;
      }
    }
    
    if (hasExtreme) {
      extremeChoices.push(choice);
    }
  }
  
  const extremeRatio = totalImpacts > 0 ? extremeImpacts / totalImpacts : 0;
  
  if (extremeRatio > EXTREME_SCORE_THRESHOLD) {
    return {
      isBalanced: false,
      ratio: extremeRatio,
      choices: extremeChoices,
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
  
  // Check for missing comments on ethical impact lines
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (line.startsWith('~') && /~\s*\w+\s*=\s*\w+\s*[+-]\s*\d+/.test(line)) {
      // Check if there's a comment
      if (!line.includes('//')) {
        issues.push({
          line: i + 1,
          message: 'Ethical impact is missing a comment explaining the rationale',
          text: line,
          severity: 'warning'
        });
      }
    }
  }
  
  // Check if the scenario has a debrief section
  if (!content.includes('=== debrief ===') && !content.includes('===debrief===')) {
    issues.push({
      line: null,
      message: 'Scenario is missing a debrief section',
      severity: 'error'
    });
  }
  
  // Check if the scenario calculates total score
  if (!content.includes('~ total = ')) {
    issues.push({
      line: null,
      message: 'Scenario does not calculate total ethical score',
      severity: 'error'
    });
  }
  
  // Check if the scenario has verdict bands
  if (!content.match(/VERDICT|verdict/i) || !content.match(/EXEMPLARY|RESPONSIBLE|AMBIGUOUS|QUESTIONABLE|HARMFUL/i)) {
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
  
  const spinner = ora('Reading file...').start();
  
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    spinner.succeed('File read successfully');
    
    // Check if all ethical axes are declared
    spinner.text = 'Checking ethical axes declarations...';
    spinner.start();
    const missingAxes = checkEthicalAxes(content);
    
    if (missingAxes.length > 0) {
      spinner.fail('Missing ethical axes declarations');
      console.log(chalk.red('  Missing axes:'));
      for (const axis of missingAxes) {
        console.log(chalk.red(`  - ${axis.name} (${axis.full})`));
      }
    } else {
      spinner.succeed('All ethical axes are properly declared');
    }
    
    // Analyze choices
    spinner.text = 'Analyzing choices and ethical impacts...';
    spinner.start();
    const choices = analyzeChoices(content);
    
    // Initialize variables that will be used in the summary regardless of choice count
    let impactIssues = [];
    let scoreBalance = { isBalanced: true, ratio: 0 };
    
    if (choices.length === 0) {
      spinner.fail('No choices found in the scenario');
    } else {
      spinner.succeed(`Found ${choices.length} choices in the scenario`);
      
      // Validate number of impacts per choice
      impactIssues = validateChoiceImpacts(choices);
      
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
      scoreBalance = checkExtremeScores(choices);
      
      if (!scoreBalance.isBalanced) {
        console.log(chalk.yellow(`  ${scoreBalance.message}`));
        console.log(chalk.yellow(`  Choices with extreme scores:`));
        for (const choice of scoreBalance.choices) {
          console.log(chalk.yellow(`  - Line ${choice.line}: "${choice.text}"`));
        }
      } else {
        console.log(chalk.green(`  Ethical scoring is balanced (${(scoreBalance.ratio * 100).toFixed(1)}% extreme scores)`));
      }
    }
    
    // Perform general linting
    spinner.text = 'Performing general linting...';
    spinner.start();
    const lintIssues = lintScenario(content);
    
    if (lintIssues.length > 0) {
      spinner.fail('Linting issues found');
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
      spinner.succeed('No linting issues found');
    }
    
    // Validate compilation
    spinner.text = 'Validating scenario compilation with inklecate...';
    spinner.start();
    const validation = validateScenarioCompilation(filePath);
    
    if (validation.success) {
      spinner.succeed('Scenario compiles successfully with inklecate');
    } else {
      spinner.fail('Scenario failed to compile with inklecate');
      console.log(chalk.red('  Compilation errors:'));
      console.log(chalk.red(`  ${validation.output}`));
    }
    
    // Summary
    const hasErrors = missingAxes.length > 0 || 
                     impactIssues.some(i => i.severity === 'error') || 
                     !scoreBalance.isBalanced || 
                     lintIssues.some(i => i.severity === 'error') || 
                     !validation.success;
                     
    const hasWarnings = impactIssues.some(i => i.severity === 'warning') ||
                       lintIssues.some(i => i.severity === 'warning');
    
    console.log('\n' + chalk.cyan('Summary:'));
    if (hasErrors) {
      console.log(chalk.red('❌ This scenario has issues that need to be addressed'));
    } else if (hasWarnings) {
      console.log(chalk.yellow('⚠️ This scenario has warnings but may still function correctly'));
    } else {
      console.log(chalk.green('✅ This scenario passes all checks'));
    }
    
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
    spinner.fail(`Error analyzing scenario: ${error.message}`);
    return {
      filename: path.basename(filePath),
      path: filePath,
      hasErrors: true,
      hasWarnings: false,
      error: error.message
    };
  }
}

// Function to run the debug utility
async function run() {
  console.log(chalk.blue('=== A Game of Ethics - Scenario Debug Utility ==='));
  
  // Check if inklecate is installed
  if (!checkInklecate()) {
    return;
  }
  
  // Check for auto-validate mode from command line arguments
  const args = process.argv.slice(2);
  const autoValidateIndex = args.indexOf('--auto-validate');
  
  if (autoValidateIndex !== -1) {
    // Auto-validate mode: get files from command line arguments
    const filesToAnalyze = args.slice(autoValidateIndex + 1).filter(arg => arg.endsWith('.ink'));
    
    if (filesToAnalyze.length === 0) {
      console.error(chalk.red('Error: No .ink files specified for auto-validation.'));
      process.exit(1);
      return;
    }
    
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
    
    return;
  }
  
  // Interactive mode (original functionality)
  // Prompt for directory path
  const { targetPath } = await inquirer.prompt([
    {
      type: 'input',
      name: 'targetPath',
      message: 'Enter directory or scenario path to analyze (or press Enter for default):',
      default: path.resolve(process.cwd(), 'scenarios', 'core')
    }
  ]);
  
  // Determine if this is a directory or file
  let stats;
  try {
    stats = fs.statSync(targetPath);
  } catch (error) {
    console.error(chalk.red(`Error: The path "${targetPath}" does not exist.`));
    return;
  }
  
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
  
  // Ask which files to analyze if multiple files were found
  let selectedFiles = filesToAnalyze;
  
  if (filesToAnalyze.length > 1) {
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
    
    if (action === 'select') {
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
      
      selectedFiles = files;
    }
  }
  
  // Array to store analysis results
  const results = [];
  
  // Analyze each selected file
  for (const file of selectedFiles) {
    const result = await debugScenario(file);
    results.push(result);
  }
  
  // Output summary table if multiple files were analyzed
  if (results.length > 1) {
    console.log('\n' + chalk.blue('=== Summary of All Scenarios ==='));
    
    // Define column widths and max table width
    const maxFilenameLength = 25;
    const statusWidth = 15;  // Increased to accommodate emoji + space
    const numericWidth = 8;
    const dividerChar = '─';
    
    // Create header row
    console.log(
      chalk.cyan('\n' + 'Scenario'.padEnd(maxFilenameLength)) +
      chalk.cyan('Status'.padEnd(statusWidth)) +
      chalk.cyan('Errors'.padEnd(numericWidth)) +
      chalk.cyan('Warnings'.padEnd(numericWidth))
    );
    
    // Calculate total width and print divider
    const totalWidth = maxFilenameLength + statusWidth + numericWidth * 2;
    console.log(dividerChar.repeat(totalWidth));
    
    // Create rows for each result
    for (const result of results) {
      // Add space after emoji for better alignment
      const status = result.hasErrors 
        ? chalk.red('❌ Error') 
        : result.hasWarnings 
          ? chalk.yellow('⚠️ Warning')
          : chalk.green('✅ Pass');
      
      // Calculate error count by summing all error-level issues
      const errorCount = result.error ? 1 : (
        (result.issues?.missingAxes || 0) + 
        (result.issues?.impactIssues || 0) + 
        (result.issues?.scoreBalance || 0) + 
        (result.issues?.lintErrors || 0) + 
        (result.issues?.compilation || 0)
      );
      
      // Calculate warning count from all warning-level issues
      const warningCount = result.issues 
        ? ((result.issues.impactWarnings || 0) + (result.issues.lintWarnings || 0))
        : 0;
      
      // Truncate filename if too long
      let displayName = result.filename;
      if (displayName.length > maxFilenameLength - 3) {
        displayName = displayName.substring(0, maxFilenameLength - 3) + '...';
      }
      
      // Format counts with proper right-alignment
      const errorCountStr = String(errorCount).padStart(numericWidth - 2).padEnd(numericWidth);
      const warningCountStr = String(warningCount).padStart(numericWidth - 2).padEnd(numericWidth);
      
      console.log(
        displayName.padEnd(maxFilenameLength) +
        status.padEnd(statusWidth) +
        errorCountStr +
        warningCountStr
      );
    }
    
    console.log(dividerChar.repeat(totalWidth));
    
    // Show summary stats without the total warnings count
    const passCount = results.filter(r => !r.hasErrors && !r.hasWarnings).length;
    const errorCount = results.filter(r => r.hasErrors).length;
    const warningOnlyCount = results.filter(r => !r.hasErrors && r.hasWarnings).length;
    
    console.log(
      chalk.bold('Total: ' + results.length) + '  ' +
      chalk.green('✅ Pass: ' + passCount) + '  ' +
      chalk.yellow('⚠️ Warning: ' + warningOnlyCount) + '  ' +
      chalk.red('❌ Error: ' + errorCount)
    );
  }
}

// Helper function to output summary table
function outputSummaryTable(results) {
  console.log('\n' + chalk.blue('=== Summary of All Scenarios ==='));
  
  // Define column widths and max table width
  const maxFilenameLength = 25;
  const statusWidth = 15;  // Increased to accommodate emoji + space
  const numericWidth = 8;
  const dividerChar = '─';
  
  // Create header row
  console.log(
    chalk.cyan('\n' + 'Scenario'.padEnd(maxFilenameLength)) +
    chalk.cyan('Status'.padEnd(statusWidth)) +
    chalk.cyan('Errors'.padEnd(numericWidth)) +
    chalk.cyan('Warnings'.padEnd(numericWidth))
  );
  
  // Calculate total width and print divider
  const totalWidth = maxFilenameLength + statusWidth + numericWidth * 2;
  console.log(dividerChar.repeat(totalWidth));
  
  // Create rows for each result
  for (const result of results) {
    // Add space after emoji for better alignment
    const status = result.hasErrors 
      ? chalk.red('❌ Error') 
      : result.hasWarnings 
        ? chalk.yellow('⚠️ Warning')
        : chalk.green('✅ Pass');
    
    // Calculate error count by summing all error-level issues
    const errorCount = result.error ? 1 : (
      (result.issues?.missingAxes || 0) + 
      (result.issues?.impactIssues || 0) + 
      (result.issues?.scoreBalance || 0) + 
      (result.issues?.lintErrors || 0) + 
      (result.issues?.compilation || 0)
    );
    
    // Calculate warning count from all warning-level issues
    const warningCount = result.issues 
      ? ((result.issues.impactWarnings || 0) + (result.issues.lintWarnings || 0))
      : 0;
    
    // Truncate filename if too long
    let displayName = result.filename;
    if (displayName.length > maxFilenameLength - 3) {
      displayName = displayName.substring(0, maxFilenameLength - 3) + '...';
    }
    
    // Format counts with proper right-alignment
    const errorCountStr = String(errorCount).padStart(numericWidth - 2).padEnd(numericWidth);
    const warningCountStr = String(warningCount).padStart(numericWidth - 2).padEnd(numericWidth);
    
    console.log(
      displayName.padEnd(maxFilenameLength) +
      status.padEnd(statusWidth) +
      errorCountStr +
      warningCountStr
    );
  }
  
  console.log(dividerChar.repeat(totalWidth));
  
  // Show summary stats without the total warnings count
  const passCount = results.filter(r => !r.hasErrors && !r.hasWarnings).length;
  const errorCount = results.filter(r => r.hasErrors).length;
  const warningOnlyCount = results.filter(r => !r.hasErrors && r.hasWarnings).length;
  
  console.log(
    chalk.bold('Total: ' + results.length) + '  ' +
    chalk.green('✅ Pass: ' + passCount) + '  ' +
    chalk.yellow('⚠️ Warning: ' + warningOnlyCount) + '  ' +
    chalk.red('❌ Error: ' + errorCount)
  );
}

// Run the program
run().catch(error => {
  console.error(chalk.red(`An unexpected error occurred: ${error.message}`));
  process.exit(1);
});
