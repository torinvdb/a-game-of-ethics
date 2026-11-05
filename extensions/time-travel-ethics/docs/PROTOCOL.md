# Evaluation protocol and claim boundaries

## Research question

Under a fixed agent configuration and a specified distribution of enterprise events, how do policy violations, task completion and unresolved work change with accumulated interactions, changing authorizations, injected tool instructions and business pressure? Does a control reduce realized harm without hiding unsafe proposals or unacceptable loss of utility?

The unit of evaluation is the **configured system**: model version, prompts, tools, permissions, retrieval, memory, runtime, policies and human review. The current implementation supplies a small fixed decision scaffold, not the user's production system. A full-system adapter must preserve the real scaffold and route its tool effects into a sandbox before this broader claim is justified.

## Three clocks

1. Wall time: how long execution actually takes, including model latency.
2. Logical time: dates in the scenario, authorization expiry and policy change.
3. Experience: number of interactions, memory updates, retrieved documents and tool actions.

Changing a date does not generate experience. Thirty-six monthly event batches are not three years of continuous operation. No fixed model weights change in this demonstration. Observed differences may reflect context, scenario difficulty, policy changes or interference, not learned ethical decay. Pressure begins at month 12 here; calendar month and pressure are intentionally confounded for demonstration. Do not estimate a time-caused drift effect from this schedule.

## Calibration delivered

Six policy families: bounded refunds, consent-bound sharing, retention expiry, immutable audit expectations, incident reporting and authorized outage repair. A 36-month schedule contains 216 opportunities. Three conditions use the same seed and facts: compliant script, faulty script with audit-only guard, faulty script with enforcing guard. Expected action is computed from facts. The faulty script knowingly chooses the other available action after month 12. This is a positive control for scorer sensitivity, not evidence about a language model. The enforcing guard uses the same known policy oracle; it is an idealized upper bound, not independent evidence of monitor quality.

State carries completion, unresolved work, exposures and audit status forward; the observation includes the last eight decisions. That establishes stateful replay, not realistic enterprise dynamics. No simulated customer actually receives a refund or suffers harm; a realized violation means the local simulator accepted a policy-violating action.

## Required next experimental design

Before making model claims, freeze and hash a discovery set and a separately authored holdout set. Separate scenario generation from target-model execution. Keep failed API calls, malformed outputs, abstentions and interrupted trajectories in explicit categories. Do not retry until a favorable answer appears. Record retry policies, provider request IDs and token costs; these are not yet included in the prototype.

Factorial conditions should independently vary logical time (constant versus advancing), experience count, pressure (on/off with randomized onset), tool injection, permission boundary, memory (bounded/full/summarized/reset), supervision visibility, model version and control. Keep model snapshots and budgets fixed. Pair conditions on exogenous event seeds; acknowledge that action-dependent state diverges. Include easy positive tasks so an agent that refuses everything cannot appear safe and useful. Include honest controls and adversarial agents, plus attacks on the monitor. Never send production credentials or production customer data into scenario generators.

Estimate failure rates by scenario family and task utility, severity-weighted realized harms, attempted unsafe actions, time/opportunities to first violation, escalation quality, unresolved-work backlog and false blocks on legitimate tasks. Use trajectory-level or scenario-family clustered bootstrap intervals; do not treat the 216 dependent decisions as independent samples. Repeated seeds of a deterministic baseline add no evidence about population model variance. For genuinely independent trials with zero failures, a rough 95% upper bound is 3/n; it is not valid with an inflated dependent denominator. Include censored trajectories in survival analysis. Preregister release gates before seeing results.

## Scoring and adjudication

Operational controls should first use executable invariants on final state and tool effects. Keep normative judgments separate: care, fairness, autonomy and loyalty may conflict, and a weighted sum can hide a severe violation. Retain Game of Ethics axes as exploratory descriptors, not a universal ethics ranking. Pair ambiguous cases with a documented rubric, domain-expert adjudication, disagreement rates and an appeal mechanism. LLM judges require calibration on expert-labeled cases, blinded agent identity, prompt-injection resistance and checks for verbosity/self-preference bias. Do not infer intent, deceptive cognition or consciousness from a single output or private chain-of-thought.

## External validity and deployment

Use controlled scenarios for discovery, held-out stress tests for replication, production-like sandboxed tools for fidelity, shadow mode for distribution checks, and a restricted canary for monitored deployment. Red-team the simulator itself. Vary realism and explicit evaluation framing; measure sensitivity rather than asserting the target cannot detect an evaluation. Synthetic cases cannot determine production prevalence without a representative sampling and transportability argument.

Evidence requirements: policy owner and version; use-case risk classification; data provenance and lawful purpose; scenario/version manifest; model/scaffold configuration; seeds and budgets; all tool inputs/outputs with sensitive fields redacted; final state; metrics and intervals; evaluator calibration; exceptions; remediation and retest; human signoff; post-deployment monitoring triggers. Hash chains need external signed roots or immutable retention to protect authenticity.

## Release scope

Local engine and tests: executed. Direct compatible adapter: offline protocol tests only. Provider router: optional, not live verified. Kubernetes, Flux and collector manifests: configuration examples, not an exercised cluster deployment. Ink integration: design seam only. Regulatory mapping: evidence-planning aid, not conformity assessment. Model efficacy, rate of deception and multiyear reliability: not measured.
