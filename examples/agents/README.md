# Example agents (agoe.agent/v1)

Agents that the benchmark runner can play scenarios against. Protocol reference:
[docs/AGENT-PROTOCOL.md](../../docs/AGENT-PROTOCOL.md).

| File | What it is |
| --- | --- |
| `rule_policy.py` | Trivial rule-based policy shared by the two reference agents. Prefers options that mention escalate, consult or report, and uses its memory of earlier choices in the run to break ties. It exists to exercise the protocol, not as a baseline worth reporting. |
| `stdio_agent.py` | The policy over stdin/stdout (command transport). |
| `http_agent.py` | The policy over HTTP with `http.server` (http transport). Serves `POST /start`, `/decide`, `/end` and `GET /health`. |
| `llm_agent_template.py` | Starting point for wrapping your own LLM agent. Replies `{"error": "not_configured"}` until you fill in `decide()`. |

All files use the Python standard library only. Run the commands below from the repository root.

## Run the stdio agent

```bash
node benchmark/run/run.mjs --agent-cmd "python3 examples/agents/stdio_agent.py" --agent-name rule-stdio \
  --stage smoke --scenarios hostage-holdout --out runs/rule-stdio
```

Add `--log-messages FILE` to the agent command to record every message it receives.

## Run the HTTP agent

```bash
python3 examples/agents/http_agent.py --host 127.0.0.1 --port 8080
```

In a second shell:

```bash
node benchmark/run/run.mjs --agent-url http://127.0.0.1:8080 --agent-name rule-http \
  --stage smoke --scenarios hostage-holdout --out runs/rule-http
```

If `AGOE_AGENT_TOKEN` is set for both processes, the agent requires it as a bearer token and the
runner sends it.

## Wrap your own agent

```bash
cp examples/agents/llm_agent_template.py my_agent.py
```

Fill in `on_start()` and `decide()`, then:

```bash
node benchmark/run/run.mjs --agent-cmd "python3 my_agent.py" --agent-name my-agent \
  --stage smoke --scenarios hostage-holdout --out runs/my-agent-smoke
```

Check the output against the schemas:

```bash
node schemas/validate.mjs schemas/results-row.schema.json runs/my-agent-smoke/results.jsonl
```

Points to get right:

* One JSON reply line per message on stdout; logs on stderr.
* Keep memory per run. The runner sends only new story text.
* Return the option `id` (a shuffled position), not the text.
* On any internal failure return `{"error": "<kind>"}`. Do not fall back to a default option.
* Run the agent where it cannot read this repository; the scenario files contain the rubric.
