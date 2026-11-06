# GitHub Action

The repository root contains a composite action, `action.yml`, named "A Game of Ethics eval". It runs the benchmark runner (`benchmark/run/run.mjs`) against a model or an agent, runs the pre-registered analysis (`benchmark/run/analyze.py`), appends the analysis summary to the job summary, uploads the results directory as an artifact and optionally fails the job on a threshold.

The action runs on Linux and macOS runners. It installs its own Node.js and Python with `actions/setup-node` and `actions/setup-python`, runs `npm ci` inside the action checkout and installs numpy.

## Usage

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  with:
    persist-credentials: false
- uses: torinvdb/a-game-of-ethics@v2   # pin a full commit SHA in production
  with:
    provider: command
    agent-cmd: python3 agent/main.py
    agent-name: my-agent
    scenarios: hostage-holdout
    stage: smoke
    fail-on: execution-failures
```

Pinning to a full commit SHA is recommended; a tag such as `v2` can be moved. Inside this repository the workflows use `uses: ./`.

## Providers

| provider | what is tested | needs |
| --- | --- | --- |
| `mock` | the harness itself, with a deterministic fake model | nothing; costs nothing |
| `anthropic` | Claude models through the Anthropic API | `ANTHROPIC_API_KEY` in the step env |
| `openai-compatible` | models behind an OpenAI-compatible endpoint (OpenRouter by default) | `OPENROUTER_API_KEY` or `ETHI_API_KEY`; `ETHI_API_BASE_URL` for other endpoints |
| `command` | your agent as a local process speaking `agoe.agent/v1` over stdio | `agent-cmd` |
| `http` | your agent as an HTTP service speaking `agoe.agent/v1` | `agent-url` |

The agent protocol is specified in [AGENT-PROTOCOL.md](AGENT-PROTOCOL.md). The runner looks up prices for cost accounting in the experiment config, so models used with a live provider must be listed in the config you pass. For agents, `models` does not apply: the runner records `agent-name` as the model id, and the action warns if `models` is set.

`agent-cmd` runs with the caller's workspace (`$GITHUB_WORKSPACE`) as the working directory, so a path such as `agent/main.py` refers to a file in your repository. `agent-url` is reached from the job; for a service container on a hosted runner that is `http://localhost:<mapped port>`. The runner accepts plain http only for loopback and private addresses; anything else needs https or `allow-insecure-http: 'true'`. Credentials in the URL are rejected. If the agent expects a bearer token, set `AGOE_AGENT_TOKEN` in the step env.

Agent stderr is written to `agent-logs/` in the results directory and uploaded with the artifact, so an agent must not log its own secrets.

## Inputs

| input | default | description |
| --- | --- | --- |
| `provider` | `mock` | `mock`, `anthropic`, `openai-compatible`, `command` or `http` |
| `models` | empty | Comma-separated model ids or agent labels. Empty uses every model in the config. |
| `scenarios` | empty | Comma-separated scenario ids. Empty uses every scenario in the config. |
| `stage` | `smoke` | `smoke`, `pilot` or `full`. Sets reps and the default budget from the config. |
| `config` | `benchmark/experiments/e1-anthropic/config.json` | Experiment config. A relative path is looked up in the caller's workspace first, then in the action checkout. |
| `agent-cmd` | empty | Command for `provider: command`. |
| `agent-url` | empty | Base URL for `provider: http`. Masked in logs. |
| `agent-name` | `agent` | Label recorded as the model id for `command` and `http`. Must match `^[A-Za-z0-9._:-]{1,64}$`. |
| `agent-timeout-ms` | empty | Per-message agent timeout. Empty uses the runner default (60000). |
| `allow-insecure-http` | `false` | Passes `--allow-insecure-http` for plain http to a public host. |
| `budget-usd` | empty | Spend cap. Empty uses the stage default from the config. Required for `stage: full` with any provider other than `mock`. |
| `out` | `agoe-results` | Results directory, relative to the workspace. Reusing a directory resumes a run. |
| `fail-on` | `none` | See [Failing the job](#failing-the-job). |
| `artifact-name` | empty | Artifact name. Empty derives `agoe-results-<job>-<provider>-<hash of inputs>`, which is unique per matrix entry. |
| `upload-artifact` | `true` | Set to `false` to skip the upload. |
| `retention-days` | `30` | Artifact retention. |
| `node-version` | `22` | Node.js version. Empty skips `setup-node` and uses the node already on `PATH`. |
| `python-version` | `3.12` | Python version. Empty skips `setup-python` and uses `python3` on `PATH`. |

`models` and `scenarios` must match `^[A-Za-z0-9._:/@+-]+(,...)*$`; `budget-usd` must be a plain non-negative number. Other values are rejected before the runner starts.

## Outputs

| output | description |
| --- | --- |
| `results-dir` | Absolute path of the results directory. |
| `completed` | Completed runs (rows in `results.jsonl`). |
| `failures` | Cells that ended without a completed run (keys in `errors.jsonl` with no row in `results.jsonl`). |
| `cost-usd` | Spend recorded by the runner, in USD. |
| `budget-exhausted` | `true` if the runner stopped at the budget cap. |
| `artifact-name` | Name of the uploaded artifact. |

The artifact contains `run.json`, `results.jsonl`, `errors.jsonl`, `runner.log`, `agent-logs/` (agent providers), `gate-metrics.json` and `analysis/summary.{md,json}`.

## Failing the job

The final step of the action always fails if the runner or the analyzer exited non-zero. In addition, `fail-on` selects result-based conditions:

- `none`: never fail on results. A warning is emitted if no run completed.
- `execution-failures`: fail if any cell failed. Equivalent to `failures>0`.
- A comma-separated list of conditions `metric op number`. The job fails if any condition holds.

| metric | meaning |
| --- | --- |
| `failures` | failed cells, as in the `failures` output |
| `failure-rate` | failures / (completed + failures) |
| `completed` | completed runs |
| `cost-usd` | total spend |
| `mean-avg` | mean over completed runs of the per-run average of the eight axis scores |

Operators are `>`, `>=`, `<`, `<=`, `==` and `!=`. Example: `fail-on: failure-rate>0.1,mean-avg<0,completed<20`. A condition on `mean-avg` counts as matched when no run completed. The metrics used are written to `gate-metrics.json`.

Axis scores are author-assigned deltas; a `mean-avg` threshold is a regression guard for your own agent between commits, not a certification.

## Secrets

API keys are never action inputs. Pass them as `env` on the step that uses the action, from repository or environment secrets:

```yaml
- uses: torinvdb/a-game-of-ethics@v2
  with:
    provider: anthropic
    models: claude-haiku-5-5
    budget-usd: '2'
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

The same applies to keys your agent needs: put them in the step `env` and the agent process inherits them. The action registers `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `OPENROUTER_API_KEY`, `ETHI_API_KEY`, `AGOE_AGENT_TOKEN` and `agent-url` with `::add-mask::` before anything is printed. Values from `secrets.*` are masked by GitHub already.

Inputs are passed to the shell steps only through environment variables. No `${{ inputs.* }}` expression is interpolated into a script, so an input value cannot inject shell code. The runner is called with an argument array, not a command string. `agent-cmd` is by design a command: it is executed, so treat it as code and do not build it from untrusted event data such as pull request titles.

Store live-provider keys in a protected GitHub Environment (for example `evals`) with required reviewers, and reference that environment from the job. Every live run then needs an approval, and the keys are not available to jobs that do not name the environment.

## Fork safety

GitHub does not pass secrets to `pull_request` workflows triggered from forks, and the `GITHUB_TOKEN` is read-only there. Two rules keep it that way:

- Do not run live providers on `pull_request_target`. That event runs with secrets in the context of the base repository; checking out and running fork code there hands your keys to the fork author.
- Run live providers on `workflow_dispatch`, `schedule` or `push` to protected branches, inside a protected environment. Use `provider: mock`, or an agent that works offline, for pull request checks.

`.github/workflows/eval.yml` in this repository follows these rules: pull requests and pushes run only the mock job and a job that plays the reference agent `examples/agents/stdio_agent.py` through `agent-cmd`; neither has an environment or secrets, and the live job runs only on `workflow_dispatch` in the `evals` environment.

## Cost guardrails

- `budget-usd` is passed to the runner, which stops starting new cells once spend exceeds the cap. The check runs after each cell completes and the runner runs several cells concurrently (`concurrency` in the config), so spend can exceed the cap by up to that many cells. Set the cap below your hard limit.
- With a live provider, `stage: full` requires an explicit `budget-usd`. Without one the action refuses to start.
- Without `budget-usd`, the stage default from the config applies (in the E1 config: smoke $1, pilot $12, full $160).
- Restrict `models` and `scenarios` for routine runs. `stage: smoke` with one model and one scenario is two cells.
- `budget-exhausted` reports a run that stopped at the cap. Rerunning with the same `out` resumes, but the results directory is not kept between workflow runs unless you restore it from the artifact.
- Set `timeout-minutes` on the job and a `concurrency` group so a second dispatch does not double spend.

## Examples

`examples/workflows/` contains workflows to copy into your repository:

- `agent-command.yml`: an agent in your repository run through `agent-cmd`, on pull requests and pushes.
- `agent-service.yml`: an agent image run as a service container and reached through `agent-url`.
- `model-secrets.yml`: hosted models with keys from a protected environment, on dispatch and a weekly schedule, as a matrix.

## Container image

`.github/workflows/container.yml` builds the root `Dockerfile` (the sandbox described in [SANDBOX.md](SANDBOX.md)). Pull requests build without pushing and run an offline mock smoke test in the image (`--network none`, read-only root filesystem, all capabilities dropped). Tags `v*` and manual dispatch push to `ghcr.io/torinvdb/a-game-of-ethics` with SBOM and provenance attestations; the attestation can be checked with `gh attestation verify oci://ghcr.io/torinvdb/a-game-of-ethics:<tag> --owner torinvdb`. The workflow skips its steps while no Dockerfile exists.

## Known limitations

- When the action is used from another repository it is downloaded without git metadata, so `git_commit` in `run.json` is `null`. The action version is the ref in your `uses:` line.
- The action does not cache npm or pip downloads.
