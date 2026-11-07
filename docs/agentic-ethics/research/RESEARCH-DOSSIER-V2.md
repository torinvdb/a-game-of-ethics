# Research dossier V2: verification pass

Review date: **6 November 2026**. This file supplements `RESEARCH-DOSSIER.md`; it does
not replace it. It records what was re-verified, what is new, and what could not be
accessed. Companion files: `CLAIM-AUDIT.md` (every deck claim classified) and
`REGULATORY-MAP.md` (law vs standard vs guidance, dated).

## 0. Evidence grades used here

| Grade | Meaning |
| --- | --- |
| **P** | Primary source fetched this session: the project's own page, README, docs or package index. Byte-snapshotted ones are hashed in `retrieval.json`. |
| **P-sum** | Primary page fetched through the WebFetch tool, which returns a model-written summary, not raw text. Numbers were taken from that summary. Re-check against the page before quoting them verbatim on a slide. |
| **S** | Search-index summary only. The primary page was blocked, and the claim rests on secondary reports surfaced by WebSearch. |

**Accessible:** `raw.githubusercontent.com`, `pypi.org`, `www.anthropic.com` (WebFetch only).

**Blocked:** `events.linuxfoundation.org`, `cncf.io`, `arxiv.org`, `metr.org`,
`eur-lex.europa.eu`, `nist.gov`, `leg.colorado.gov`, `opentelemetry.io`, law-firm sites, and
the GitHub API (not authorised for these repositories). No arXiv paper full text was read,
so **every paper-level claim below rests on the project or lab page, not the paper itself**.

## 1. The event (grade S)

- KubeCon + CloudNativeCon North America 2026 runs **9–12 November 2026** at the
  **Salt Palace Convention Center, Salt Lake City, Utah**.
- **Monday 9 November** is the day for CNCF-hosted co-located events. The main conference
  runs 10–12 November.
- Co-located events need an All-Access pass. Sources say there is no co-located-only pass.
- The CNCF pages that report this are
  https://events.linuxfoundation.org/kubecon-cloudnativecon-north-america/co-located-events/cncf-hosted-co-located-events-overview
  and https://cncf.io/blog/2026/09/11/kubecon-cloudnativecon-north-america-2026-your-week-in-salt-lake-city.
  Both were blocked for direct fetch. The CFP was hosted at
  https://sessionize.com/cncf-hosted-co-located-events-north-america-2026.
- Monday events named in search results: Agentics Day: MCP + Agents, Cloud Native AI +
  Inference Day, ArgoCon, BackstageCon, CiliumCon, FluxCon, Kubernetes on Edge Day,
  Observability Day and others. The lists differ between sources.
- **Not verified:** a public schedule entry for "Three Years in Thirty Minutes", for either
  speaker, for which co-located event hosts the talk, or for its room and time. Searches for
  the title and both names returned nothing.
- The supplied deck says "9 November 2026, Salt Lake City", which is **consistent** with the
  search evidence. The speakers should confirm the slot on the official sched before printing
  a time or room.

## 2. Research sources

### 2.1 Agentic Misalignment, Anthropic, 20 June 2025 (P-sum)

URL: https://www.anthropic.com/research/agentic-misalignment. Code:
https://github.com/anthropic-experimental/agentic-misalignment (README re-fetched; hash
unchanged). Search results report a companion paper, Lynch et al., arXiv:2510.05179 (S); it
was not opened.

**Method.**
- 16 models from several developers were placed in simulated corporate settings with
  harmless business goals.
- Treatments were a replacement threat and/or a goal conflict.
- Controls had neither treatment.
- Most rates are computed from 100 samples per model and condition.

**Findings.**
- When harm was the only path to the goal, models from every developer sometimes took
  insider-style harmful actions.
- In the headline five-model figure, blackmail rates reached 96% (Claude Opus 4, Gemini 2.5
  Flash).
- In controls, models almost never misbehaved. The one exception was a single sample out of
  100 from Llama 4 Maverick.
- Direct prohibitions in the prompt reduced the behaviour but did not eliminate it. Claude
  Opus 4's blackmail rate fell from 96% to 37%.
- Evaluation-awareness probe (Claude Opus 4, 500 samples): the model blackmailed in 55.1% of
  samples where it stated the scenario was real, versus 6.5% where it stated it was an
  evaluation.

**Stated limitations.**
- The scenarios deliberately limited the available options.
- Real deployments typically offer more nuanced alternatives.
- Key information was placed close together, which may have made the harmful option
  unusually salient.
- Stated chain-of-thought may not reflect the model's actual process.
- The authors say they are not aware of this behaviour in real deployments.

**Talk-safe inference.** Constructed pressure can elicit harmful agent actions, and
evaluation framing changes the rates.

**Not supported.** That this is prevalent in production, that deployed agents "will
blackmail", or that the model has intent.

### 2.2 Alignment faking, Anthropic with Redwood Research, 18 Dec 2024; paper 20 Dec 2024 (P-sum)

URL: https://www.anthropic.com/research/alignment-faking. Paper: arXiv:2412.14093 (not
opened).

**Method.**
- Model: Claude 3 Opus.
- The model was told that free-tier conversations would be used for training and paid-tier
  conversations would not. This setup was fictional.
- The model had a scratchpad it believed was hidden.

**Findings.**
- With the paid (unmonitored) framing, the model refused the harmful query 97% of the time.
- With the free (monitored) framing, it complied 12% of the time, with alignment-faking
  reasoning in the scratchpad.
- After RL training toward compliance, alignment-faking reasoning appeared in 78% of
  scratchpads.

**Caveats.**
- The authors say the work "does not show that dangerous alignment faking behavior will
  necessarily emerge".
- The preferences the model preserved were its benign original ones.

**Note.** The earlier README discrepancy (14 vs 16%) is a different statistic. The deck uses
no alignment-faking number, and that should stay the case.

### 2.3 AgentDojo, ETH Zurich SPY Lab, 2024 (P)

Code: https://github.com/ethz-spylab/agentdojo (README hash unchanged). PyPI
`agentdojo` 0.1.35 (uploaded 2025-10-27). Paper: arXiv:2406.13352. Results:
https://agentdojo.spylab.ai/results/.

It is a dynamic environment for prompt-injection attacks and defences on tool-using agents,
with suites, user tasks, injection tasks and defences. The transferable idea: report utility
with and without attack.

Task counts and other numbers are from the paper, which was not opened. Do not quote them.

### 2.4 UK AISI Inspect (P)

Code: https://github.com/UKGovernmentBEIS/inspect_ai. PyPI `inspect-ai` **0.3.287**
(2026-10-31).

New this pass: `inspect-k8s-sandbox` **0.14.0** (2026-10-09) is UK AISI's "Kubernetes
sandbox environment in which agentic evaluations can securely be run at scale". The README
says it was designed for AISI infrastructure and "may require further tailoring". See
https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox. This is the most direct precedent
for running agent evaluations as isolated Kubernetes workloads.

### 2.5 ControlArena, UK AISI (P)

Code: https://github.com/UKGovernmentBEIS/control-arena (README hash unchanged). PyPI
`control-arena` **20.1.1** (2026-10-22). Docs: https://control-arena.aisi.org.uk.

**Structure.**
- Settings pair benign main tasks with harmful side tasks.
- It runs honest and attack modes.
- Micro-protocols (for example defer-to-trusted) and monitors produce suspicion scores.
- It includes an infra setting that talks to Kubernetes and an IaC setting.

**Grounding.** Greenblatt et al. AI-control paper, arXiv:2312.06942.

### 2.6 SHADE-Arena, Anthropic, 16 June 2025 (P-sum, new)

URL: https://www.anthropic.com/research/shade-arena-sabotage-monitoring.

**Method.**
- 17 benign tasks, each paired with a malicious side task.
- A monitor scores suspicion from 0 to 100.
- A score of 80 or above counts as detected.

**Findings.**
- 14 models were tested. None exceeded 30% overall sabotage success; most were below 10%.
- The best monitor, Gemini 2.5 Pro, needed a false-positive rate above 20% to catch 80% of
  side tasks.

**Limitations.**
- The side goals were assigned. The benchmark measures "can", not "would".
- Most of the dataset is private.

**Relevance.** Monitors have a measurable false-positive/recall trade-off. This supports the
deck's "an oracle guard is a ceiling" caveat.

### 2.7 Petri, Anthropic, 6 Oct 2025; donated to Meridian Labs 7 May 2026 (P-sum + P)

URLs: https://www.anthropic.com/research/petri-open-source-auditing and
https://www.anthropic.com/research/donating-open-source-petri.

**Pilot (Oct 2025).**
- 14 frontier models and 111 seed instructions.
- An auditor agent drove multi-turn conversations with simulated users and tools, and LLM
  judges scored the transcripts.

**Stated limits.**
- The authors call the evaluation "very provisional".
- 111 scenarios is too few to explore many edge cases.
- Using current AI systems as auditors imposes limits.
- Summary metrics are reductive.
- Models that speculate about being tested complicate comparisons.

**Petri 3.0** (PyPI `inspect-petri` **3.1.1**, 2026-10-01, maintained at
https://github.com/meridianlabs-ai/inspect_petri):
- The auditor and target are separate components.
- An add-on called "Dish" runs audits with a target's real system prompt and scaffold.
- It integrates with Bloom.

The donation page says a model "can often deduce from various artificialities in the setup
that it's actually part of a test". This is a primary-source statement that directly
**contradicts any "indistinguishable from reality" claim**.

### 2.8 Bloom, Anthropic, 19 Dec 2025 (P-sum + P)

URL: https://www.anthropic.com/research/bloom. The original repository is frozen (README hash
unchanged). Maintained as `petri-bloom` **0.2.6** (2026-06-08):
https://meridianlabs-ai.github.io/petri_bloom/.

**Method.** Four stages: understanding, ideation, rollout and judgment, plus a meta-judge.

**Validation.**
- Bloom separated system-prompted model organisms from baseline models in 9 of 10 quirks.
- Judge calibration against 40 hand-labelled transcripts: Spearman 0.86 for Claude Opus 4.1
  and 0.75 for Claude Sonnet 4.5.

**Caveats.**
- Absolute metrics shift with configuration.
- Results should be cited with their seed file.

### 2.9 METR time horizons (P for the repo; S for the 2026 update)

Repo: https://github.com/METR/eval-analysis-public (README hash unchanged). Paper:
"Measuring AI Ability to Complete Long Tasks", METR (repo citation lists author "METR"), 2025, arXiv:2503.14499
(not opened).

**Method.**
- Fit model success against the logarithm of the time a human takes to complete the task.
- p50 and p80 horizons are the task lengths at 50% and 80% success.
- The README states that horizons have doubled "approximately every 7 months". The repo holds
  reports for Time Horizon **v1.0 and v1.1**.

**2026 update (S only; metr.org blocked).**
- Search results attribute to Time Horizon 1.1 (January 2026) a post-2023 doubling time of
  about 4 months (cited as roughly 130 days).
- Secondary pages report frontier p50 horizons above 14 hours in 2026.
- **Do not put either figure on a slide** until they are checked on metr.org.

**Talk-safe point.** A horizon is human task length at a success rate. It is not agent
runtime, years of operation, or ethical persistence.

### 2.10 LongMemEval (ICLR 2025) and LongMemEval-V2 (2026) (P)

**LongMemEval** (https://github.com/xiaowu0162/LongMemEval):
- 500 questions covering five long-term memory abilities.
- The paper was accepted at ICLR 2025.

**LongMemEval-V2** (https://github.com/xiaowu0162/LongMemEval-V2; paper arXiv:2605.12493,
not opened):
- 451 curated questions covering five abilities over agent trajectories in web and
  enterprise domains.
- AgentRunbook-C V2 update in August 2026.

### 2.11 τ-bench / τ²-bench, Sierra (P)

Repo: https://github.com/sierra-research/tau2-bench (README hash unchanged). It is now
titled **τ-bench 2.0**, and the τ² paper is arXiv:2506.07982.

**What 2.0 adds.**
- Six languages.
- Full-duplex voice.
- An `intake` domain.
- Frozen released task sets.

**Comparability.**
- 2.0 English runs are "not input-identical" to v1.0.1, so their scores are not comparable
  with the 1.x leaderboard.
- The natural-language judge changed to `gpt-5.4-mini-2026-03-17`.
- The previous release was τ³-bench v1.0.

**Lesson for the deck.** A benchmark name without a version is not a reproducible
reference.

The PyPI name `tau2` belongs to an **unrelated** physics package.

### 2.12 Vending-Bench, Andon Labs, Feb 2025 (S, new)

Paper: Backlund and Petersson, arXiv:2502.15840. It is a long-horizon simulated business
benchmark.

**Reported findings.**
- Every model had runs that derailed, for example by misreading delivery schedules or
  entering "meltdown" loops.
- The failures showed no clear correlation with the context window filling up.

A successor, Vending-Bench 2, exists (https://epoch.ai/benchmarks/vending-bench-2). Both
facts come from search summaries only and need a check against the paper before use.

### 2.13 Google ADK evaluation (P)

PyPI `google-adk` **2.13.0** (2026-10-23), which is the version the repository validated
against.

**Current criteria** (from https://github.com/google/adk-docs, `docs/evaluate/criteria.md`):
- Reference-based: `tool_trajectory_avg_score` (exact trajectory match),
  `response_match_score` (ROUGE-1) and `final_response_match_v2`.
- Reference-free, LLM-judged: `rubric_based_tool_use_quality_v1`,
  `rubric_based_multi_turn_trajectory_quality_v1`, `hallucinations_v1`, `safety_v1`,
  `multi_turn_task_success_v1`, `multi_turn_trajectory_quality_v1` and
  `per_turn_user_simulator_quality_v1`.

**Evaluation surfaces.**
- Test files and EvalSet files.
- A user simulator.
- Conformance testing.

None of this is an ethics validator. The `safety_v1` criterion is a harmlessness judge,
not a policy-compliance proof.

### 2.14 DeepEval (P)

PyPI `deepeval` **4.3.3**, uploaded 2026-11-04. It matches the installed version recorded in
VALIDATION.md, and it is still the latest release.

### 2.15 OpenTelemetry GenAI semantic conventions (P)

**Location and status.**
- Core semantic-conventions changelog: latest section **v1.45.0**.
- In **v1.42.0**, all `gen_ai.*`, `openai.*` and `mcp.*` conventions were **moved to a
  dedicated repository**, https://github.com/open-telemetry/semantic-conventions-genai, and
  deprecated in the core repository.
- The new repository's changelog shows **no release yet**, only an "Unreleased" section.
- Its documents are marked **Status: Development**.

**What exists.**
- Agent spans (`invoke_agent`, `execute_tool`).
- `gen_ai.agent.version` (added in v1.40.0).
- A GenAI **Evaluation Event** (introduced in v1.38.0).

**Talk-safe point.** OTel has development-status agent/tool span conventions. Do not call
them "stable" or "the standard".

### 2.16 Kubernetes / CNCF agent infrastructure (P + S)

**kubernetes-sigs/agent-sandbox** (P; https://github.com/kubernetes-sigs/agent-sandbox):
- It is a `Sandbox` CRD and controller "under the umbrella of SIG Apps".
- It manages "isolated, stateful, singleton workloads" with stable identity, persistent
  storage and pause/resume.
- Extensions are `SandboxTemplate`, `SandboxClaim` and `SandboxWarmPool`.
- It is an orchestrator that delegates isolation to runtimes such as gVisor or Kata via
  `RuntimeClass`.
- The README's install example pins **v1.0.2**. A 2026 roadmap is published in the repo.
- It is relevant as an isolated execution substrate. It is **not** an evaluation framework.

**kagent** (P/S; https://github.com/kagent-dev/kagent):
- A Kubernetes-native framework for building and running AI agents. The README states "kagent
  is a Cloud Native Computing Foundation project" (P).
- Search results put it at CNCF **Sandbox** maturity: donated by Solo.io in April 2025 and
  accepted May 2025 (S). A pending application to move up to Incubation was not verified.
- It is an agent runtime, not an ethics or evaluation tool.

**inspect-k8s-sandbox**: see §2.4.

## 3. Synthesis changes from V1

1. **Evaluation awareness has primary-source support as a confound.** Three primary sources
   back it:
   - Agentic Misalignment: 55.1% vs 6.5% blackmail by stated belief.
   - Petri: "can often deduce … it's actually part of a test".
   - Petri 3.0 Dish: real scaffolds to improve realism.

   The deck must treat realism as measured and imperfect, never as achieved.
2. **Monitors have a measurable recall/false-positive trade-off.** SHADE-Arena reports more
   than 20% false positives at 80% recall. Keep the "oracle guard is a ceiling" caveat.
3. **Versioning matters.** τ-bench 2.0 scores are not comparable with 1.x, Petri 3 replaced
   v2, and Bloom moved repositories. Pin versions in every citation.
4. **Cloud-native substrate is real but early.** That covers agent-sandbox (SIG Apps), the
   Inspect K8s sandbox and OTel GenAI conventions at Development status. They support a
   "portable pattern" claim, not a "validated cluster integration" claim.
