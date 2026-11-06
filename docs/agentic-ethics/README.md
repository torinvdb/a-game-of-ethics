# Agentic ethics evaluation

The extension, research and talk now live in **A Game of Ethics**. The uploaded
`ai-ethic-eval` starter informed the infrastructure direction; a second repository
is not needed to run this proof.

## Start with the working proof

At the repository root, with Node.js 18+ and Python 3.10+:

```sh
npm ci
npm run ethics:test
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/demo
```

The demo compiles Ink with the compiler already included in the locked `inkjs`
dependency, then runs seven complete scripted trajectories and an intentionally
rejected adapter. It also verifies matched cohort-label probes. No model keys,
Kubernetes cluster or separate Inklecate installation are needed for this path.
Use a fresh output directory for each execution. The original interactive CLI
and original validator still use the repository's documented Inklecate setup.

- [Scenario, adapters and method](../../extensions/time-travel-ethics/README.md)
- [Optional offline DeepEval integration](../../extensions/time-travel-ethics/docs/DEEPEVAL.md)
- [Google ADK session-to-reviewed-eval workflow](../../extensions/time-travel-ethics/docs/ADK-FEEDBACK.md)
- [Kubernetes, Flux and OpenTelemetry examples](../../extensions/time-travel-ethics/deploy/README.md)
- [Research dossier](research/RESEARCH-DOSSIER.md), [repository assessment](research/REPOSITORY-ASSESSMENT.md)
- [30-minute talk and editable source](../../talks/three-years-in-thirty-minutes/README.md)
- [Verification and recorded calibration](VALIDATION.md)
- [System review and test campaign, 6 Nov 2026](SYSTEM-REVIEW.md): executed vs implemented vs design intent

## What the demo establishes

Earlier actions change later branches: a global bypass persists, exceptions
expire, capacity credits run out and backlogs accumulate. Explicit policy checks,
service impacts and demographic-label probes remain separate. The experiment
calibrates the instrument with deliberately scripted behaviors; it does not
measure spontaneous model degradation or prove years of safe operation.

## Remaining work for enterprise evidence

1. Connect a real model to the offline agent scaffold (`ethicslab/scaffold.py`:
   mocked tools, sandboxed ledger, guarded/unguarded permissions, frozen held-out
   cases), or wire an existing production scaffold to its tool interface. So far
   only deterministic scripted policies have been run.
2. Obtain reviewed, timestamped telemetry exports and service-impact cards.
   The current generator validates and renders an AI-authored fixture; it does
   not collect live cluster telemetry or invoke a generative authoring model.
3. Freeze independent scenario families and adjudication rubrics; run repeated
   live-model trials with controls and report uncertainty and censoring.
4. Run the Ink Job on a disposable cluster. The image build, a Job-equivalent
   container run with collector receipt, and offline schema validation were
   executed. Kubernetes apply, NetworkPolicy enforcement, RBAC and Flux were not.
5. Finish primary-paper and current legal-source verification. Network access
   allowed project repositories but blocked several research/regulatory sites.

No automatic training, cluster mutation, remote repository write or publication
is part of the offline commands above.
