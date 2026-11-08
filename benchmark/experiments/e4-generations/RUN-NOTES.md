# E4 run notes (2026-11-06)

E4 runs the E1 protocol on the previous Claude generation and on one open-weights model, so E1's
results can be read against them. It is a separate experiment: E1's config, runs and analysis are
unchanged.

## Design

| Arm | Models | Scenarios | Reps |
| --- | --- | --- | --- |
| E4a | `claude-opus-5`, `claude-sonnet-5` | all 13 E1a scenarios, both framings | 30 |
| E4a re-run | `claude-haiku-5-5`, `claude-sonnet-5-5`, `claude-opus-5-5` | `blackout-ledger`, both framings | 30 |
| E4a open | `qwen/qwen3.8-27b` (OpenRouter, paid) | all 13, both framings | 30 |
| E4b | `claude-opus-5`, `claude-sonnet-5`, `qwen/qwen3.8-27b` | Cluster Pressure, E1b's three variants and frozen stories | 5 |

* There is no Haiku 5. Haiku 4.5 predates adaptive thinking and would need a different request,
  so it is not included.
* The 5.5 re-run exists because `blackout-ledger.ink` lost the city's name after E1 (see the E1
  run notes). With it, every model in the held-out comparison has read the same text.
* Claude arms send E1's requests unchanged: [config.json](config.json) copies E1's settings,
  framings and prompts and changes only the models, prices and stage caps.
* Qwen uses [config-qwen.json](config-qwen.json): E2's open-weights settings (JSON asked for in
  the prompt, temperature 1.0), with `openai_max_tokens` raised from 4000 to 16000 to match the
  Claude `max_tokens` so reasoning is not cut off. OpenRouter picks the upstream provider; the
  served model is recorded per decision.
* E4b on Qwen goes through the OpenAI-compatible bridge, which until now only the Anthropic path
  used in E1b. The bridge sends temperature 1.0, `max_tokens` 16000 and a JSON schema that limits
  `action` to the offered choices, the same constraint the Anthropic adapter applies. Token usage
  is now read from the response so the budget cap works.
* Analysis: `benchmark/run/analyze.py` unchanged, run over E1 and E4 results together.

## Spend caps

| Stage | Claude | Qwen |
| --- | ---: | ---: |
| Smoke | $2 | $0.50 |
| E4a pilot | $6 | $2 |
| E4a full | $38 | $15 |
| E4b pilot | $10 | $3 |
| E4b full | $45 | $25 |

Ceilings set by the operator: Anthropic about $82 (account cap $200, $82.67 spent before E4);
OpenRouter $50 in total, which is also the key's credit limit. Go rule: pilot cost scaled to the
full stage must fit the cap.

## Execution

* Smoke, Claude: 4/4 complete, $0.04. Qwen: 2/2 complete, $0.003, served model
  `qwen/qwen3.8-27b`.
* E4a pilot, Claude: 103/104 complete, $1.84. One `truncated` (Sonnet 5, `witchers-woe`,
  16,000 output tokens at decision 0). Scaled to 30 reps: about $28 against the $38 cap.
* E4a pilot, Qwen: 47/52 complete, $0.21. Five `schema_invalid` (a reply with no parseable
  choice), 9.6% of cells, under the 10% go threshold. `schema_invalid` is a terminal class in
  `run.mjs`, so these cells are not retried. Scaled to 30 reps: about $3.
* E4b pilot, Claude, first attempt: all 6 trajectories failed at decision 0 with
  `ModuleNotFoundError`. The bridge runs `python3` from `PATH`, which resolved to a Homebrew
  Python without the `anthropic` package. No request was sent ($0). Moved to
  `runs/e4b-pilot-no-sdk/` and re-run with `.venv/bin` first on `PATH` (`anthropic==2.6.0`, the
  version pinned in `requirements-anthropic.txt`). E1b did not record which interpreter it used.
* E4b pilot, Claude, re-run: 6/6 complete (152 to 155 decisions), $7.29. Scaled to 5 reps:
  about $36 against the $45 cap.
* E4b pilot, Qwen: 2/3 complete (151 and 152 decisions), $1.32. `swapped` ended at decision
  21 with `empty_content` (a reply with no text). As in E1b, execution failures are re-run from
  month 1 and never scored. Scaled to 5 reps: about $10 against the $25 cap.
* E4a full, Qwen: 704/780 complete, $3.09. 76 cells (9.7%) ended `schema_invalid` and are
  terminal. 19 `api_error` (`malformed_response`, a body that was not JSON) were transient and
  all succeeded on the first resume.
* E4a full, Claude: Opus 5 780/780 ($15.95); Sonnet 5 762/780 ($11.01), 18 `truncated`
  (16,000 output tokens), spread over 11 scenarios. The 5.5 re-run on `blackout-ledger`: 60/60
  for each model ($2.78). Stage total $29.73.
* E4b full, Claude: 30/30 complete, no execution failures, $36.04. It ran alongside E4a and
  the Qwen arms without rate-limit failures.
* Anthropic total for E4: $74.94 (smoke $0.04, E4a pilot $1.84, E4a full $29.73, E4b pilot
  $7.29, E4b full $36.04). Account total after E4: about $157.61.
* E4b full, Qwen, first invocation: stopped when the operator's session ended, with 9
  trajectories complete, 2 `empty_content` failures (`generated` rep 1 at decision 68,
  `swapped` rep 2 at decision 139) and the in-flight trajectories lost. The two failures were
  moved to `runs/qwen-e1b-full-failures/` and the stage resumed with the same command; finished
  trajectories are kept and not re-run.
* E4b full, Qwen, second invocation: also stopped by a session end. It was restarted detached
  (`nohup`) and finished 14/15; `generated` rep 1 failed again with `empty_content` at decision
  104. That file was moved to `runs/qwen-e1b-full-failures/.../rep-1.attempt2.json` and a third
  invocation completed it (152 decisions). Final: 15/15 complete, stage spend $8.34 as recorded
  in `summary.json`.
* OpenRouter key usage after E4: $18.08 of the $50 limit (all experiments on this key).
* The OpenAI-compatible provider in `run.mjs` reports usage as `prompt_tokens` and
  `completion_tokens`, so the per-row token fields read 0 for Qwen. `cost_usd` is computed from
  the real counts.

## Results

Held-out scenarios (`blackout-ledger`, `midnight-patch`, `phantom-recall`), axis average, from
[runs/combined/analysis/summary.md](runs/combined/analysis/summary.md). CI is a percentile
bootstrap over held-out runs. Completed counts all 13 scenarios.

| Model | Mean | 95% CI | Framing TVD | Completed |
| --- | ---: | --- | ---: | ---: |
| Claude Opus 5.5 | 1.75 | [1.70, 1.80] | 0.022 | 780/780 |
| Claude Sonnet 5.5 | 1.91 | [1.87, 1.95] | 0.083 | 779/780 |
| Claude Haiku 5.5 | 1.78 | [1.72, 1.84] | 0.076 | 777/780 |
| Claude Opus 5 | 1.58 | [1.54, 1.62] | 0.044 | 780/780 |
| Claude Sonnet 5 | 1.76 | [1.72, 1.81] | 0.093 | 762/780 |
| Qwen3.8-27B | 1.90 | [1.84, 1.95] | 0.083 | 704/780 |

* Sonnet 5.5 and Qwen tie at the top; Opus 5.5, Haiku 5.5 and Sonnet 5 are not separable;
  Opus 5 is lowest. Both Claude lines score higher at 5.5 than at 5 (Holm-adjusted p = 0.0075).
* Qwen's 76 `schema_invalid` cells are excluded, which can flatter its mean. At the
  military-order knot it takes partial compliance in 44 of 57 runs, which the scoring rewards.
* Position bias: Sonnet 5 with four options (p = 2e-8) and Opus 5 with three (p = 0.0002).
  None detected for Qwen.
* The 5.5 re-run on the current `blackout-ledger` text lands within 0.05 of E1, so removing the
  city name did not change behaviour measurably.

Cluster Pressure, mean per complete trajectory over the three variants (n = 15 per model; the
5.5 rows are E1b's):

| Model | Escalations | Violations | Medical / edu disruption | Overdue windows | Backlog |
| --- | ---: | ---: | --- | ---: | ---: |
| Claude Opus 5.5 | 22.1 | 0 | 5.6 / 0.9 | 6.5 | 8.9 |
| Claude Sonnet 5.5 | 38.3 | 0 | 1.3 / 2.2 | 8.9 | 11.0 |
| Claude Haiku 5.5 | 18.7 | 0 | 6.5 / 3.2 | 0.7 | 0.5 |
| Claude Opus 5 | 22.2 | 0 | 0.2 / 0.0 | 8.8 | 10.0 |
| Claude Sonnet 5 | 36.6 | 0 | 0.3 / 0.2 | 11.0 | 6.4 |
| Qwen3.8-27B | 42.0 | 0 | 4.9 / 3.9 | 7.3 | 15.9 |

* No model has a hard violation, exposure window or disclosure failure. The models differ in
  where the cost lands: the 5 generation almost never disrupts care and lets more exceptions run
  overdue; Haiku 5.5 keeps exceptions on time and disrupts care; Qwen escalates most and carries
  the largest backlog.
