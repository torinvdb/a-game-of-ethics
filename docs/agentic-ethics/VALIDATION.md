# Verification record

**Second pass, 6 November 2026.** Executed after the first review below:

| Check | Exit | Result |
| --- | ---: | --- |
| `npm run ethics:test` | 0 | 140 tests pass |
| `npm test` (CLI, Node) | 0 | 60 tests pass |
| `npm run ethics:demo -- --output …/ink-v2-001` (DeepEval 4.3.3), repeated | 0 | Byte-identical repeat; counts unchanged; resume equivalence, revenue probe, 48-month horizon and independent oracle verified |
| `verify-evidence.py …/ink-v2-001 docs/agentic-ethics/evidence/manifest.json --inputs-root .` | 0 | 85/85 outputs and all inputs match |
| `tools/independent-oracle.py …/ink-v2-001` | 0 | 42/42 trajectories agree |
| `npm run ethics:scaffold -- …/scaffold-v2-002`, repeated | 0 | Same set digest twice; red-team 11/0/1; report gate blocks 80/80 detected misleading reports |
| Control plane: etcd + kube-apiserver + controller-manager v1.32.13 | 0 | Apply, PSA admit/reject, RBAC, NetworkPolicy selectors, namespace GC. No kubelet: no pod ran |
| `node benchmark/check_scenarios.mjs`; `benchmark/manifest.py verify` | 0 | All scenarios OK; manifest 2.0.2 PASS |

Status of each review gap: [SYSTEM-REVIEW.md §7](SYSTEM-REVIEW.md#7-gap-status-after-the-second-pass-2026-11-06).

---

**6 November 2026 review:** see [SYSTEM-REVIEW.md](SYSTEM-REVIEW.md) for the test
campaign. It records which results were executed and which are design intent.
Summary of the review:

- The 5 November baseline was reproduced byte for byte before any change: all 21
  recorded output hashes, including the DeepEval reports, with inkjs 2.4.0.
- Eight defects were fixed, among them credential forwarding on HTTP redirect and
  adapter failures counted as guard blocks or policy passes.
- Python tests went from 35 to 88.
- A mocked-tool agent scaffold was added, with frozen held-out cases.
- Provider-contract tests run against a local mock server.
- The container/Job now runs the Ink scenario. It was executed with Docker and a
  real OTel collector, but not on Kubernetes.

Current hashes: [evidence/manifest.json](evidence/manifest.json). The superseded
baseline is in [evidence/baseline-2026-11-05/](evidence/baseline-2026-11-05/).

| Check (6 Nov 2026) | Exit | Result |
| --- | ---: | --- |
| `npm run ethics:test` | 0 | 88 tests pass (provider contract, scaffold, trajectory recomputation, deploy consistency, evidence verification, plus the original 35) |
| `npm run ethics:demo -- --output …/review-005-final --deepeval-python …` | 0 | Same 7 trajectories and counts as below. The rejected adapter is now `execution_failure` / not evaluable (it was previously a policy-metric "pass") |
| `python3 extensions/time-travel-ethics/tools/verify-evidence.py RUN docs/agentic-ethics/evidence/manifest.json --inputs-root .` | 0 | 21/21 outputs and all inputs match |
| `python3 extensions/time-travel-ethics/tools/scaffold-eval.py --split all --output …` | 0 | 126 scripted-policy sessions. Guarded: 0 tool-level violations executed. Content violations (misleading reports) pass the guard. Deterministic across two runs |
| Docker build plus Job-equivalent run with an OTel collector | 0 | Collector received 1062 spans; Ink hashes identical; overwrite and collector-down runs fail as intended |
| `kubeconform -strict` (Kubernetes 1.32) on `kubectl kustomize deploy` | 0 | 7/7 valid. Not applied to any cluster (kind failed in the sandbox) |
| Inklecate validator | n/a | Not run. The working-tree validator now compiles with inkjs: 16 scenarios, 15 pass, 1 expected warning |

---

The record below is the original 5 November baseline, kept for comparison.

# Verification record

Verified locally on 5 November 2026. These are harness/calibration results,
not real-model performance or regulatory approval.

| Check | Result |
| --- | --- |
| `npm run ethics:test` | 35 tests pass: time/state, guard behavior, invalid responses, evidence edits, feedback review, input filtering, scenario generation and trajectory auditing |
| Full Ink demo | Seven complete trajectories plus an intentionally rejected remote-plaintext adapter; paired labels and delayed consequences checked |
| DeepEval 4.3.3 | Both custom metrics executed on all eight artifacts; bad policy and incomplete adapter produce expected failures |
| Offline guard | Python DNS attempt rejected before network access; forged zero-violation summary rejected |
| Original Inklecate validator | 12 core/template scenarios pass; new cluster scenario has zero errors and one expected warning about conventional verdict bands |
| Validator regressions | Reusable choices accepted; bookkeeping-only impacts and no-choice stories rejected |
| Presentation | 14 main slides + 3 hidden appendices; offline browser navigation, 35 reveal groups, notes, reduced motion, text bounds and four viewport sizes checked; native PPTX timing targets and four looping GIFs verified structurally; static PPTX/PDF supplied. Microsoft PowerPoint playback not exercised. |
| ADK 2.13.0 | Synthetic reviewed export passed `EvalSet.model_validate_json`; no ADK agent execution |

## Recorded cluster calibration

| Scripted policy | Decisions | Policy violations | Medical disruption | Education disruption | Release backlog |
| --- | ---: | ---: | ---: | ---: | ---: |
| Impact-aware | 144 | 0 | 18 | 18 | 0 |
| Delivery at all costs | 179 | 107 | 84 | 0 | 0 |
| Scoped exceptions | 155 | 0 | 18 | 18 | 0 |
| Defer batch work | 144 | 0 | 0 | 0 | 36 |
| Label-biased | 144 | 0 | 0 | 84 | 0 |
| Impact-aware, labels swapped | 144 | 0 | 18 | 18 | 0 |
| Label-biased, labels swapped | 144 | 0 | 84 | 0 | 0 |

The matched impact-aware trajectories select identical actions. All 36 capacity
choices flip in the intentionally label-biased pair. Impact units are authored
fixture assumptions, not clinical or financial estimates. Zero immediate API
disruption can displace cost into backlog. The exception trajectory reaches 11
expiry reviews; its last exception remains open at the horizon (censored).

[Comparison](evidence/cluster-calibration.json), [DeepEval reports](evidence/deepeval-calibration.json)
and [input/output hashes](evidence/manifest.json) are stored here. Full transcripts
are generated by the demo into ignored `runs/` directories. The manifest records
tool versions and source hashes; it is not a signed attestation. Its input hashes
allow you to distinguish later code edits from the recorded calibration.

## Reproduce

```sh
npm ci
npm run ethics:test
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/verification
# With Inklecate on PATH, also check the original validator:
npm run debug-scenarios -- --auto-validate scenarios/core/*.ink scenarios/tmpl/*.ink
python3 extensions/time-travel-ethics/tools/check-cluster-validator.py
```

The demo uses the compiler included in inkjs; the original validator uses
Inklecate 1.1.1. Both compiler paths produced matching scripted outcome counts.
For the optional DeepEval run, follow [its setup instructions](../../extensions/time-travel-ethics/docs/DEEPEVAL.md)
and add `--deepeval-python /absolute/path/to/venv/bin/python` to the demo command.
Dependency installation requires network access; inference credentials do not.

For the ADK schema check, install `requirements-adk.txt` in an isolated environment
and validate `extensions/time-travel-ethics/examples/adk.evalset.json` using
`google.adk.evaluation.eval_set.EvalSet.model_validate_json`. The corresponding
review record is explicitly synthetic and included for demonstration only.

## Outstanding verification

No live model/provider trials, complete production-agent execution, automatic
training, live telemetry collection or live scenario-authoring service was run.
As of 6 November the image is built and the Ink Job script runs under Docker
with a real collector. Kubernetes apply, NetworkPolicy enforcement and Flux
reconciliation remain unexecuted (see SYSTEM-REVIEW.md, section 6). Current
legal applicability and full-paper review remain incomplete because several
primary sites were unavailable. Native PowerPoint playback needs rehearsal in
the conference software.
