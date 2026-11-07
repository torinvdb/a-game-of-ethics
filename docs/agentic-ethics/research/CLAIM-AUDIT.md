# Claim audit: `talks/three-years-in-thirty-minutes/content.json`

Audited on 6 Nov 2026 against `RESEARCH-DOSSIER-V2.md`, `REGULATORY-MAP.md`,
`docs/agentic-ethics/VALIDATION.md` (recorded 5 Nov 2026) and the repository fixtures.

Since the audit, two findings below changed: the offline scaffold now has a
hash-chained ledger for mocked side effects (`ethicslab/scaffold.py`), and the
deployment manifests were built, run under Docker and applied to a real control
plane, though no pod ran on a node. Current status: [SYSTEM-REVIEW.md §7](../SYSTEM-REVIEW.md#7-gap-status-after-the-second-pass-2026-11-06).

## Classes

| Class | Meaning |
| --- | --- |
| **1. Published finding** | A third-party result, with its source |
| **2. Design intent** | The authors' recommendation or proposal; not tested |
| **3. Implemented** | The code or fixture exists in the repository; behaviour has not been shown by a recorded run |
| **4. Executed + verified** | A recorded run in VALIDATION.md or an evidence JSON file. It was *not re-run in this research pass* |

**UNSUPPORTED** marks a claim that needs rewording; suggested text follows the arrow (→).

## A. Known overclaims (must be fixed or kept explicitly bounded)

| # | Overclaim risk | Where | Ruling | Safe wording |
| --- | --- | --- | --- | --- |
| A1 | "Three years" read as three years of evidence | Title, `opening`, `consequences`, `clocks` | The run has **36 logical monthly batches** (class 4). That is not three operational years. The `clocks` slide already says "36 event batches ≠ three operational years"; keep that line and say it out loud in the opening. | "Thirty-six simulated months of decisions, executed in seconds. Not three years of field evidence." |
| A2 | The agent cannot tell the simulation from reality | Earlier abstract; not in the current content.json | **UNSUPPORTED and contradicted.** The Petri donation page says models "can often deduce … it's actually part of a test". In Agentic Misalignment, blackmail was 55.1% when the model stated the scenario was real and 6.5% when it stated it was an evaluation. The delivered prompt also discloses the simulation. | → "Realism is a variable we measure, not a property we assume." |
| A3 | Blackmail under constructed pressure read as prevalence | `research` | Class 1 (Anthropic, 2025). The slide's takeaway "possibility—not production prevalence" is correct. Do not show 96% without the setting: binary options, limited alternatives, 100 samples per condition, near-zero rates in controls, and no known real-world instances. | "In constructed no-good-option scenarios, many models sometimes chose harmful insider actions; controls were near zero." |
| A4 | Scripted policy change read as discovered drift or degradation | `consequences`, `demo`, `fairness` | The three "agents" are **deterministic scripted policies** (class 4). Their differences are put in by the authors. They are not observed model drift. The demo notes already say this; make it visible on the slide. | "Three scripted control policies, used to calibrate the instrument. No model was evaluated." |
| A5 | Passing the rubric read as being ethical or compliant | `score`, `gate`, `obligations` | **UNSUPPORTED** as universal ethics or legal compliance. The rubric checks authored policy invariants and completion (class 4). Ethical adequacy and legal applicability are outside its scope. | "Passing means the authored invariants held in these scenarios, not that the system is ethical or compliant." |
| A6 | Zero violations under the oracle guard read as monitor safety | Appendix / demo | The guard knows the correct action (class 3/4). SHADE-Arena shows real monitors trade recall against false positives (class 1). | "Oracle guard = upper bound; real monitors must be evaluated separately." |

## B. Slide-by-slide

| Slide / claim | Class | Source or note | Action |
| --- | --- | --- | --- |
| **opening**: names; "CNCF-Hosted Co-located Events North America 2026" | Event facts (S) | Co-located events are on 9 Nov 2026 at the Salt Palace, Salt Lake City (search-index). No session listing for this talk was found. | Replace the note "Event label follows the supplied deck" with "Mon 9 Nov 2026 · Salt Lake City". Confirm the room and time on the official schedule. |
| opening: "accelerated logical scenarios, not proof of three operational years" | 2 | — | Keep |
| **incident**: 2 failed fixes, 6 pending pods, CPU 24/20, unsigned release blocked | 3/4 | `examples/cluster-telemetry.synthetic.json` (failed_fix_attempts 2, pending_pods 6, allocatable_cpu 20) | Label it "synthetic fixture" on the slide, not just in the notes. |
| **people**: medical API vs education finance; "impact, urgency and alternatives — not age" | 2 (impact cards are 3) | Fixture impact profiles are authored assumptions | Keep. Add "authored impact assumptions". |
| **consequences**: bypass persists, exception expires, six credits run out | 3/4 | Ink scenario state; 35 exposure windows for delivery-at-all-costs (`evidence/cluster-calibration.json`) | Keep. "Exposure window ≠ exploit" stays in the notes. |
| consequences takeaway: "36 logical monthly batches" | 4 | VALIDATION: 36 capacity choices | Keep |
| **clocks**: wall, logical and experience clocks; "36 event batches ≠ three operational years" | 2 | METR horizon definition (class 1) | Keep. Strongest anti-overclaim line in the deck. |
| clocks note: METR horizons use human task time | 1 | METR eval-analysis-public README; METR 2025, arXiv:2503.14499 | Keep. Do **not** add a 2026 doubling or horizon figure (metr.org not verified). |
| **research**: "Anthropic: constructed conflicts can expose concerning behavior" | 1 | anthropic.com/research/agentic-misalignment, 20 Jun 2025 | Keep. Optionally add "16 models; controls near zero". |
| research: "AgentDojo: adversarial content through tools" | 1 | Debenedetti et al., NeurIPS 2024 D&B, arXiv:2406.13352 | Keep |
| research: "ControlArena: compare policy, monitoring and useful task completion" | 1 (tool capability) | UKGovernmentBEIS/control-arena, v20.1.1 | Keep |
| research note: "full-paper and current-law verification remain incomplete" | — | Still true for papers. Law: secondary sources only. | Keep, updated |
| **pattern**: "Allowlisted telemetry + domain impact cards → stateful scenario → evidence" | 3 for the synthetic export and Ink compile; 2 for live telemetry and domain review | Notes already state there is no live telemetry or generative authoring | The slide shows the future loop. Mark it "target loop; today: synthetic input". |
| pattern takeaway: "Prototype: a fixed decision scaffold. Full agent integration is next." | 3 | — | Keep |
| **demo**: 144/0/18-18; 179/107/84-0; 155/0/18-18 | 4 | VALIDATION.md table | Keep. "Scripted calibration" must stay visible. |
| demo note: "11 expiry reviews; final exception open (censored)" | 4 | VALIDATION.md | Keep |
| demo note: "Full demo output and provider interfaces are already implemented" | 3 | Provider adapters exist, but no real-model run was executed | → "Provider adapters exist; no real-model run has been executed." |
| **fairness**: identical choices after the swap; 36/36 change for the label-biased control | 4 | VALIDATION.md | Keep |
| fairness title: "Zero violations can still be unfair" | 2, illustrated by 4 | Calibrated on an injected bias | Keep, with the existing takeaway |
| **score**: "DeepEval checks policy + completion" | 4 | DeepEval 4.3.3 custom metrics executed (VALIDATION.md); 4.3.3 is current on PyPI (2026-11-04) | Keep. Say "custom deterministic metrics". |
| **feedback**: "Every session can become a test" | 2 for real sessions; 3/4 for the synthetic ADK export | Synthetic EvalSet validated under ADK 2.13.0; no ADK agent was executed | → "Every reviewed session can become a candidate test." |
| feedback takeaway: "Feedback is not automatic RLHF" | 2 | — | Keep |
| **stack**: Kubernetes Jobs, Flux, OTel | 3 (manifests exist); not executed | Notes: no rollout, reconciliation or collector receipt was executed | Keep the takeaway "cluster integration is unvalidated". Optionally cite agent-sandbox (SIG Apps) and inspect-k8s-sandbox as prior art. |
| stack: "OpenTelemetry: decision evidence" | 3 | OTel GenAI conventions are at **Development** status and moved to semantic-conventions-genai in v1.42.0 | Add "(GenAI semconv: Development)" if conventions are named. |
| **gate**: "Evidence supports approval. A score does not grant authority." | 2 | NIST AI RMF GOVERN; ISO 42001 | Keep |
| gate note: "current applicability and legal dates require primary verification" | — | Now partly resolved; see REGULATORY-MAP | Update: EU high-risk dates are Dec 2027 / Aug 2028 (Omnibus). Still "no compliance certification claimed". |
| **close** note: "attempted GitHub push was denied by repository authorization" | **Stale / incorrect** | The handoff says the branch was pushed and verified at 393c18b | → "Code: github.com/torinvdb/a-game-of-ethics, branch feat/ethics-v2." |
| close: "Increase autonomy as the evidence improves" | 2 | — | Keep |
| **verification** appendix: 35 tests; 7 Ink calibrations; ADK schema check; DeepEval | 4 | VALIDATION.md | Keep. Add "recorded 5 Nov 2026". |
| verification: 12 core/template scenarios pass the original validator | 4 | VALIDATION.md | Keep |
| **sources** appendix: "τ-bench" | 1 | The repository is now τ-bench 2.0; 2.0 scores are not comparable with 1.x | Cite a version, e.g. "τ²-bench (arXiv:2506.07982) / τ-bench 2.0". |
| sources: Petri link safety-research/petri | 1 | Now Meridian Labs inspect_petri v3 (donated 7 May 2026) | Update the URL to github.com/meridianlabs-ai/inspect_petri |
| sources: Bloom link safety-research/bloom | 1 | The repository is frozen; maintained as petri-bloom | Update the URL to meridianlabs-ai.github.io/petri_bloom |
| **obligations** appendix: NIST, EU AI Act and GDPR "not accessible … does not assert dates" | — | Secondary-verified dates are now available | Either keep it date-free, or use REGULATORY-MAP §5 wording with "(verify)". |
| obligations: NIST AI RMF and the EU AI Act listed side by side | — | Different instrument types | Label them "guidance" and "law" respectively. |

## C. Rewording list (minimum set)

1. "Three years" → "36 simulated monthly batches, executed in seconds; not field evidence."
2. Any realism or indistinguishability phrasing → "Realism is measured; models often detect tests."
3. Blackmail example → "constructed, no-good-option scenarios; not production prevalence."
4. Demo "agents" → "scripted control policies; no model evaluated; differences are injected, not discovered."
5. Rubric pass → "authored invariants held in these scenarios; not ethics or legal compliance."
6. Guard → "oracle upper bound; real monitors trade recall against false positives."
7. "Every session can become a test" → "every *reviewed* session can become a *candidate* test."
8. Provider interfaces "implemented" → "adapters exist; no real-model run executed."
9. Close note "push denied" → the actual repository and branch.
10. Event note → "Mon 9 Nov 2026, Salt Lake City" (confirm the slot).
11. Sources → pin τ-bench 2.0 / τ²; Petri → Meridian Labs v3; Bloom → petri-bloom.
12. Regulatory → "EU high-risk: 2 Dec 2027 (Annex III) / 2 Aug 2028 (Annex I) after Reg. 2026/1744; evidence ≠ compliance determination."

## D. Addendum: revised content.json (20 slides), re-scanned on 6 Nov 2026

`content.json` was rewritten by another workstream during this audit. Sections B and C
cover the earlier 17-slide version. The revised deck already fixes most of section C:

- the clocks line;
- "possibility, not prevalence";
- scripted controls stated as such;
- "No real-model inference has been run";
- "not a compliance determination";
- the stale push note is gone.

The remaining issues in the revised deck:

| Slide | Claim | Class | Action |
| --- | --- | --- | --- |
| opening (script) | "We can't wait three years to find out, so we compress the time." | 2 | Implies compression substitutes for time. → "...so we compress *logical* time, which tests sequencing, not three years of field exposure." |
| boundary | "Test the whole agent"; agent under test = "model · prompt · tools · permissions · memory" | 2 | The current adapters drive a finite-choice scaffold (REPOSITORY-ASSESSMENT). Mark it as the target design, e.g. subtitle "Target boundary; today's adapter drives a finite-choice scaffold". |
| boundary | "Tools are mocked; side effects go to a ledger, never to a real cluster" | 2 | No ledger implementation was found under `extensions/` or `src/` (grep, 6 Nov). → "Designed so that side effects go to a ledger", or implement it first. |
| stack | "An isolated Job per evaluation, with no egress and a read-only root filesystem"; Flux "reconciled"; "Decisions are emitted as traces" | 3 (manifests in `extensions/time-travel-ethics/deploy/`) | VALIDATION.md: Docker, Kubernetes, Flux and collector examples "were not built or deployed". Add "Manifests provided; not yet deployed or validated." The default NetworkPolicy allows collector and DNS egress, so say "no external egress", not "no egress". |
| stack | OpenTelemetry traces | 3 | If conventions are named: GenAI semconv status is Development (semantic-conventions-genai). |
| sources | "Alignment Faking (Greenblatt et al., 2024)" | 1 | The author list was not verifiable this session (arXiv blocked; the snapshot has no BibTeX). Verify on arXiv:2412.14093 or cite "Anthropic & Redwood Research (2024)". |
| sources | "LongMemEval (Wu et al., 2024)", "AgentDojo (Debenedetti et al., 2024)" | 1 | Verified against the repository BibTeX in `sources/` |
| sources | "τ²-bench (2025)" | 1 | OK. Optionally note "now τ-bench 2.0; scores not comparable with 1.x". |
| sources | Petri, Bloom | 1 | Cite the Meridian Labs maintained versions (inspect_petri v3; petri-bloom) |
| obligations | "check current application dates" | — | Optional: add "High-risk obligations now 2 Dec 2027 / 2 Aug 2028 (Reg. 2026/1744; verify)". |
