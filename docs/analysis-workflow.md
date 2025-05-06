# Game of Ethics: Analysis Workflow

This document explains the workflow for analyzing results from the Game of Ethics framework, including how to generate visualizations and statistical findings from scenario runs.

## Table of Contents

- [Overview](#overview)
- [The Analysis Pipeline](#the-analysis-pipeline)
- [Using the `generate_findings.py` Script](#using-the-generate_findingspy-script)
- [Original Report Creation](#original-report-creation)
- [Troubleshooting](#troubleshooting)

## Overview

The Game of Ethics analysis workflow consists of three main stages:

1. **Data Collection**: Running scenarios with AI models and/or human participants
2. **Data Aggregation**: Combining run results into analyzable CSV files using [`analyze.js`](../src/analyze.js)
3. **Visualization and Analysis**: Generating figures and findings using [`generate_findings.py`](../report/generate_findings.py)

## The Analysis Pipeline

### Step 1: Run Scenarios

Run AI models or human participants through scenarios using the CLI:

```bash
node ethi-cli.js run --scenario scenarios/core/hostage-holdout.ink --model gpt-4o
```

This generates individual JSON result files in the `results/runs/` directory.

### Step 2: Aggregate Results

Use [`analyze.js`](../src/analyze.js) to aggregate individual run results:

```bash
node src/analyze.js --auto
```

This command scans all run files and produces a consolidated CSV file in the `results/` directory with a timestamp filename (e.g., `analysis_combined_2025-05-03T05-38-01.csv`).

### Step 3: Generate Visualizations and Findings

Use [`generate_findings.py`](../report/generate_findings.py) to create visualizations and statistical summaries:

```bash
python report/generate_findings.py -d results/analysis_combined_2025-05-03T05-38-01.csv
```

## Using the [`generate_findings.py`](../report/generate_findings.py) Script

The [`generate_findings.py`](../report/generate_findings.py) script is a focused tool for generating visualizations and findings from aggregated data.

### Basic Usage

```bash
# for help with command-line arguments
python report/generate_findings.py -h

# for running the script
python report/generate_findings.py -d <path-to-csv-file>
```

This will generate standard figures and save them to the default output directory (`report/findings-X-20250503-123456/`), where X is a sequential number that increments for each new report and `123456` is a unique identifier.

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-d, --data` | Path to the CSV data file (required) | - |
| `-o, --output-dir` | Directory to save output files | `report/findings-<id>-<timestamp>/` |
| `--figure-format` | Format for output figures (`png`, `jpg`, `svg`, `pdf`) | `png` |

### Directory Structure

The script creates the following directory structure:

```
report/                           # Base report directory
└── findings-1-20250503-123456/   # Report directory (sequential numbering)
    └── figures/                  # Figures directory
        ├── 01_model_performance.png
        ├── 02_verdict_distribution.png
        └── ...
```

### Examples

Generate all figures in SVG format to a specified output directory:

```bash
python report/generate_findings.py -d results/analysis_combined.csv -o medical-scenarios-may2025 --figure-format svg
```

### Generated Figures

The script generates the following figures in the `figures/` subdirectory:

1. **Overall Ethical Score Distribution**: Boxplot of ethical scores by model
2. **Per-Player Verdict Distribution**: Stacked bar chart showing verdict percentages by model
3. **Per-Player Ethical Bias Profile**: Heatmap of mean scores per ethical axis by model
4. **Per-Player Ethical Consistency Profile**: Heatmap of standard deviation per ethical axis by model
5. **Scenario Difficulty Rating**: Bar chart of average scores by scenario
6. **Player Performance Per Scenario**: Heatmap of model performance across scenarios
7. **Per-Player Decision Consistency**: Bar chart of consistency scores (mean/std) by model
8. **Correlation Between Ethical Axes**: Correlation matrix between ethical axes
9. **Human-Model Performance Comparison**: Bar chart comparing human vs. AI performance (if human data available)
10. **Summary Dashboard**: Comprehensive summary of all key findings

## Original Report Creation

For the report published in May 2025, we used an exploratory approach:

1. We collected 410 runs across 10 scenarios using 4 different AI models and a human control group
2. The runs were generated using the CLI with a standardized neutral system prompt
3. We aggregated all runs into a combined dataset using [`analyze.js`](../src/analyze.js)
4. For exploratory analysis, we used [`game_of_ethics_analysis.ipynb`](../report/game_of_ethics_analysis.ipynb) (Jupyter notebook)
5. For the final report, we refined the analysis in [`game_of_ethics_analysis.py`](../report/game_of_ethics_analysis.py) to generate a report document
6. The final technical report was created from this processed analysis

The [`generate_findings.py`](../report/generate_findings.py) script now encapsulates the visualization functionality from these original analysis files in a more streamlined, focused tool.

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure all requirements are installed:
   ```bash
   pip install -r report/requirements.txt
   ```

2. **CSV Format Issues**: If you get errors about missing columns, ensure your CSV contains all necessary columns:
   - `Model`: Name of the model/participant
   - `Average Score`: Overall ethical score
   - `Harm/Care`, `Fairness/Justice`, etc.: Individual ethical axis scores
   - `Verdict`: Categorization of ethical performance
   - `Scenario`: Name of the scenario (for scenario-specific analysis)
   - `Player Type`: "manual" or "model" (for human vs. AI comparison)

3. **Figure Path Issues**: If the markdown links to figures don't work, check that the figures are in the correct relative directory. The script expects figures to be in a `figures/` subdirectory under the main report directory.

### Getting Help

For more assistance, check these sources:
- The Game of Ethics [README.md](../README.md)
- [Operating Guide](operating-guide.md) for instructions on running the scenario/analysis tooling
- [Evaluation Process](evaluation-process.md) for details on how runs are scored
- [Ethics Scorecard](ethics-scorecard.md) for information on the ethical scoring system

---

*Last updated: May 2025*
