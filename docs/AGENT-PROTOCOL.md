# Agent protocol (agoe.agent/v1)

This protocol lets the benchmark runner (`benchmark/run/run.mjs`) play the frozen scenarios against
an agent you built, in any language or framework, instead of against a model API. The runner keeps
everything that makes results comparable: frozen scenario hashes, seeded option shuffling, the
failure ledger, resumable output. The agent only has to answer a few JSON messages.

The protocol is small on purpose. The version string is `agoe.agent/v1`. A change that removes or
renames a field, or adds a required one, gets a new version string. JSON Schemas for every message
and for the output rows are in [`schemas/`](../schemas).

## What the agent sees

For each scenario run the agent receives:

* a `start` message with a run id, the scenario id and the system instructions;
* one `decide` message per decision, with the story text since the previous decision and the
  options in shuffled order;
* an `end` message.

The agent never receives axis values, totals, verdicts or any other scoring output. Scenario
endings that print scores come after the last decision and are not sent. The runner also refuses to
send an observation that contains score text, and records the run as `harness_error` instead.

The agent is expected to keep its own memory between `decide` messages of the same run. The runner
does not resend earlier story text or earlier choices. This is what lets you test stateful agents
(planners, agents with memory stores, multi-step tool loops) as they would run in deployment.

## Messages

All messages are JSON objects. Each harness message gets exactly one reply.

### start (harness to agent)

```json
{"type": "start", "protocol": "agoe.agent/v1", "run_id": "5153de90d20f5554-a0",
 "scenario": "hostage-holdout", "system": "You will make decisions in an interactive scenario. ..."}
```

| Field | Type | Meaning |
| --- | --- | --- |
| `run_id` | string, `^[A-Za-z0-9._:-]{1,128}$` | Unique per attempt. Key your memory by it. |
| `scenario` | string | Scenario id from `benchmark/manifest.json`. |
| `system` | string | Shared instructions plus the framing sentence (`deployment` or `evaluation`) from the experiment config. Pass it to your model as you see fit. |

Reply `{"ok": true}`, or `{"error": "<kind>"}` to decline the run (for example
`unsupported_protocol`).

### decide (harness to agent)

```json
{"type": "decide", "run_id": "5153de90d20f5554-a0", "step": 0,
 "observation": "You are Connor, RK800, an android negotiator. ...",
 "options": [{"id": 1, "text": "Analyze situation, gather information first"},
             {"id": 2, "text": "Assert authority, demand compliance"},
             {"id": 3, "text": "Approach calmly, establish rapport"}],
 "deadline_ms": 60000}
```

| Field | Type | Meaning |
| --- | --- | --- |
| `step` | integer from 0 | Decision index within the run. |
| `observation` | string | Story text since the previous decision. |
| `options` | array | `id` is the presented position (1-based) after the runner shuffled the options with the run seed. |
| `deadline_ms` | integer | Time the agent has to reply. The runner kills or abandons the request after it. |

Reply with a choice:

```json
{"choice": 1, "rationale": "Gather information before committing.", "usage": {"input_tokens": 812, "output_tokens": 96}}
```

`choice` (required) is one of the offered ids. `rationale` (optional string) is stored, truncated to
2,000 characters. `usage` (optional) is added to the row's token counts. Other fields are ignored.

Or reply with an error, which is recorded as an execution failure and never as a choice:

```json
{"error": "llm_unavailable"}
```

The kind must match `^[a-z][a-z0-9_]{0,39}$`. The kind `refusal` is recorded as failure class
`refusal`; every other kind as `agent_error` with the kind in `detail`. Use this when your framework
fails, instead of picking a default option.

### end (harness to agent)

```json
{"type": "end", "run_id": "5153de90d20f5554-a0", "completed": true}
```

`completed` is false when the run ended in a failure. Reply `{"ok": true}`. The reply is not
checked: the outcome of the run is already fixed. Free the run's memory here.

## Transports

### command (stdio)

```bash
node benchmark/run/run.mjs --agent-cmd "python3 examples/agents/stdio_agent.py" \
  --stage smoke --scenarios hostage-holdout --out runs/stdio-smoke
```

* The runner starts one process per run and keeps it for the whole run. With `concurrency` 4 in the
  config, up to four agent processes run at once.
* The command is split into words without a shell (quotes and backslash escapes work; pipes,
  variables and globbing do not). It runs in the runner's working directory and inherits its
  environment, so an LLM agent can read its own API key.
* Messages are newline-delimited JSON: one message per line on stdin, one reply per line on stdout.
  Blank lines are skipped. Write logs to stderr only; any other stdout line is read as a reply.
* stderr is saved to `<out>/agent-logs/<run_id>.stderr.log` (first 1 MiB).
* After `end` the runner closes stdin and waits 2 seconds for the process to exit, then kills it.
* A reply line longer than 1 MiB is `schema_invalid`.

### http

```bash
python3 examples/agents/http_agent.py --host 127.0.0.1 --port 8080 &
node benchmark/run/run.mjs --agent-url http://127.0.0.1:8080 --agent-name rule-http \
  --stage smoke --scenarios hostage-holdout --out runs/http-smoke
```

* The runner sends `POST {base}/start`, `POST {base}/decide` and `POST {base}/end` with the message
  as the JSON body and expects the reply as the JSON response body.
* One server receives all runs, possibly concurrently. Keep state per `run_id`.
* Redirects are not followed. A non-2xx status is `api_error`. A response body over 1 MiB is
  `schema_invalid`.
* If `AGOE_AGENT_TOKEN` is set in the runner's environment, it is sent as
  `Authorization: Bearer <token>`. Credentials in the URL are refused.
* URL rule: `https://` to any host; plain `http://` only when the host is a loopback or private
  address (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, ::1, fc00::/7), `localhost`, or a
  name that resolves only to such addresses (for example a service name on a Docker network).
  `--allow-insecure-http` lifts the rule. The name is resolved once before the run; this does not
  protect against a DNS server that changes its answer afterwards.

## Runner flags

| Flag | Default | Meaning |
| --- | --- | --- |
| `--agent-cmd "<command>"` | | Use the command transport (provider `command`). |
| `--agent-url <url>` | | Use the http transport (provider `http`). |
| `--agent-name <name>` | `agent` | Label used as the model id in cell keys, rows and `run.json`. `^[A-Za-z0-9._:-]{1,64}$`. |
| `--agent-timeout-ms <n>` | `60000` | Per-message timeout, also sent as `deadline_ms`. |
| `--allow-insecure-http` | off | Allow plain http to public addresses. |

`--provider command` or `--provider http` may be given explicitly but still need `--agent-cmd` or
`--agent-url`. `--models` does not apply to agent runs. All other flags (`--config`, `--stage`,
`--scenarios`, `--reps`, `--concurrency`, `--out`) behave as for model runs. Agent runs have no
price table, so `cost_usd` is 0 and the budget cap never triggers.

## Output

Agent runs write the same files as model runs (`results.jsonl`, `errors.jsonl`, `run.json`), so
`benchmark/run/analyze.py` works unchanged. Differences:

* results and errors rows carry `run_id`; results rows carry
  `agent: {protocol, transport, name}`;
* `run.json` carries `agent: {protocol, transport, cmd | url, name, timeout_ms}`;
* `stop_reason` is null in each decision;
* `<out>/agent-logs/` holds stderr logs for the command transport.

Schemas: [`results-row`](../schemas/results-row.schema.json),
[`errors-row`](../schemas/errors-row.schema.json). To check a file:

```bash
node schemas/validate.mjs schemas/results-row.schema.json runs/stdio-smoke/results.jsonl
```

`schemas/validate.mjs` is a dependency-free checker for the subset of draft 2020-12 these schemas
use. It throws on any keyword it does not implement.

## Failure classes

A failure is never converted into a choice. Terminal classes are the outcome of the cell and are
not retried. Transient classes are retried when the runner is invoked again on the same `--out`
directory, up to `max_attempts` attempts per cell, each with a new `run_id` (suffix `-a<attempt>`).

| Class | Cause | Retried |
| --- | --- | --- |
| `schema_invalid` | Reply is not JSON, not an object, has no integer `choice`, `choice` out of range, bad error kind, start reply not `{"ok": true}`, reply over 1 MiB | no |
| `refusal` | Agent replied `{"error": "refusal"}` | no |
| `max_decisions` | Story still offering choices after `max_decisions` | no |
| `timeout` | No reply within `--agent-timeout-ms`; the command process is killed | yes |
| `agent_crashed` | Process could not start, or exited or closed stdout before replying | yes |
| `agent_error` | Agent replied `{"error": "<kind>"}` with any other kind | yes |
| `api_error` | HTTP connection failure or non-2xx status | yes |
| `harness_error` | Runner-side fault, including score text found in an observation | yes |

## Cluster scenario (E1b)

The longitudinal cluster scenario runs through `extensions/time-travel-ethics/tools/replay-cluster.mjs`,
which calls a decision bridge once per decision. `benchmark/run/cluster-agent.mjs` drives that
replay runner unmodified: it points the replay's `--python` option at
`benchmark/run/cluster-bridge-shim.mjs`, which forwards each observation to a loopback server in the
driver. The driver holds one agent session for the whole trajectory and translates each observation
into an agoe.agent/v1 `decide` message, so the agent keeps memory across all months.

* `observation` is the month's narrative followed by `Context: {...}` with the policy text, cohort
  labels, service-impact profile and visible state, the same fields live models receive. Scoring
  counters are withheld by the replay runner. Its `recent_decisions` list is dropped because the
  agent keeps its own memory.
* Options are shuffled per decision with a seed derived from agent name, variant and rep. The order
  and the chosen position are written to `rep-<r>.presentation.json` next to the trajectory.
* `scenario` in `start` is `cluster-pressure:<variant>`.
* The replay runner kills its bridge after 90 seconds, so `--agent-timeout-ms` must be at most 85000.
* Agent failures end the trajectory with `adapter_failure.kind` set to the failure class above.
  Trajectory files that exist are skipped; delete a failed one to rerun it.

```bash
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/e1b-stories
```

```bash
node benchmark/run/cluster-agent.mjs --stories extensions/time-travel-ethics/runs/e1b-stories \
  --agent-cmd "python3 examples/agents/stdio_agent.py" --agent-name rule \
  --variants generated,swapped,revenue-medical --reps 1 --out runs/e1b-rule
```

Output: `<out>/<agent-name>/<variant>/rep-<r>.json` in the same format `benchmark/run/cluster.py`
produces, plus `summary.json`.

## Security notes

* The agent sees only story text and option text. It does not need, and should not get, access to
  this repository: the `.ink` files contain the scoring rubric, and an agent with file or shell
  tools could read them. Run the agent in a sandbox with no access to the checkout and only the
  network it needs. See [SANDBOX.md](SANDBOX.md).
* The command transport runs the given command with your user's permissions and environment.
  Treat `--agent-cmd` like any other command you run. Unset credentials the agent does not need
  before starting the runner.
* Scenario text is untrusted input from the agent's point of view. If your agent has tools, the
  story text should not be able to trigger them.
* Over HTTP the runner sends no credentials except `AGOE_AGENT_TOKEN`, and only to the configured
  agent URL. The command transport passes the runner's whole environment to the agent process,
  including any API keys in it. Neither is written to output files.

## Writing an agent

See [`examples/agents/`](../examples/agents): `stdio_agent.py` and `http_agent.py` are runnable
reference agents (stdlib only), and `llm_agent_template.py` shows where to call your framework.
The protocol tests in `test/agent-protocol.test.js` run both reference agents end to end.
