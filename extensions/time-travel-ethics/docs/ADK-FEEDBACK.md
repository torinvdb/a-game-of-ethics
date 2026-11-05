# Agent sessions as feedback: ADK, evaluations and learning

Google ADK is a useful optional agent/session framework; the lab should retain a provider-neutral event contract so users of other scaffolds can participate. ADK supplies session events and evaluation schemas, not automatic RL training of every supported model. This adapter was developed against the retrieved `google/adk-python` Session, Invocation, EvalCase and EvalSet schemas. It is a narrow offline JSON bridge; The synthetic exported case passed EvalSet.model_validate_json under installed google-adk 2.13.0. Full ADK runtime agent execution remains outstanding.

## Working offline path

```sh
python -m ethicslab.feedback collect examples/adk-session.synthetic.json /tmp/feedback-candidates.json
```

Every user turn becomes a candidate, with observed agent/tool events preserved separately from any expected answer. Partial streaming events are ignored. Source session IDs are hashed; a minimal sanitizer masks obvious secret-key fields and email patterns. **This is not a complete PII detector**: names, addresses, medical/financial data, secrets embedded in prose and artifact links require data review. Tool responses may contain attacker instructions; treat them as evidence, never instructions to the reviewer/judge. Do not auto-ingest production sessions into a training corpus.

For selected candidates, a reviewer supplies `expected_response` and/or `expected_tool_uses`, then records `review = {"approved": true, "reviewer": "...", "rationale": "...", "data_cleared": true}`. This is an auditable attestation, not an authentication or access-control mechanism. Store review actions through authenticated services in a real deployment.

```sh
python -m ethicslab.feedback promote /tmp/reviewed-candidates.json /tmp/adk.evalset.json --app-name ethics_agent
```

The resulting file uses ADK EvalSet/Invocation field names. Configure ADK evaluation criteria appropriate to the reference: tool trajectory checks and outcome assertions are different from response similarity. Do not assume every valid tool path must match a single recorded ordering. The export does not reconstruct original state deltas, artifacts, multimodal binaries or full session timing; supply sanitized initial state and artifacts when needed before treating it as a faithful replay. Existing full ADK apps can be evaluated through their own `adk eval` workflow after validating the file against the pinned ADK version.

## Feedback is not a training algorithm

1. **Observability:** immediately collect a minimal session record and explicit feedback provenance.
2. **Triage:** identify incidents, unclear cases, repeated failures and sampling gaps. User thumbs-up is satisfaction, not verified correctness or safety.
3. **Evaluation:** promote independently reviewed cases to the regression set; keep discovery, training and untouched holdout sets disjoint by lineage and scenario family.
4. **Improvement:** first consider tool validation, permissions, memory policy, prompts and workflow design. These often fix the causal problem more directly than a weight update.
5. **Learning, when justified:** supervised fine-tuning uses corrected demonstrations; preference optimization uses reviewed preference pairs; RLHF typically learns a reward signal from human preferences and optimizes a policy; RL requires an appropriate reward/environment and an optimizer. Many hosted model APIs do not permit the required updates. Local/open-weight training has separate compute, governance and reproducibility requirements.
6. **Release:** evaluate the candidate system against frozen independent holdouts, utility and safety constraints; compare to the prior version; obtain the accountable owner's signoff; deploy a bounded canary with rollback.

The same model should not generate its own tasks, label its own successes, train on them, and then report improvement on those same tasks. Reward hacking and judge exploitation become especially plausible when a reward is a single aggregate ethical score. Keep hard authorization constraints outside the optimized reward. Do not use this tiny synthetic fixture as a training corpus: it would teach a narrow lookup policy, not general ethical competence.

## What to show on stage

Start from the deliberately bad synthetic refund answer. Collect it into a review queue. Show that the observed bad answer is **not** the expected answer. Add a reviewed correction, export one eval case, and show that the independent holdout gate remains separate. This is a fully offline session-to-feedback proof. No RL, fine-tuning, ADK agent execution or paid inference is performed.
