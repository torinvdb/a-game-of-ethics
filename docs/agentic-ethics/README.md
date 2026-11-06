# Agentic ethics evaluation

The time-travel extension, its research notes and the KubeCon talk live in this repository. The `ai-ethic-eval` starter informed the infrastructure direction; no second repository is needed.

## Start with the working proof

At the repository root, with Node.js ≥ 22.13 and Python 3.10+:

```sh
npm ci
npm run ethics:test
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/demo
```

`ethics:test` runs 142 tests. The demo compiles Ink with the compiler included in the locked `inkjs` dependency, runs seven complete scripted trajectories and an intentionally rejected adapter, and checks matched cohort-label probes. No model keys, Kubernetes cluster or separate Ink compiler are needed. Use a fresh output directory for each run. The core CLI and its validator (`src/debug.js`) also compile with inkjs.

- [Scenario, adapters and method](../../extensions/time-travel-ethics/README.md)
- [Optional offline DeepEval integration](../../extensions/time-travel-ethics/docs/DEEPEVAL.md)
- [Google ADK session-to-reviewed-eval workflow](../../extensions/time-travel-ethics/docs/ADK-FEEDBACK.md)
- [Kubernetes, Flux and OpenTelemetry examples](../../extensions/time-travel-ethics/deploy/README.md)
- [Research dossier](research/RESEARCH-DOSSIER.md), [repository assessment](research/REPOSITORY-ASSESSMENT.md)
- [30-minute talk and editable source](../../talks/three-years-in-thirty-minutes/README.md)
- [Verification and recorded calibration](VALIDATION.md)
- [System review and test campaign, 6 Nov 2026](SYSTEM-REVIEW.md): executed vs implemented vs design intent; gap status in [§7](SYSTEM-REVIEW.md#7-gap-status-after-the-second-pass-2026-11-06)

## What the demo establishes

Earlier actions change later branches: a global bypass persists, exceptions expire, capacity credits run out and backlogs accumulate. Explicit policy checks, service impacts and demographic-label probes are reported separately. The experiment calibrates the instrument with deliberately scripted behaviors. It does not measure spontaneous model degradation or show years of safe operation.

## Remaining work for enterprise evidence

Status as of the second pass ([SYSTEM-REVIEW.md §7](SYSTEM-REVIEW.md#7-gap-status-after-the-second-pass-2026-11-06)):

1. Connect a real model to the offline agent scaffold (`ethicslab/scaffold.py`) or wire an existing production scaffold to its tool interface. Only deterministic scripted policies have been run; model weights and paid APIs were unavailable here.
2. Obtain reviewed, timestamped telemetry exports and service-impact cards. The current generator validates and renders an AI-authored fixture; it does not collect live cluster telemetry or invoke a generative authoring model.
3. Freeze independent scenario families and adjudication rubrics; run repeated live-model trials with controls and report uncertainty and censoring.
4. Run the Ink Job on a node. Manifests were applied to a real control plane (etcd, kube-apiserver, controller-manager v1.32.13): server-side apply, PodSecurity admission, RBAC and NetworkPolicy selectors were checked. Pods on a node, NetworkPolicy enforcement, PVC writes and Flux were not exercised.
5. Replace the keyword-based report check with a stronger content check; red-team case rt-09 is not yet exercised.
6. Finish primary-paper and current legal-source verification. Several research and regulatory sites were unreachable.

No automatic training, cluster mutation, remote repository write or publication is part of the offline commands above.
