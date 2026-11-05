# DeepEval integration: deterministic checks first

DeepEval is an optional evaluation library; Game of Ethics remains the stateful
scenario engine. This bridge uses actual `LLMTestCase` and `BaseMetric` APIs from
**DeepEval 4.3.3**. It invokes custom metrics directly, avoiding the cloud-aware
evaluation runner. No account, judge model, paid inference or training is needed.

From the repository root:

```sh
npm ci
python3 -m venv .venv-deepeval
.venv-deepeval/bin/pip install -r extensions/time-travel-ethics/requirements-deepeval.txt
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/demo \
  --deepeval-python "$PWD/.venv-deepeval/bin/python"
```

Dependency installation uses the network. The demo and evaluation then run
offline. Use a fresh output path each time. To evaluate one saved trajectory:

```sh
cd extensions/time-travel-ethics
../../.venv-deepeval/bin/python -m ethicslab.deepeval_bridge runs/demo/replays/delivery.json
```

Exit 0 means both implemented checks passed; 1 means at least one failed; 2
means malformed evidence or a missing optional dependency. The demo expects
policy failures from the deliberately bad calibration and completion failure
from the rejected adapter, so these expected results do not fail the demo.

| Signal | Implementation | Interpretation |
| --- | --- | --- |
| Explicit policy violations | Independently count the frozen action rubric; reconcile intermediate and final counters | Zero unauthorized bypasses, expired-exception continuations or misleading reports |
| Horizon completion | Check decision sequence, counters, final month and adapter status | Prevent an interrupted run from appearing to pass because it made no bad decisions |
| Operational outcomes | Preserve per-service disruption, backlogs, exposure and remaining credits | Descriptive fixture outcomes; no universal threshold or moral ranking |
| Demographic-label dependence | Paired replays checked by `check-cluster-replays.py` | Instrument calibration under fixed operational facts; requires plausibility review |

The label-biased calibration intentionally passes the two DeepEval metrics.
Its paired allocation choices nevertheless flip 36 times. A positive binary
check therefore cannot replace the outcome dashboard or domain adjudication.
These checks establish internal consistency, not log authenticity; retain
trusted external hashes and provenance for operational use. The closed action
rubric rejects new vocabulary until the rubric is explicitly updated.

The CLI sets telemetry opt-out, disables dotenv and legacy credential loading,
disables update checks and cloud trace flushing, and rejects Python socket
connections/DNS/sends using a process-wide audit hook before importing DeepEval.
Use a dedicated process. This is an accidental-network-use guard, not a native
code security sandbox. Importing `evaluate_run()` into an existing application
does not install the hook; use the documented CLI for the offline contract.

## Where model judges and Google ADK fit

DeepEval also offers G-Eval, conversational metrics and agent-trace evaluation.
Those are useful for nuanced rubric review after calibration against independent
human labels. They are **not implemented or executed by this offline bridge**.
Built-in judge metrics can make model calls; select the judge explicitly, record
its model/prompt/version, test agreement and subgroup error, cap cost, and keep
its result advisory for contested normative questions. A plausible explanation
cannot override a forbidden action.

ADK session exports feed the separate reviewed-case workflow in
[ADK-FEEDBACK.md](ADK-FEEDBACK.md). DeepEval can evaluate the resulting agent
behavior; ADK supplies the agent/session abstraction. Neither observing sessions
nor running metrics automatically provides RLHF or RL. Promote reviewed examples
to regression tests, fix prompts/tools/policies, and use a separate held-out suite
before any deployment. Training requires an additional, explicitly designed
optimization pipeline with reviewed labels or validated rewards.

The target model remains behind the existing compatible-endpoint/LiteLLM
adapter. Choosing DeepEval does not limit targets to one provider. Broad adapter
coverage is not a claim that every provider, local runtime or complete agent
scaffold has been tested.

Source reviewed: [DeepEval commit fec0da6](https://github.com/confident-ai/deepeval/tree/fec0da671d861ba8a8b15c7679bad380be1945f6),
including custom metrics, test cases, settings and telemetry implementation.
