# Time-Travel Ethics Lab

An extension of **A Game of Ethics** for controlled, stateful enterprise decision stress tests. Python 3.10+, standard library only for offline operation. The cluster scenario path generates and replays an Ink story with the same inkjs runtime as the core CLI; the generic Python calibration below is separate.

**What is proven:** the offline harness replays deterministic schedules, changes authorization/retention facts with logical time, persists state, detects known injected failures, applies an idealized policy guard, and exports auditable records. **What is not proven:** years of operational reliability, spontaneous model drift, an indistinguishable simulation, real-model deception, regulatory compliance, or production Kubernetes integration.

## Run locally

From this directory:

```sh
python3 -m unittest discover -s tests -v
python3 -m ethicslab --agent compliant --controls audit --output runs/compliant
python3 -m ethicslab --agent pressured --controls audit --output runs/pressure
python3 -m ethicslab --agent pressured --controls enforce --output runs/guarded
python3 -m ethicslab --verify runs/pressure/run.json --output unused
```

Each run contains 36 logical months × 6 decisions = 216 opportunities. No sleeping, artificial wall-clock acceleration, model training or external service mutation occurs. Seed controls the fact schedule. Context is the current event, policy, persistent state and last eight decisions. The scripted positive control flips decisions after month 12; this is **injected behavior**, not discovered degradation. The guard uses the known expected action, an idealized upper bound rather than a realistic monitor.

Outputs: `run.json` (observations, decisions, state, hash chain), `summary.json`, and OTLP/HTTP JSON traces. Existing output directories are rejected to prevent accidental overwrites. Invalid responses fail closed and are counted separately from behavioral violations; process exit 2 indicates invalid/API outcomes. Zero violations alongside unresolved work is not a success.

## Reproduce the 6 Nov 2026 review

From the repository root. Use a new output directory each time; existing directories are refused.

```sh
npm ci
npm run ethics:test                      # 142 tests; Ink replay tests skip if node_modules is absent
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/repro-001
python3 extensions/time-travel-ethics/tools/verify-evidence.py \
  extensions/time-travel-ethics/runs/repro-001 docs/agentic-ethics/evidence/manifest.json --inputs-root .
#   DeepEval outputs are listed in the manifest; without --deepeval-python they show as "missing".
python3 -m venv /tmp/de && /tmp/de/bin/pip install -r extensions/time-travel-ethics/requirements-deepeval.txt
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/repro-002 --deepeval-python /tmp/de/bin/python
python3 extensions/time-travel-ethics/tools/scaffold-eval.py --split all \
  --output extensions/time-travel-ethics/runs/scaffold-001
python3 extensions/time-travel-ethics/tools/export-otlp.py \
  extensions/time-travel-ethics/runs/repro-001/replays --output /tmp/traces.otlp.json
```

The container/Job path is in [deploy/README.md](deploy/README.md). The review findings, with
executed results kept apart from design intent, are in
[../../docs/agentic-ethics/SYSTEM-REVIEW.md](../../docs/agentic-ethics/SYSTEM-REVIEW.md).

### Failure classes

Every summary keeps these classes separate. None of them is ever folded into another.

- **Execution failures:** adapter or transport errors (`rate_limited`, `timeout`, `non_json`,
  `redirect_refused`, …), invalid or unoffered actions, parse and schema errors, retry
  exhaustion, step limits. They make a run incomplete or unresolved. They are not policy
  outcomes, and an incomplete Ink run is *not evaluable*.
- **Guard outcomes:** denials (allowlist, permission expiry or revocation, exception
  expiry, external effects).
- **Policy outcomes:** rubric violations that were executed (realized) and violations that
  were attempted (intent).
- **Useful work and burdens:** releases shipped through an authorized path, disruption,
  backlog.
- **Fairness probes:** paired label-swap runs. A run with zero violations can still flip
  every allocation.

## Offline agent scaffold (mocked tools)

`ethicslab/scaffold.py` drives any `model(observation) -> str` callable through parsed tool
calls, a permission gateway (`GUARDED` / `UNGUARDED`), mocked cluster tools and a hash-chained
ledger. Nothing leaves the process; `http_post` is recorded as "not sent". The scripted
policies in `ethicslab/scripted_models.py` are deterministic calibration controls, not
language models. Held-out cases in `cases/heldout/` are frozen by
`cases/heldout.FROZEN.json`, and the loader refuses to run them if they change. A changed set
needs a new name and a new freeze (`tools/freeze-heldout.py --force`, announced). Sessions
checkpoint and resume to an identical ledger. `verify_session(session, trusted_head)` detects
edits only against a head digest stored elsewhere.

## Providers and local models

Fully offline testing needs no keys. Direct OpenAI-compatible endpoints:

```sh
# Local example; requires a separately started local inference server.
python3 -m ethicslab --agent live --model YOUR_LOCAL_MODEL --endpoint http://127.0.0.1:11434/v1/chat/completions --months 1 --output runs/local
# Remote compatible endpoint: set ETHICS_API_KEY securely in your environment.
python3 -m ethicslab --agent live --model YOUR_MODEL --endpoint https://openrouter.ai/api/v1/chat/completions --months 1 --output runs/remote
```

Other provider protocols use the optional LiteLLM adapter:

```sh
python3 -m pip install -r requirements-live.txt
# Set provider-native variables (e.g. ANTHROPIC_API_KEY) through secure settings.
python3 -m ethicslab --agent live --model anthropic/YOUR_MODEL --months 1 --output runs/anthropic
```

The compatible-endpoint client (`ethicslab/provider.py`) refuses redirects, retries 429 and
5xx a bounded number of times (honouring `Retry-After` up to 30 s), classifies every failure,
and accepts either JSON content or a single `choose_action` tool call. These behaviours were
tested only against a local mock server.

Use LiteLLM's supported provider prefixes for Azure, Bedrock, Gemini, Ollama, vLLM and others. This is broad adapter coverage, **not verification of every provider**. No paid provider calls were made. Some models require different temperature/structured-output options; a rejected request is an adapter error, never a behavioral failure. For an existing full agent system, implement `decide()` to invoke its entire scaffold. The built-in live adapter tests a fixed decision scaffold, not arbitrary production agents.

## Method and deployment

Read `docs/PROTOCOL.md` before reporting results. Kubernetes, Flux and OpenTelemetry examples are in `deploy/`. The image and the Ink Job
script were executed under Docker with a real collector. The manifests were applied to a real control plane, but no pod has run on a node. Deployment examples require building an image and selecting an isolated cluster. They never create permissions for the evaluated policy to access a production Kubernetes API. The [research and verification index](../../docs/agentic-ethics/README.md) and [presentation](../../talks/three-years-in-thirty-minutes/README.md) are included in this repository.

The log hash chain detects edits against a trusted external final hash. On its own it is not tamper-proof: an attacker able to replace the whole bundle can recompute it. Sign the evidence manifest (`tools/sign-evidence.py`, see [deploy/README.md](deploy/README.md#signing-evidence)) or store an immutable external digest. Raw observations are synthetic here; enterprise deployments require redaction, retention controls and restricted access to logs.

## Session feedback

See `docs/ADK-FEEDBACK.md` for the offline ADK-session import and reviewed eval-case export. The delivered synthetic export validates against Google ADK 2.13.0. This does not train a model or execute a full ADK app.

## Branching cluster scenario

See [The Exception That Stayed](docs/CLUSTER-SCENARIO.md): allowlisted telemetry, reviewed impact cards, 36 logical monthly batches, persistent exceptions and debt, and matched demographic-label probes. The generated story is also selectable in the original manual CLI as Cluster Pressure.

## Optional DeepEval metrics

[DeepEval 4.3.3](docs/DEEPEVAL.md) evaluates the actual Ink trajectories with deterministic custom policy and completion metrics. It needs no judge model or cloud account. Operational outcomes and paired-label probes remain separate from these checks.
