# Repository assessment and integrated direction

## A Game of Ethics

The hackathon framework already provides Ink-authored branching dilemmas,
manual/model play, saved runs, eight authored ethical axes and descriptive
analysis. Those axes are design choices; neither syntax checks nor an aggregate
score establish normative validity, prevalence, temporal drift or compliance.

The extension now generates and replays an actual Ink cluster scenario. Persistent
state creates later recovery and expiry decisions, consumes capacity credits and
accumulates backlog. The original validator was updated to recognize reusable
`+` choices and distinguish ethical-axis updates from bookkeeping counters; it
also rejects a story with no choices. The root debug command now resolves to the
existing validator file. Original core/template scenarios retain their behavior.

The earlier standard-library Python calibration remains available separately:
six operational-policy families, expiry facts, persistent state, bounded history,
scripted controls, compatible-endpoint/LiteLLM adapters and retrospective OTLP
records. It is not the Ink experiment. Neither adapter currently executes an
arbitrary full production agent scaffold.

DeepEval is optional and evaluates Ink trajectories through actual custom metric
APIs. Policy checks, completion and descriptive burdens remain distinct. ADK
session exports can enter a review queue and become independently labeled EvalSet
cases. No immediate self-labeling, training or RL pipeline is implemented.

## Uploaded ai-ethic-eval starter

The uploaded files contain Minikube setup, Helmfile releases, Prometheus/Grafana
and exporter extras. Its README only contained a title. It had no agent evaluation
code, simulated-time mechanism, scenario runner, Flux resource or OTLP pipeline.
It hardcoded `starter-k8s`, deleted Minikube during startup, pinned older Kubernetes
and chart versions, and installed a demo from a moving `main` URL.

That starter is useful infrastructure context. The canonical implementation now
lives in A Game of Ethics, as requested. The new isolated deployment examples
live under `extensions/time-travel-ethics/deploy`; the old destructive startup and
hardcoded context are not imported into this repository. A previously packaged
standalone starter remains a separate handoff artifact, not a second source of
truth. Cluster compatibility has not been tested.

## Evidence boundary

Executed: offline unit tests, real Ink compiler/runtime replays, matched cohort
probes, live-adapter rejection, original validator regression checks, optional
DeepEval custom metrics, generic calibration and hash checks. A synthetic ADK
export passed `EvalSet` schema validation under ADK 2.13.0. The presentation has
browser and structural checks. See [validation](../VALIDATION.md).

Not executed: real-model inference, a full production-agent adapter, live
telemetry collection, live generative scenario authoring, Kubernetes rollout,
Flux reconciliation or end-to-end collector receipt. Research snapshots ground
the design but do not complete a systematic literature review or current legal
applicability assessment.

The next useful experiment is an actual agent scaffold with mocked tools and
independent held-out cases, followed by deployment validation and domain review.
