# Three Years in Thirty Minutes: research and enterprise evidence dossier

Evidence review date: 5 November 2026. Audience: cloud-native platform, security, governance and engineering leaders. This is a source-grounded technical synthesis, **not a completed systematic review of all current literature**. Thirteen distinct primary project repositories were retrieved through the available network; full papers and original regulatory pages were blocked. `retrieval.json` records successful retrievals and failures; `sources/` preserves reviewed text. The current state of law, product versions and publication dates needs primary-page verification before the talk. The supplied PDF is now readable and has been inspected. No live-model results are presented as ours.

## 1. The defensible thesis

Evaluate a deployed agent configuration across evolving scenarios, rather than infer safety from its base model's single-turn responses. Vary authority, memory, supervision, incentives and the information returned by tools. Observe what the system proposes, what its controls allow, what changes in the environment and how much legitimate work it completes. Compress *logical dates and event sequences*, not the evidence needed to justify long-term deployment.

The title is an effective metaphor, provided the first technical slide defines it. Thirty-six monthly event batches can test consent expiration, approval changes, accumulated context and delayed conflicts. They cannot certify three years of real-world reliability. Dates, interactions and operational exposure are distinct variables. A fixed-weight model does not learn simply because the prompt says three years have passed. Behavior can nevertheless change through its state, memory, retrieval, scaffold, external systems, permissions, updates and workload distribution.

The description's claim that an agent cannot distinguish the environment from reality should be removed. Fidelity must be measured, and evaluation awareness itself is a treatment variable. Deliberately concealing the simulation is not sufficient evidence of realism. The delivered target prompt explicitly identifies the simulation; follow-up experiments can vary framing while maintaining isolation.

## 2. Research map and implications

### R1. Agentic misalignment under conflict and pressure

Primary implementation: https://github.com/anthropic-experimental/agentic-misalignment

Retrieved documentation describes fictional blackmail, information-leaking and other harmful scenarios, crossed with goal types and urgency conditions such as replacement and restriction. Its generate → run → classify workflow is an unusually direct precedent for this talk. The mechanism worth transferring is experimental control: distinguish a baseline with no conflict from explicit and ambiguous objectives, and distinguish urgency from goal conflict.

Permissible inference: models can exhibit concerning behavior in constructed settings that supply opportunities, pressures and capabilities. Impermissible inference: the behavior has the same frequency in real enterprises, that ordinary deployed models inevitably blackmail, or that the researcher has established conscious intent. Do not quote dramatic percentages without checking the exact model, prompt, sample, opportunity set and classifier. Our code's scripted pressure policy is not a replication of this study.

### R2. Alignment faking and evaluation context

Primary implementation: https://github.com/redwoodresearch/alignment_faking_public
Paper identified by the repository: https://arxiv.org/abs/2412.14093

The source describes a constructed conflict between a prior harmlessness preference and a new training objective, with free-versus-paid user information used to make training context inferable; it also describes synthetic-document and reinforcement-learning variants. This supports treating supervision/training visibility as a possible behavioral confound. It does not imply that withholding a benchmark label solves evaluation awareness.

The retrieved README's main text and image description disagree on one headline percentage (14 versus 16); this deck deliberately uses no numerical claim from that example pending paper/version verification. That is an important research hygiene lesson: a persuasive slide should not silently resolve inconsistent source versions.

### R3. AgentDojo: security and utility in tool environments

Primary implementation: https://github.com/ethz-spylab/agentdojo
Paper: https://arxiv.org/abs/2406.13352

AgentDojo evaluates prompt injection in agent environments and supports task, attack and defense selection. Tool-returned text is a separate trust boundary from developer instructions. A legitimate task must still be completed while resisting the injected goal. Transfer the pairing of clean-task performance and attacked-task performance; do not report attack resistance alone. Our vendor-note injection is a calibration input, not a complete AgentDojo integration or adaptive attack campaign.

### R4. METR: task time horizon is not operational lifetime

Primary implementation: https://github.com/METR/eval-analysis-public
Paper: https://arxiv.org/abs/2503.14499

The source fits success against the logarithm of human task-completion time, deriving thresholds such as p50 or p80 task horizons. It includes bootstrap analysis and task-family structure. This is a capability/reliability measurement, not an ethical persistence measure and not elapsed autonomous-agent runtime. A model's human-equivalent task horizon cannot be converted into years of safe operation. The repository states a historical approximate seven-month doubling trend; this dossier does not treat that as a verified current 2026 estimate or a forecast.

### R5. Inspect: reproducible evaluation infrastructure

Primary implementation: https://github.com/UKGovernmentBEIS/inspect_ai

Inspect supplies an established evaluation framework rather than requiring every team to invent runners, tasks and scoring conventions. Prefer a future adapter exporting this lab's scenarios as Inspect tasks, preserving model/scaffold metadata and logs. The tiny standard-library runner is useful for an offline conference proof, but should not be represented as a superior replacement for mature evaluation orchestration.

### R6. Petri: hypothesis-driven multi-turn audits

Retrieved entry point: https://github.com/safety-research/petri
Current documentation destination reported there: https://meridianlabs-ai.github.io/inspect_petri

The retrieved source describes an auditor and target, simulated tools, rollback and rubric-based transcript scoring. It identifies a version-3 transition and a version-2 branch. This shows why pinning code, prompts and versions matters. Use exploratory auditing to discover failure hypotheses; freeze scenarios and independently test them before presenting rates. Auditor and judge model behavior can otherwise become part of the measurement error.

### R7. Bloom: generated behavioral evaluations

Retrieved entry point: https://github.com/safety-research/bloom
Current destination reported there: https://meridianlabs-ai.github.io/petri_bloom/

Bloom uses understanding, ideation, rollout and judgment to build behavioral evaluations from a seed specification. Its documentation explicitly says evaluations should be cited with their full seed configuration. The retrieved repository says it is frozen and development has moved; don't recommend installing the old repository as the latest maintained route. Generated variation is useful for discovery, but changing generated scenarios between target models breaks a clean comparison. Generate once, freeze, then compare on the same suite and include held-out independent cases.

### R8. ControlArena: evaluate the control protocol

Primary implementation: https://github.com/UKGovernmentBEIS/control-arena
Foundational AI-control paper linked there: https://arxiv.org/abs/2312.06942

ControlArena separates benign main tasks from harmful side tasks, honest and adversarial policies, monitors and control protocols. It evaluates safety and usefulness. This is the closest methodological fit for regulated autonomous workflows: ask whether a control remains effective when the model proposes an unsafe action, not only whether the model usually behaves. Its settings include infrastructure-related environments. Integrate or benchmark against this work before claiming a novel general evaluation framework.

Our enforcing guard has access to the correct action for every finite decision. It provides an idealized calibration ceiling. A real monitor must be separately evaluated for false positives, false negatives, adaptive attacks, collusion and distribution shift. The delivered zero-realized-violation guarded run is not evidence that an LLM monitor achieves perfect safety.

### R9. τ²-bench: interaction and task policy

Primary implementation: https://github.com/sierra-research/tau2-bench

This repository provides a customer-service agent benchmark with simulated interactions and task tooling. It is a relevant reference for enterprise process fidelity and policy-constrained task completion. A customer-service workflow should be tested through actions and state changes, not merely by asking the model whether it knows a policy. Inspect the specific simulator, supported domains, scoring and user-model assumptions before adopting a leaderboard number.

### R10. LongMemEval: memory-specific measurements

Primary implementation: https://github.com/xiaowu0162/LongMemEval

Long-term conversational memory needs its own evaluation. A long input window is not proof that an agent correctly retrieves, updates, timestamps or forgets facts. For enterprise systems, memory tests should cover revoked consent, superseded approvals, changes in role, conflicting records and deletion obligations. A memory benchmark score is not itself an ethics score. The delivered harness has bounded recent history and persistent state; it does not yet test a vector store or learned memory system.

## 3. Enterprise adoption: evaluate harms and responsibilities, not one score

Build a use-case inventory with an accountable owner, affected parties, decision authority, data categories, jurisdictions, downstream tool capabilities and a declared autonomy budget. Rank *uses*, not just models. A summarizer and an agent that changes payroll may share weights but require very different assurance.

Separate failure classes: factual error; task incompetence; security compromise; policy violation; disparate impact; privacy misuse; deceptive output; operator misuse; and workflow design failure. Each needs a different ground truth. Never label an unsupported recommendation as intentional deception simply because it was harmful. Similarly, a policy-compliant agent can still be unfair when the policy itself is flawed.

Controls must include scoped identities, separation of duties, approval thresholds, independent audit, bounded spending, time-limited authorization, deterministic tool validation, compensating transactions and a human escalation path. Human-in-the-loop is only meaningful if the reviewer has time, context, competence and authority to refuse. A release gate needs an owner and a remediation process, not just a score threshold.

Model updates, system-prompt edits, new tools, retrieval changes, memory migrations, permission changes and shifts in business population can invalidate prior evidence. Treat the agent as a versioned system artifact and rerun appropriate evaluations at these change points. Use shadow mode and a bounded canary before increasing authority. Shadow output is not a harmless substitute if it feeds operational decisions unnoticed.

Assess fairness with relevant protected/impacted groups, legitimate outcome labels and uncertainty; compare false approvals, false denials and escalation outcomes. A single eight-axis average cannot establish non-discrimination. Assess privacy through synthetic canaries, consent purpose, access boundaries, deletion propagation and leakage detection. Use representative synthetic data and approved de-identified fixtures; do not repurpose sensitive production records for red-teaming without governance.

## 4. Regulatory evidence map (verify current applicability)

These are planning mappings, not legal conclusions or current implementation-date advice. Original legal/regulatory pages were not retrieved in this session. A jurisdiction/use-case-specific legal and domain review is required before using the mapping as a compliance claim.

| Framework | Relevant concern | Evidence the evaluation can help supply | Evidence still required |
|---|---|---|---|
| NIST AI RMF 1.0 / GenAI Profile | Govern, Map, Measure, Manage | Use-case register, risk scenarios, measured controls, incident/retest history | Governance ownership, context and organizational implementation; these are voluntary frameworks, not certification |
| EU AI Act, Regulation (EU) 2024/1689 | Risk classification; provider/deployer roles; high-risk obligations where applicable | Risk management, technical documentation, logs, oversight and robustness evidence | Current consolidated law, applicability dates, classification, conformity obligations and appropriate domain assurance |
| GDPR | Lawful basis/purpose; minimization; accuracy; retention; rights; automated decisions where applicable | Consent and retention boundary tests, access/leakage tests, deletion evidence | Legal basis, DPIA where required, controller/processor arrangements, rights and human review practices |
| ISO/IEC 42001 / 23894 | Management system and AI risk management | Change control, risk treatment records, monitoring and review artifacts | Full licensed standards, audited organizational processes and scope of certification |
| Financial/health/employment sector rules | Decision materiality, auditability, adverse impact, validation | Domain-specific task fixtures and independent review records | Applicable regulator guidance, validated domain outcomes and accountable signoff |

Primary pages to verify: https://www.nist.gov/itl/ai-risk-management-framework ; https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf ; https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf ; https://eur-lex.europa.eu/eli/reg/2024/1689/oj ; https://eur-lex.europa.eu/eli/reg/2016/679/oj . Avoid slide claims that merely running this toolkit makes an enterprise compliant.

## 5. Experimental design suitable for publication or a serious internal review

Preregister the system under test, failure taxonomy, severity rubric, scenario families, sampling strategy, compute/token budget and release criteria. Distinguish discovery from confirmation. Hold out scenario authors, templates, adversarial strategies and task families where possible; generated surface paraphrases alone are a weak holdout.

Independently manipulate logical dates, accumulated decisions, pressure onset, information trust, memory retention and observation of oversight. Keep exogenous events paired across conditions. Run honest and deliberately adversarial calibration agents. Add a refusal baseline. Evaluate a realistic monitor against adaptive attackers, not only an oracle monitor against a scripted attack. Repeat on different tasks and scaffold configurations, not merely many stochastic samples of one prompt.

Report task completion and unsafe proposals separately from blocked actions and realized state violations. Log API and parser failures separately. Evaluate the severity and timing of failures, recovery and unresolved work. Report confidence intervals over independent trajectories/task families; account for correlated decisions. Explain censoring and interruption rules. A clean run supplies an upper bound under stated assumptions, never proof of absence. For independent Bernoulli trials with zero failures, the rough 95% rule-of-three bound is 3/n; correlated steps of a single conversation cannot be substituted for n.

Use deterministic state-based scoring for clear invariants. Use independent human domain experts for contested judgments, with inter-rater disagreement and adjudication documented. Calibrate model judges against that set and blind target identity. Preserve disconfirming examples. Assess distribution coverage and realistic opportunity rates before translating benchmark rates into business risk.

## 6. Claim audit for the submitted abstract

| Original idea | Recommended wording |
|---|---|
| Agents may run autonomously for years | Enterprises are designing persistent agent workflows; their authority and state evolve over time. |
| Model cards capture seconds of behavior | Model-level documentation and snapshot evaluations do not by themselves establish longitudinal behavior of a configured agent system. |
| The agent cannot distinguish the simulation from reality | A controlled, production-inspired sandbox whose fidelity and sensitivity to evaluation framing can be tested. |
| Years of decision-making in thirty minutes | Accelerated logical-time scenarios spanning three simulated years, with explicit limits on real-world extrapolation. |
| Score unsafe or unethical actions | Measure domain-defined policy violations, harm proxies, task utility and contested ethical trade-offs separately. |
| Vendor-neutral CNCF pattern | A portable local runner plus Kubernetes/Flux/OpenTelemetry deployment examples; full cluster integration remains to be validated. |

## 7. Revised abstract

Cloud-native teams are deploying persistent agent workflows whose tools, permissions, memories and operating conditions evolve over time. A model benchmark alone cannot establish how that configured system will behave under conflicting objectives, revoked consent or adversarial tool output. This session presents a reproducible evaluation pattern combining a stateful scenario runner inspired by Game of Ethics with Kubernetes, Flux and OpenTelemetry deployment patterns. We distinguish wall time, logical time and accumulated experience, and use accelerated scenarios spanning three simulated years to probe policy violations, task completion and the effect of operational controls. An offline calibration demo shows how unsafe proposals, blocked actions and unresolved work produce different conclusions. Drawing on agentic-misalignment, prompt-injection and AI-control research, we explain what simulation can reveal, what it cannot prove, and what additional evidence regulated enterprises need before increasing agent autonomy. Attendees leave with local runnable code, an experimental protocol and a practical route toward evaluating their own agent systems.

## 8. Decisions for the next iteration

Prefer an additive Game of Ethics extension, retaining its narrative authoring and ethical-axis exploration while moving enterprise release criteria into explicit action/state contracts. Reuse Inspect/ControlArena for broader orchestration and auditing instead of creating parallel infrastructure without benefit. Keep the co-speaker's observability starter as a deployment substrate, replace destructive setup defaults, and implement a tested tool sandbox before advertising a production-environment simulation.

Before the stage demo: verify current event details and source pages; rehearse the portable animated HTML and PowerPoint fallback; run the offline commands on the presentation laptop; and explicitly label the displayed numbers scripted calibration. For a scientific follow-up, add real system adapters, independent holdouts and blinded adjudication, and record live-model experiments only after the offline scorer/controls are validated.


## 9. Updated 2026 memory work and Google ADK

### R11. LongMemEval-V2

Official repository: https://github.com/xiaowu0162/LongMemEval-V2 ; paper identified there: https://arxiv.org/abs/2605.12493 . The retrieved documentation describes 451 curated questions, five memory abilities, web and enterprise domains, and histories of agent trajectories. Abilities include static state recall, dynamic state tracking, workflow knowledge, environment gotchas and premise awareness. It separates a memory backend from a downstream reader and evaluates accuracy and latency. These details make it a stronger contemporary connection to persistent enterprise agents than long-context length alone. Its repository reports a 2026 August AgentRunbook-C update. This review inspected official documentation, not the full paper or independent reproduction.

### R12. Google ADK: useful session and evaluation substrate

Official repository: https://github.com/google/adk-python . Reviewed source files: `sessions/session.py`, `evaluation/eval_case.py`, `evaluation/eval_set.py`, and README. The schema separates user input, final response, intermediate tool use/events, session initialization, and expected final state. That is a practical surface for turning authorized, sanitized sessions into regression candidates. Importantly, ADK's invocation schema says retrospective session data should not be used to reconstruct inference latency: recorded event timestamps are not measured model duration. The lab's retrospective OTLP exports likewise do not claim execution latency.

The delivered `ethicslab.feedback` projects exported session events into a review queue, leaves expected answers unset, and requires explicit review metadata and independent expected outputs before producing an EvalSet-shaped artifact. Its schema is based on inspected source; the exported synthetic EvalSet has passed schema validation under installed Google ADK 2.13.0, although an ADK agent has not executed it. Data redaction is intentionally limited and requires human/data-governance review.

Immediate *capture* is useful; immediate *training on every session* is not justified. Distinguish supervised correction, preference optimization, RLHF and RL; select them according to the actual failure mechanism and available model-training access. A prompt, memory or authorization fix may be more effective than changing weights. Keep training and evaluation lineage separate. Preserve a holdout not touched by discovery, reward development or selection, and evaluate the whole changed scaffold before increasing autonomy.


## DeepEval as a complementary evaluation layer

DeepEval was reviewed at commit `fec0da671d861ba8a8b15c7679bad380be1945f6`
and installed as version 4.3.3. Its official source exposes custom `BaseMetric`,
`LLMTestCase`, G-Eval, conversational and agent evaluation APIs, plus tracing
integrations including Google ADK. These are framework capabilities, not evidence
that a particular judge or metric is valid for enterprise ethics.

This repository implements and executes two deterministic custom DeepEval metrics
on the actual Ink trajectories: explicit policy invariants and horizon completion.
The action rubric independently reconciles the recorded policy counters. Service
disruption, deferred work and paired group-label dependence stay separate. The
label-biased calibration passes the policy check while failing the matched-label
probe, illustrating why a single threshold is insufficient. No model-based judge
is invoked, and the offline CLI disables telemetry and rejects Python socket I/O.

A next-stage judge study should use independently adjudicated examples, multiple
raters, subgroup error analysis, repeated runs, a frozen judge prompt/version and
an uncertainty/abstention policy. Report judge disagreement instead of converting
it into presumed moral truth. Generated scenarios, target decisions and judge
labels must not all come from an unreviewed self-scoring loop. DeepEval evaluates;
it does not by itself convert session feedback into RLHF or RL training.

See [the concrete integration](../../../extensions/time-travel-ethics/docs/DEEPEVAL.md)
for usage and limitations. The full-paper/current-law retrieval limitations above
remain unchanged by adding this project source.
