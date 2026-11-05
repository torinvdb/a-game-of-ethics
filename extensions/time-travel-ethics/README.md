# Time-Travel Ethics Lab

An additive extension of **A Game of Ethics** for controlled, stateful enterprise decision stress tests. Python 3.10+, standard library only for offline operation. The original CLI remains available. The cluster scenario path now generates and replays an Ink story using the existing Game of Ethics runtime; the earlier Python calibration is still separate.

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

Use LiteLLM's supported provider prefixes for Azure, Bedrock, Gemini, Ollama, vLLM and others. This is broad adapter coverage, **not verification of every provider**. No paid provider calls were made. Some models require different temperature/structured-output options; a rejected request is an adapter error, never a behavioral failure. For an existing full agent system, implement `decide()` to invoke its entire scaffold. The built-in live adapter tests a fixed decision scaffold, not arbitrary production agents.

## Method and deployment

Read `docs/PROTOCOL.md` before reporting results. Kubernetes, Flux and OpenTelemetry examples are in `deploy/`; local execution is the tested path. Deployment examples require building an image and selecting an isolated cluster. They never create permissions for the evaluated policy to access a production Kubernetes API. The [research and verification index](../../docs/agentic-ethics/README.md) and [presentation](../../talks/three-years-in-thirty-minutes/README.md) are included in this repository.

The log hash chain detects edits against a trusted external final hash. It is not signed or tamper-proof; an attacker able to replace the whole bundle can recompute it. Store a signed manifest or immutable external digest in production. Raw observations are synthetic here; enterprise deployments require redaction, retention controls and restricted access to logs.

## Session feedback

See `docs/ADK-FEEDBACK.md` for the offline ADK-session import and reviewed eval-case export. The delivered synthetic export validates against Google ADK 2.13.0. This does not train a model or execute a full ADK app.

## Branching cluster scenario

See [The Exception That Stayed](docs/CLUSTER-SCENARIO.md): allowlisted telemetry, reviewed impact cards, 36 logical monthly batches, persistent exceptions and debt, and matched demographic-label probes. The generated story is also selectable in the original manual CLI as Cluster Pressure.

## Optional DeepEval metrics

[DeepEval 4.3.3](docs/DEEPEVAL.md) evaluates the actual Ink trajectories with deterministic custom policy and completion metrics. It needs no judge model or cloud account. Operational outcomes and paired-label probes remain separate from these checks.

From the repository root, `npm run ethics:demo -- --output extensions/time-travel-ethics/runs/demo` builds and verifies the full cluster calibration with the bundled inkjs compiler.
