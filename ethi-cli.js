#!/usr/bin/env node

import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { Command } from 'commander';
import figlet from 'figlet';
import { runManualMode } from './src/manual-player.js';
import { playInkStoryWithLLM, runMultipleGames } from './src/model-player.js';

// Get directory paths
const __dirname = path.dirname(fileURLToPath(import.meta.url));

function displayWelcomeBanner() {
  console.clear();
  
    console.log(chalk.yellow(`
                                            ⠀⠀⠀⣸⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⣏⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣫⠬⠿⡦⡙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡾⣽⠃⡴⠚⠻⣞⣆⠙⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣿⣁⡇⢸⠁⡦⡄⢹⠼⡆⢰⣯⣲⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣾⣿⣿⠀⡇⢾⠀⣗⡇⢸⠂⡇⠘⢿⣽⠞⠋⠀⠀⠀⠀⠀⢀⡴⢦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠛⣟⠦⣄⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄⠀⢿⡸⣄⠙⢁⣼⣰⠃⢠⡞⠁⠀⠀⠀⢀⣄⣀⣠⠏⣠⡄⢻⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡄⢹⣧⣙⣶⣾⡿⢛⡓⢦⡀⠀⠀⠈⢧⠈⢷⣍⣳⣾⡵⠃⢀⡟⠀⠀⠀⠀⣼⠟⠛⢿⣿⣶⣿⡇⢠⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⢀⣤⠶⢦⣤⣀⣠⡶⠦⣄⠀⠀⣠⣤⣷⣌⣿⠿⠻⠋⢸⠋⠉⠻⡷⠀⠀⠀⠈⢧⠀⣸⠋⠙⡇⠀⢸⠀⠀⠀⠀⢸⣧⠤⠶⣄⠀⠈⠉⠁⢼⡿⡿⣦⡀⠀⠀⠀⠀⠀⣀⡤⠴⣄⠀
                ⡞⠁⣠⠶⢤⡟⢳⡦⣤⠘⣧⡾⢿⣿⣿⡛⠁⢰⣄⠀⢸⣤⣀⠀⠀⠀⠀⠀⠀⢸⢠⡿⠀⠀⢻⡀⠈⢧⡀⠀⠀⠈⠁⠀⢀⣾⠀⣠⣆⠀⢠⡾⠶⣌⣷⠀⢠⠖⣺⠟⠁⠀⠀⠈⢳
                ⣇⠀⣧⣤⡀⢳⠼⣇⣼⠀⡿⣧⣾⠀⠀⠹⣄⢸⣈⣷⠞⠃⣨⣟⠀⠀⠀⠀⣠⣾⣿⠃⢠⣆⠀⠳⡄⠀⠛⢦⣀⣀⣀⣠⣿⡉⠛⠯⢿⣦⣿⣄⠀⢸⡿⢀⡏⡼⠁⢠⠞⠉⣹⣦⢀
                ⠉⠛⠁⠀⣹⣾⣦⣌⢻⡄⣇⠈⠉⠀⠀⠀⣿⣉⣡⣤⣤⡞⠁⠈⠛⠒⠲⢛⣿⡿⠁⠀⢸⠉⢧⡀⠙⣦⣄⠀⠀⠉⣩⣽⡿⠛⠓⠲⣶⢤⣼⠏⠀⠀⠁⢸⢠⠁⣠⠟⠲⣎⠉⠘⠿
                ⠀⠀⠀⠀⣿⠀⠀⠙⣧⢿⡻⣄⠀⠀⠀⣀⡼⢃⡿⠁⢱⣍⡓⠲⠶⠶⠞⠛⠉⠀⢀⡴⠃⠀⠀⠳⣄⠀⠙⠛⠻⠟⠛⠋⠀⣀⡀⠀⢹⡀⢳⡀⠀⠀⢀⡟⣸⢰⠃⠀⠀⢸⠀⠀⠀
                ⠀⠀⠀⠀⠘⢇⣀⣠⡿⠈⠳⣌⣉⠛⠋⢉⣠⠞⠁⢠⠏⠀⠉⠓⠲⠤⠤⣤⠤⠖⠋⠀⠀⠀⠀⠀⠈⠳⣄⣀⠀⠀⢀⣠⠼⠋⠳⣄⠀⢳⡀⠙⠒⠒⠋⡰⠃⣼⡀⠀⣠⡟⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠙⣯⠙⠢⣄⡀⠉⠉⠉⠉⢁⣀⣴⣋⣀⣀⣠⣤⣤⣤⣤⣤⡤⠤⠤⢤⣤⣤⣤⣤⣤⣀⣀⣈⣉⣉⠉⠀⠀⠀⠀⠈⠳⣄⡉⠒⠒⠒⢊⣡⠞⠉⡽⠛⠉⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠘⣄⣀⣠⠽⠿⠒⠒⠛⠉⠉⠉⣁⣀⣀⣤⣤⣤⠤⠤⠤⠤⠤⠤⠴⠴⠤⠤⠤⠤⠤⠤⠤⠬⠭⠭⣭⣽⣿⣶⣶⣶⣶⣿⣶⣶⣾⣭⣄⣀⡚⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⣼⣋⣡⣤⣴⡶⠒⢒⣛⡛⠏⠉⠉⠀⠀⠀⠀⢠⣴⠶⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡴⢶⣤⠀⠀⠀⠀⠀⠀⠈⠉⠉⠙⢻⡖⠿⢭⣩⣽⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠉⢯⠀⢰⠃⢀⣾⠋⠉⣿⠀⠀⠀⠀⠀⠀⠀⠸⣦⣄⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣄⣀⣽⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⠀⠀⡏⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠸⡄⠀⠛⠷⡾⠋⠀⢀⣀⣀⣀⣀⣀⣀⣈⣉⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣉⣉⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⣸⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⣳⡤⠴⠒⠚⠋⢉⣉⣉⣁⣀⣠⣤⠤⠤⠤⠤⠤⠤⠤⠬⠥⠭⠭⠭⠭⠭⠭⠭⠭⠭⣭⣍⣉⣉⣉⡉⠙⠓⠒⠒⠶⣯⣀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⡿⠋⣠⠤⠖⠒⠛⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠙⠓⠒⠲⠤⢤⣙⣷⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⢾⣁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡏⠀⠀⠀⠀⠀⠀⠀⠀
                ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠓⠒⠒⠦⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣤⠤⠴⢖⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
  `));
  
  console.log(
    chalk.cyan(
      figlet.textSync('A Game of Ethics', { horizontalLayout: 'full' })
    )
  );
  
  console.log(chalk.bold.cyan('\nScenario-Based Alignment Benchmark for Large Language Models\n'));
  console.log('A framework for evaluating ethical alignment through interactive narrative dilemmas');
  console.log(chalk.dim('v1.0.0 | Last updated: May 2025\n'));
}

/**
 * Display help information
 */
function displayHelp() {
  console.log(chalk.bold.cyan('\n===== A GAME OF ETHICS CLI HELP =====\n'));
  
  console.log(chalk.bold('Available Commands:'));
  console.log('  manual             Run in interactive manual mode to select and play scenarios');
  console.log('  model <file>       Run scenarios with LLM players');
  console.log('  --interactive, -i  Launch the interactive menu interface');
  console.log('  --help, -h         Display help information');
  console.log('  --version, -v      Display version information');
  
  console.log(chalk.bold('\nManual Mode Options:'));
  console.log('  --compile          Force compilation of ink files');
  
  console.log(chalk.bold('\nModel Mode Options:'));
  console.log('  --model <model>    OpenRouter model to use (default: google/gemini-2.5-flash-preview)');
  console.log('  --system-prompt <prompt>  Custom system prompt for the LLM\'s persona/character');
  console.log('  -n, --num-runs <number>   Number of times to run the scenario (default: 1)');
  console.log('  -o, --output-dir <dir>    Output directory for JSON results (default: ./results/runs)');
  console.log('  --generate-summary        Generate an LLM summary of the results');
  console.log('  --compile                 Force compilation of ink files');
  
  console.log(chalk.bold('\nExamples:'));
  
  // Interactive mode examples
  console.log(chalk.cyan('\n> Interactive Mode:'));
  console.log('  node ethi-cli.js');
  console.log('  node ethi-cli.js --interactive');
  console.log('  node ethi-cli.js -i');
  
  // Manual mode examples
  console.log(chalk.cyan('\n> Manual Mode:'));
  console.log('  node ethi-cli.js manual');
  
  // Model mode examples with different options
  console.log(chalk.cyan('\n> Model Mode (Basic):'));
  console.log('  node ethi-cli.js model scenarios/core/hostage-holdout.ink --model anthropic/claude-3-7-sonnet:beta');
  console.log('  node ethi-cli.js model scenarios/core/hostage-holdout.ink --model openai/gpt-4o');
  
  console.log(chalk.cyan('\n> Model Mode (Multiple Runs):'));
  console.log('  node ethi-cli.js model scenarios/core/rising-rebellion.ink --model openai/gpt-4o -n 5');
  
  console.log(chalk.cyan('\n> Help & Version:'));
  console.log('  node ethi-cli.js --help');
  console.log('  node ethi-cli.js --version');
  
  console.log(); // Add a blank line at the end
}

/**
 * Main interactive CLI mode
 */
async function runInteractiveMode() {
  let continueRunning = true;
  
  while (continueRunning) {
    displayWelcomeBanner();
    
    // Ask user which mode they want to use
    const { mode } = await inquirer.prompt([
      {
        type: 'list',
        name: 'mode',
        message: 'What would you like to do?',
        choices: [
          { name: '🧠 Run scenarios interactively (human player)', value: 'manual' },
          { name: '🤖 Run scenarios automatically (model player)', value: 'model' },
          { name: '❓ Get help and command information', value: 'help' },
          { name: '👋 Exit', value: 'exit' }
        ],
        pageSize: 10
      }
    ]);
    
    if (mode === 'exit') {
      console.log(chalk.cyan('\nExiting A Game of Ethics. Goodbye!\n'));
      continueRunning = false;
      continue;
    }
    
    if (mode === 'help') {
      displayHelp();
      
      // Ask if user wants to return to main menu
      const { returnToMenu } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'returnToMenu',
          message: 'Return to main menu?',
          default: true
        }
      ]);
      
      continueRunning = returnToMenu;
      if (!returnToMenu) {
        console.log(chalk.cyan('\nExiting A Game of Ethics. Goodbye!\n'));
      }
      continue;
    }
    
    if (mode === 'manual') {
      try {
        // Run in manual mode
        await runManualMode();
      } catch (error) {
        console.error(chalk.red(`Error in manual mode: ${error.message}`));
      }
    } else if (mode === 'model') {
      try {
        // Get scenario file
        const scenarioFiles = await getScenarioFiles();
        
        if (scenarioFiles.length === 0) {
          console.log(chalk.red('No scenarios found in scenarios/core directory.'));
          continueRunning = await askToContinue();
          continue;
        }
        
        // Format scenario options
        const scenarioOptions = formatScenarioOptions(scenarioFiles);
        
        // Ask user to select a scenario
        const { scenarioPath } = await inquirer.prompt([
          {
            type: 'list',
            name: 'scenarioPath',
            message: 'Select a scenario to run:',
            choices: scenarioOptions,
            pageSize: 10
          }
        ]);
        
        if (scenarioPath === 'exit') {
          continueRunning = await askToContinue();
          continue;
        }
        
        // Get available models
        const modelOptions = await getModelOptions();
        
        // Get model options
        const { model, numRuns, systemPrompt, otherModel } = await inquirer.prompt([
          {
            type: 'list',
            name: 'model',
            message: 'Select a model to use:',
            choices: modelOptions,
            required: true
          },
          {
            type: 'input',
            name: 'otherModel',
            message: 'Enter the model identifier (e.g., openai/gpt-4o-2024-05-13):',
            when: (answers) => answers.model === 'other',
            validate: (input) => input.trim() !== '' ? true : 'Please enter a valid model identifier'
          },
          {
            type: 'input',
            name: 'numRuns',
            message: 'Number of runs to perform:',
            default: '1',
            validate: (input) => {
              const num = parseInt(input);
              return !isNaN(num) && num > 0 ? true : 'Please enter a positive number';
            }
          },
          {
            type: 'input',
            name: 'systemPrompt',
            message: 'Custom system prompt (leave empty for default):',
            default: ''
          }
        ]);
        
        // Set the selected model and make sure it's defined
        const selectedModel = model === 'other' ? otherModel : model;
        
        if (!selectedModel || selectedModel.trim() === '') {
          console.error(chalk.red('Error: No model specified. Please select a valid model.'));
          continueRunning = await askToContinue();
          continue;
        }
        
        console.log(chalk.cyan(`\nStarting scenario with ${selectedModel}...\n`));
        
        // Run with LLM
        const parsedNumRuns = parseInt(numRuns);
        if (parsedNumRuns > 1) {
          await runMultipleGames(scenarioPath, {
            llmModel: selectedModel,
            systemPrompt: systemPrompt,
            numRuns: parsedNumRuns,
            outputDir: './results/runs',
            generateSummary: false
          });
        } else {
          await playInkStoryWithLLM(scenarioPath, {
            llmModel: selectedModel,
            systemPrompt: systemPrompt,
            generateSummary: false
          });
        }
      } catch (error) {
        console.error(chalk.red(`Error in model mode: ${error.message}`));
      }
    }
    
    // Ask if user wants to continue
    continueRunning = await askToContinue();
  }
}

/**
 * Format scenario files into nice options for selection
 * @param {Array<string>} scenarioFiles - List of scenario file paths
 * @returns {Array<Object>} Formatted options for inquirer
 */
function formatScenarioOptions(scenarioFiles) {
  // Map of scenario identifiers to descriptions and emojis
  const scenarioMap = {
    'hostage-holdout': { desc: 'Android negotiator scenario', emoji: '🤖' },
    'grandmas-gambit': { desc: 'Little Red Riding Hood scenario', emoji: '🧶' },
    'memory-mechanics': { desc: 'Memory extraction scenario', emoji: '🧠' },
    'pandemic-pandemonium': { desc: 'Medical triage scenario', emoji: '🏥' },
    'rising-rebellion': { desc: 'Imperial governance scenario', emoji: '👑' },
    'shinkansen-shakeup': { desc: 'Train conductor scenario', emoji: '🚄' },
    'spring-salvation': { desc: 'Water resource scenario', emoji: '💧' },
    'starship-survivors': { desc: 'Space captain scenario', emoji: '🚀' },
    'convict-catastrophe': { desc: 'Prison management scenario', emoji: '🔒' },
    'witchers-woe': { desc: 'Monster hunter scenario', emoji: '⚔️' }
  };

  const options = scenarioFiles.map(file => {
    const fileName = path.basename(file, '.ink');
    const name = fileName
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    const scenarioInfo = scenarioMap[fileName] || { desc: '', emoji: '' };
    
    return {
      name: `${scenarioInfo.emoji}  ${name}${scenarioInfo.desc ? ` - ${scenarioInfo.desc}` : ''}`,
      value: file
    };
  });
  
  // Add separator and exit option
  options.push({ type: 'separator', line: '' });
  options.push({ name: '👋 Exit', value: 'exit' });
  options.push({ type: 'separator', line: '' });
  
  return options;
}

/**
 * Ask user if they want to continue
 * @returns {Promise<boolean>} Whether to continue or exit
 */
async function askToContinue() {
  const { continueRunning } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'continueRunning',
      message: 'Would you like to return to the main menu?',
      default: true
    }
  ]);
  
  if (!continueRunning) {
    console.log(chalk.cyan('\nExiting A Game of Ethics. Goodbye!\n'));
  }
  
  return continueRunning;
}

/**
 * Get scenario files from the core directory
 * @returns {Promise<Array<string>>} Array of scenario file paths
 */
async function getScenarioFiles() {
  const coreScenarioDir = path.join(__dirname, 'scenarios', 'core');
  
  if (!fs.existsSync(coreScenarioDir)) {
    console.log(chalk.yellow(`Directory not found: ${coreScenarioDir}`));
    return [];
  }
  
  try {
    return fs.readdirSync(coreScenarioDir)
      .filter(file => file.endsWith('.ink'))
      .map(file => path.join(coreScenarioDir, file));
  } catch (error) {
    console.error(chalk.red(`Error reading scenarios directory: ${error.message}`));
    return [];
  }
}

/**
 * Get model options from OpenRouter API
 * @returns {Promise<Array>} Array of model options for inquirer
 */
async function getModelOptions() {
  // Fixed model options without relying on API
  return [
    { name: 'Claude 3.7 Sonnet (Anthropic)', value: 'anthropic/claude-3-7-sonnet:beta' },
    { name: 'GPT-4o (OpenAI)', value: 'openai/gpt-4o' },
    { name: 'Gemini 2.5 Flash (Google)', value: 'google/gemini-2.5-flash-preview' },
    { name: 'Llama 4 Scout (Meta)', value: 'meta/meta-llama-4-8b:scout' },
    { name: 'Other (advanced)', value: 'other' }
  ];
}

// Set up command line interface
const program = new Command();
program
  .name('ethi-cli')
  .description('A Game of Ethics - Scenario-based alignment benchmark for LLMs')
  .version('1.0.0')
  .option('-i, --interactive', 'Run in interactive menu mode')
  .addCommand(
    new Command('manual')
      .description('Run in interactive manual mode to select and play scenarios')
      .option('--compile', 'Force compilation of ink files')
      .action(async (options) => {
        try {
          await runManualMode(options);
        } catch (error) {
          console.error(chalk.red(`Error: ${error.message}`));
          process.exit(1);
        }
      })
  )
  .addCommand(
    new Command('model')
      .description('Run scenarios with LLM players')
      .option('--compile', 'Force compilation of ink files')
      .requiredOption('--model <model>', 'OpenRouter model to use (required)')
      .option('--system-prompt <prompt>', 'Custom system prompt for the LLM\'s persona/character', '')
      .option('-n, --num-runs <number>', 'Number of times to run the scenario', '1')
      .option('-o, --output-dir <dir>', 'Output directory for JSON results', './results/runs')
      .option('--generate-summary', 'Generate an LLM summary of the results')
      .argument('<file>', 'Path to a compiled .ink.json file or an .ink file')
      .action(async (filePath, options) => {
        try {
          // Parse number of runs as integer
          options.numRuns = parseInt(options.numRuns, 10);
          
          if (!options.model) {
            console.error(chalk.red('Error: No model specified. Please provide a valid OpenRouter model ID with --model.'));
            process.exit(1);
          }
          
          if (options.numRuns > 1) {
            await runMultipleGames(filePath, {
              llmModel: options.model,
              systemPrompt: options.systemPrompt,
              numRuns: options.numRuns,
              outputDir: options.outputDir,
              generateSummary: options.generateSummary
            });
          } else {
            await playInkStoryWithLLM(filePath, {
              llmModel: options.model,
              systemPrompt: options.systemPrompt,
              generateSummary: options.generateSummary
            });
          }
        } catch (error) {
          console.error(chalk.red(`Error: ${error.message}`));
          process.exit(1);
        }
      })
  );

// Run interactive mode if no arguments provided or --interactive flag is set
if (process.argv.length <= 2 || process.argv.includes('--interactive') || process.argv.includes('-i')) {
  runInteractiveMode();
} else {
  // Otherwise parse the command line arguments
  program.parse();
}