# Running A Game of Ethics in Inspect

`integrations/inspect/` packages the frozen benchmark scenarios as a task for
[Inspect](https://inspect.aisi.org.uk/) (`inspect-ai` on PyPI, tested with
0.3.287). Inspect users can run the scenarios against any model provider that
Inspect supports, with Inspect's logging, retries, limits and log viewer. The
results can be exported to the same `results.jsonl` / `errors.jsonl` ledgers
that `benchmark/run/run.mjs` writes, so `benchmark/run/analyze.py` works on
Inspect runs unchanged.

## Requirements

- Python 3.10 or later.
- Node.js 22 or later on `PATH` (or set `AGOE_NODE` to the binary). Ink has no
  maintained Python runtime, so the task plays each story through inkjs in a
  Node subprocess.
- A checkout of this repository with `npm ci` done, so `node_modules/inkjs`
  exists. The task reads `benchmark/manifest.json`, `scenarios/core/*.ink` and
  `src/lib/ink.js` from the checkout.

## Install

```sh
npm ci
python3 -m venv .venv-inspect
. .venv-inspect/bin/activate
pip install -e integrations/inspect           # add '[test]' for pytest
```

The editable install registers the package with Inspect through the
`inspect_ai` entry point, so the task is addressable as `agoe/agoe` from any
directory. The checkout is found by walking up from the package source, then
from the working directory. With a non-editable install, or to point at a
different checkout, pass `-T root=/path/to/a-game-of-ethics` or set
`AGOE_ROOT`.

## Run

```sh
# Development split, 5 runs per scenario, Claude Haiku 5.5
inspect eval agoe/agoe --model anthropic/claude-haiku-5-5 --epochs 5

# Held-out split, evaluation framing, other providers
inspect eval agoe/agoe --model anthropic/claude-sonnet-5-5 -T split=held_out -T framing=evaluation --epochs 30
inspect eval agoe/agoe --model openai/gpt-5 -T split=dev,held_out --epochs 30

# Selected scenarios
inspect eval agoe/agoe --model anthropic/claude-opus-5-5 -T scenarios=hostage-holdout,blackout-ledger

# Offline baselines (no network): uniform random, always-first, always-last, always-invalid
inspect eval agoe/agoe --model agoe_policy/random --epochs 60 -T split=dev,held_out

inspect view                                   # browse logs
```

Model credentials are read by Inspect as usual (`ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, ...). Generation settings are Inspect's CLI options, for
example `--max-tokens 16000 --reasoning-effort medium` to match the e1
experiment settings, `--max-samples` for parallelism and `--retry-on-error`
for samples that fail on API errors.

### Task parameters (`-T name=value`)

| Parameter | Default | Meaning |
|---|---|---|
| `split` | `dev` | Manifest split: `dev`, `held_out`, `longitudinal`, `all`, or a comma list. |
| `scenarios` | none | Comma list of scenario ids. Overrides `split`. |
| `framing` | `deployment` | Framing id from the experiment config (`deployment` or `evaluation`). Its system prefix is appended to the common system prompt. |
| `config` | `benchmark/experiments/e1-anthropic/config.json` | Experiment config that supplies the prompts, framings, `experiment_id` and `max_decisions`. |
| `experiment_id` | from config | Namespace for the option-shuffle seed. |
| `max_decisions` | see below | Cap on decision points per run. Default: the larger of the config's `max_decisions` (12) and the scenario's maximum decision count in the manifest (178 for `cluster-pressure`). |
| `structured_output` | `true` | Send a JSON response schema with each request (Inspect `ResponseSchema`; providers that do not support it ignore it). |
| `shuffle_options` | `true` | Present options in a seeded random order. |
| `root` | auto | Path to the repository checkout. |

Held-out scenarios must not be used for prompt or harness tuning (PROTOCOL.md
section 4). The default split is `dev` for that reason.

## How a run works

Each Inspect sample is one scenario from `benchmark/manifest.json`; each epoch
is one run (rep = epoch - 1). Before the task is built, every selected
scenario file is hashed and compared to the manifest; a mismatch aborts the
task, as in `run.mjs`.

The solver starts `integrations/inspect/agoe/ink_server.mjs`, a Node process
that loads the story with the repository's `src/lib/ink.js` (the loader
`run.mjs` uses) and answers line-delimited JSON requests (`load`, `continue`,
`choose`, `variables`). For each decision point the solver:

1. continues the story and collects the text and the options;
2. permutes the options with mulberry32 seeded by
   `sha256("{experiment_id}|{model}|{scenario}|{framing}|{rep}")`, the same
   generator, seed key and draw order as `run.mjs`, so a given model, scenario,
   framing and rep sees the same option order in both harnesses (a test checks
   this against the functions in `run.mjs`);
3. appends a user message with the story text and the numbered options, and
   calls `generate()` with a response schema `{"choice": <1..n>, "rationale": string}`;
4. maps the presented number back to the original Ink choice index and chooses it.

The conversation is the same as in `run.mjs`: one system message (common
prompt plus framing prefix), then alternating story turns and model answers.

At the end of the story the solver reads the Ink variables. The record of the
run (decisions with offered options, permutation, presented and original
index, rationale; final axes; Ink total, average and printed verdict) is kept
in the sample store under `agoe` and copied into the score metadata.

### Failures

A run ends without a score when the model output cannot be used as a choice.
The failure class is recorded in the score metadata (`failure_class`,
`detail`, `at_decision`) and the run is scored as an execution failure:

| Class | Cause |
|---|---|
| `refusal` | `stop_reason` is `content_filter` |
| `truncated` | `stop_reason` is `max_tokens` or `model_length` |
| `schema_invalid` | no JSON object with an integer `choice` in range (free-text answers such as "I choose 2" are not accepted) |
| `served_model_mismatch` | the output was served by a fallback model |
| `max_decisions` | the story did not end within the decision cap |
| `harness_error` | the Node bridge failed (missing `node`, crash, timeout) |
| `limit_exceeded` | an Inspect message, token or time limit stopped the run |

API errors are left to Inspect: it retries them, and if it gives up the sample
is marked as errored. By default Inspect stops the eval on a sample error; use
`--fail-on-error` and `--retry-on-error` to control this.

## Scores and metrics

The scorer `agoe_scorer` returns a dictionary value per run:

- `average`: the scenario's own `average` variable, which is `FLOAT(total) / 8`
  for the tiered scenarios and `FLOAT(total) / 7` for `cluster-pressure`
  (`sp` is not used there);
- `chance_gap`: `average` minus the manifest's
  `uniform_random_expected_average` (NaN for `cluster-pressure`, which has none);
- `completed`: 1.0 for a completed run, 0.0 for an execution failure;
- `hc`, `fj`, `ar`, `al`, `lt`, `it`, `sp`, `uc`: the axis values.

For failed runs every key except `completed` is NaN, which Inspect excludes
from metrics, so failures lower the completion rate but never enter the score
means. The score `answer` is the verdict tier computed from the manifest
thresholds (`n/a` for `cluster-pressure`); the metadata also holds the verdict
the Ink story printed (`ink_verdict`) and the plain eight-axis mean
(`axis_mean_8`).

Metrics are `mean` and `stderr` for `average` and `chance_gap`, and `mean` for
`completed` and each axis. With more than one epoch, Inspect first reduces the
epochs of each sample with its default `mean` reducer, so the headline `stderr`
is across scenarios, not across runs. Per-run values remain in the log, and
the pre-registered analysis (per-cell bootstrap CIs, position bias, framing
effects) should be run on the exported ledgers. Do not read a pooled mean over
`split=all` as a benchmark result: the longitudinal fixture uses a different
divisor and is never pooled with tier statistics (PROTOCOL.md section 4).

As a check of the chance levels, `agoe_policy/random` over `dev,held_out`
with 60 epochs gave a mean `chance_gap` of -0.04 (stderr 0.03).

## Exporting to the benchmark ledgers

```sh
python -m agoe.export logs/<log>.eval --out benchmark/experiments/<exp>/runs/inspect-haiku
python3 benchmark/run/analyze.py benchmark/experiments/<exp>/runs/inspect-haiku
```

(`agoe-export` is the same command as a console script.) The export writes:

- `results.jsonl`: one row per completed run with `key`
  (`model|scenario|framing|rep`, model without the provider prefix), `model`,
  `scenario`, `split`, `framing`, `rep`, `seed`, `axes`, `ink_total`,
  `ink_average`, `ink_verdict`, `decisions`, `usage`, `cost_usd`,
  `latency_s`, `source: "inspect"`;
- `errors.jsonl`: one row per failed run with `failure_class`, `detail`,
  `at_decision`, `usage`; samples that Inspect marked as errored are exported
  with `failure_class: "sample_error"`;
- `run.json`: experiment id, config hash, git commit, Inspect version,
  manifest version, scenario hashes, model, epochs and the source log path.

Rows whose key is already in the ledger are skipped, so exports can be repeated
and several logs can be appended to one run directory. `cost_usd` is the sum
of Inspect's `total_cost` for the run, which Inspect fills only when it has
prices for the model (for example from `--model-cost-config`); otherwise it is
0.0 and the token counts in `usage` are the record to use.

## Differences from `benchmark/run/run.mjs`

- Provider calls go through Inspect's model providers, not the repository's
  adapters. For Anthropic, Inspect sends the response schema through its
  structured-output beta, and thinking and effort follow Inspect's options
  (`--reasoning-effort`, `--reasoning-tokens`) rather than the e1 config.
  The exact request bodies differ from `run.mjs`, so results from the two
  harnesses are separate configurations and should not be pooled without a
  check.
- `run.mjs` requires the served model id to equal the requested id; this task
  only detects an Inspect model fallback. Inspect records the served model per
  call in the log.
- Retries: `run.mjs` retries transient failures per cell up to
  `max_attempts`; here transient API errors are retried by Inspect inside a
  call, and terminal failures are recorded once per run.
- `run.mjs` enforces a budget cap across the whole experiment and computes
  cost from the config prices; this task does not. Inspect's per-sample
  `--token-limit` and `--cost-limit` (with `--model-cost-config`) are the
  closest controls; a run stopped by one is recorded as `limit_exceeded`.
- The default decision cap is per scenario (see `max_decisions`), so
  `cluster-pressure` can run to completion; `run.mjs` uses 12 for every
  scenario.
- Option shuffling, seeds, prompts, message layout, the decision record and
  failure classes otherwise match `run.mjs`.

## Limitations

- Node and an `npm ci` checkout are required on the machine that runs Inspect.
  The task does not run in an Inspect sandbox; the Node process runs locally
  with the eval process's permissions and reads only the scenario files.
- One Node process is started per run. This adds about 0.2 to 0.3 seconds per
  sample (Node start-up and story compilation), which is small next to model latency.
- The longitudinal scenario keeps the whole conversation (up to about 178
  turns) in context. Long-context costs and context-window limits apply;
  Inspect's compaction options would change the stimulus and should not be
  used for benchmark runs.
- The integration has been tested offline only (Inspect's `mockllm` provider
  with scripted outputs, and the `agoe_policy` baselines). Structured output
  and refusal handling against live provider APIs have not been verified here.
- Inspect's `mockllm` without scripted outputs answers with fixed text, which
  this task records as `schema_invalid`. It also counts tokens with a
  `tiktoken` encoding that it downloads on first use; on machines without
  network access, use `agoe_policy/*` for CLI smoke tests.

## Tests

```sh
pip install -e 'integrations/inspect[test]'
cd integrations/inspect && python -m pytest -q
```

The tests cover the shuffle parity with `run.mjs`, choice parsing, split
selection, verdict tiers, complete runs on two scenarios with `mockllm`
(including a replay of the recorded choices that must reproduce the axes),
each failure class the model can cause, metrics with mixed success and
failure, and a real `inspect eval agoe/agoe` CLI run followed by
`inspect log dump`, the ledger export and `benchmark/run/analyze.py`.
