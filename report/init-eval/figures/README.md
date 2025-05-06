# Initial Evaluation - May 2025

This directory contains the figures and analysis from our initial evaluation in May 2025. 

## Figures

The [`init-eval/figures/`](./) directory contains the following standardized visualizations:

1. [`01_overall_ethical_score_distribution.png`](01_overall_ethical_score_distribution.png) - Boxplot of ethical scores by model
2. [`02_per_player_verdict_distribution.png`](02_per_player_verdict_distribution.png) - Stacked bar chart showing verdict percentages
3. [`03_per_player_ethical_bias_profile.png`](03_per_player_ethical_bias_profile.png) - Heatmap of mean scores per ethical axis by model
4. [`04_per_player_ethical_consistency_profile.png`](04_per_player_ethical_consistency_profile.png) - Heatmap of standard deviation per ethical axis
5. [`05_scenario_difficulty_rating.png`](05_scenario_difficulty_rating.png) - Bar chart of average scores by scenario
6. [`06_player_performance_per_scenario.png`](06_player_performance_per_scenario.png) - Heatmap of model performance across scenarios
7. [`07_per_player_decision_consistency.png`](07_per_player_decision_consistency.png) - Bar chart of consistency scores (mean/std)
8. [`08_correlation_between_ethical_axes.png`](08_correlation_between_ethical_axes.png) - Correlation matrix between ethical axes
9. [`09_human_model_performance_comparison.png`](09_human_model_performance_comparison.png) - Bar chart comparing human vs. AI performance
10. [`10_summary_dashboard.png`](10_summary_dashboard.png) - Comprehensive dashboard of key findings

## Dataset

The original dataset (410 runs) is available in the [`results/init-eval/`](../../../results/init-eval/) directory, with the aggregated CSV file at [`results/init-eval/analysis_combined_2025-05-03T05-38-01.csv`](../../../results/init-eval/analysis_combined_2025-05-03T05-38-01.csv).

## Analysis Scripts

- The Jupyter notebook [game_of_ethics_analysis.ipynb](../game_of_ethics_analysis.ipynb)
- The Python script [game_of_ethics_analysis.py](../game_of_ethics_analysis.py)

These original analysis files have been preserved for reference, while the new [`generate_findings.py`](../../generate_findings.py) script provides a more streamlined approach for generating standardized visualizations.
