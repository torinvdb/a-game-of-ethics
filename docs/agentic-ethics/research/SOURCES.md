# Source snapshots

`retrieval.json` identifies retrieval outcomes, source URLs and hashes. Paths
beginning `research/` are relative to the parent `docs/agentic-ethics` directory.
The snapshots preserve the reviewed project documentation; some upstream default
branch links may move. DeepEval additionally has a recorded immutable commit.

Third-party source snapshots retain their upstream authorship and applicable
licenses; the repository's MIT license does not relicense them. DeepEval's Apache
2.0 license is preserved alongside its snapshot. Consult each linked project for
its complete license and attribution requirements before redistributing source
material separately. Authored synthesis is in `RESEARCH-DOSSIER.md`.

Project documentation is evidence about an implementation and its stated scope.
It does not substitute for reading the full study, validating its methodology or
checking current legal texts. Retrieval failures are recorded, not filled in with
invented citations or results.

Source snapshots are intentionally byte-preserved, including upstream trailing
whitespace, so the retrieval hashes remain verifiable. Authored-file whitespace
checks exclude this snapshot directory.

## 2026-11-06 verification pass

`RESEARCH-DOSSIER-V2.md`, `CLAIM-AUDIT.md` and `REGULATORY-MAP.md` were added. New
byte-preserved snapshots, hashed in `retrieval.json`:

- `k8s-agent-sandbox-readme.md` and `k8s-agent-sandbox-roadmap.md`: kubernetes-sigs, Apache-2.0
- `kagent-readme.md`: Apache-2.0
- `inspect-k8s-sandbox-readme.md`: UK AISI
- `otel-genai-semconv-readme.md` and `otel-genai-agent-spans.md`: OpenTelemetry, Apache-2.0
- `adk-eval-criteria.md` and `adk-eval-index.md`: google/adk-docs

The ten earlier snapshots were re-fetched; their hashes are unchanged.

Anthropic research pages were read through a summarising fetch tool and were not
snapshotted. Treat their numbers as "P-sum" and re-check them verbatim before quoting.

**Blocked hosts:** events.linuxfoundation.org, cncf.io, arxiv.org, metr.org, eur-lex,
nist.gov, leg.colorado.gov, opentelemetry.io and law-firm sites. Event and regulatory dates
attributed to those hosts come from search-index summaries and are graded "S".
