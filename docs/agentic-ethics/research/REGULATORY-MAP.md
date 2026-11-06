# Regulatory and enterprise map (checked 6 November 2026)

> **An evaluation artifact is not a compliance determination.** Results from this harness
> can be *evidence* that an accountable owner, counsel or an auditor uses. They do not
> establish that any system is lawful, conformant, certified, non-discriminatory or safe
> for a given use. Applicability depends on role (provider, deployer and so on), use case,
> sector and jurisdiction. Nothing here is legal advice.

## 1. Access limits

EUR-Lex, NIST, the Colorado General Assembly and law-firm sites were **blocked** in this
session. Status grades:

- **B**: base text known from the regulation or standard as published. It was not re-fetched
  this session.
- **S**: reported consistently by several search-index results; the primary text was not
  fetched.
- **U**: unverified or conflicting.

Re-check every **S** item on the official page before printing a date on a slide.

## 2. Instrument types

| Instrument | Type | Binding? |
| --- | --- | --- |
| EU AI Act, Regulation (EU) 2024/1689 | EU law | Yes, within scope |
| Digital Omnibus on AI, Regulation (EU) 2026/1744 | EU law that amends the AI Act | Yes |
| GDPR, Regulation (EU) 2016/679 | EU law | Yes, within scope |
| GPAI Code of Practice (EU) | Voluntary code; can be used to demonstrate compliance | No |
| NIST AI RMF 1.0 (AI 100-1) and Generative AI Profile (AI 600-1) | US federal guidance / voluntary framework | No |
| ISO/IEC 42001:2023 | International management-system standard; certifiable by accredited bodies | No, unless contracted |
| Colorado SB 24-205, replaced by SB 26-189 | US state law | Yes, within scope |
| US Executive Orders (e.g. EO 14365) | Executive direction to federal agencies; does not itself preempt state law | Directs agencies only |

## 3. Dates

### EU AI Act (Regulation 2024/1689), as amended by Regulation 2026/1744

| Date | Obligation | Grade |
| --- | --- | --- |
| 1 Aug 2024 | Entry into force | B |
| 2 Feb 2025 | Prohibited practices (Art. 5) and AI literacy (Art. 4) | B |
| 2 Aug 2025 | GPAI model obligations, governance and penalties | B/S |
| 2 Aug 2026 | Commission enforcement powers over GPAI providers; general application, including Art. 50 transparency (reported **not** delayed) | B/S |
| 24 Jul 2026 | Regulation 2026/1744 published in the Official Journal (ELI: http://data.europa.eu/eli/reg/2026/1744/oj), dated 8 Jul 2026; Parliament endorsed it 16 Jun 2026 and the Council adopted it 29 Jun 2026 | S |
| 27 Jul 2026 | Regulation 2026/1744 enters into force | S |
| 2 Dec 2026 | Two new Art. 5 prohibitions added by the Omnibus | S, details unverified |
| 2 Aug 2027 | GPAI models placed on the market before 2 Aug 2025 must comply; national regulatory sandboxes due (moved from 2 Aug 2026) | B/S |
| **2 Dec 2027** | **Annex III stand-alone high-risk obligations** (originally 2 Aug 2026) | S |
| **2 Aug 2028** | **Annex I product-embedded high-risk obligations** (originally 2 Aug 2027) | S |

A corrigendum to Regulation 2026/1744 dated 29 Sep 2026 is listed by DIN; it was not
examined (U). Pages still describing the Omnibus as "proposed" predate its adoption.

### NIST

| Item | Status | Grade |
| --- | --- | --- |
| AI RMF 1.0 (NIST AI 100-1) | Released 26 Jan 2023; still the version in use | B |
| AI RMF revision | Under way, directed by the July 2025 AI Action Plan. No revised text was found; treat "1.1" or "2.0" labels as unofficial | S/U |
| AI 600-1, Generative AI Profile | Final, 26 Jul 2024 | B |

### ISO/IEC 42001:2023

Published December 2023. It specifies an AI management system (AIMS), certifiable through
accredited third-party audit (B/S). Its scope is organisational processes, not individual
model behaviour.

### Colorado

| Date | Event | Grade |
| --- | --- | --- |
| 2024 | SB 24-205 enacted, originally effective 1 Feb 2026 | B |
| 28 Aug 2025 | SB25B-004 delayed the effective date to 30 Jun 2026 | S |
| 27 Apr 2026 | Federal court order reportedly halted enforcement of SB 205 (xAI litigation). Sources disagree on the procedural posture | S/U |
| 14 May 2026 | **SB 26-189 signed**, repealing and replacing SB 24-205 with a narrower, notice-based automated-decision law, **effective 1 Jan 2027** | S |

**Do not say** "the Colorado AI Act took effect June 2026".

### US federal

| Date | Action | Grade |
| --- | --- | --- |
| Jul 2025 | "America's AI Action Plan" | S |
| 11 Dec 2025 | **EO 14365**, which challenges state AI laws through a DOJ AI Litigation Task Force (operating from 10 Jan 2026) and grant conditions. An executive order does not itself preempt state law | S |
| 2026 | White House legislative recommendations (National Policy Framework); FTC proposed policy statement on preemption (reported 1 Jul 2026) | S, final status unverified |

There is no comprehensive US federal AI statute.

## 4. Enterprise concerns: what the harness can evidence, and what it cannot

| Concern | What this harness can contribute | Still required elsewhere | Typical anchors |
| --- | --- | --- | --- |
| Intended use | A scenario card naming the use, its authority and its out-of-scope uses | Owner-approved use-case register | AI Act Art. 9/13 (high-risk); NIST MAP 1; ISO 42001 cl. 6 |
| Affected people | Impact cards; matched-label probes | Domain review of impacts; stakeholder input; fairness analysis with real outcomes | AI Act Art. 27 FRIA (certain deployers); NIST MAP 5; GDPR Art. 35 DPIA |
| Materiality | Severity tiers per action | Legal classification (Annex III? consequential decision under Colorado law?) | AI Act Art. 6; SB 26-189 |
| Authority | Allowed/denied action contracts | IAM design and approval policy | NIST GOVERN 2; ISO 42001 A.3 |
| Least privilege | Measured denied-action attempts and blocked effects | Production permission review | Security baselines; ISO 27001 if in scope |
| Human oversight | Escalation/defer choices and expiry reviews are tested | Reviewer competence, time and authority to refuse | AI Act Art. 14 (providers) and Art. 26 (deployers) |
| Audit evidence | Hashed runs, manifests, OTLP records | Signed, tamper-evident retention; an independent auditor | AI Act Art. 11/12/19; ISO 42001 cl. 9 |
| Traceability | Scenario/version/prompt/tool lineage; OTel `gen_ai.agent.version` (Development status) | Organisation-wide lineage of models, data and deployments | AI Act Art. 12 logging; NIST MEASURE 2 |
| Privacy | Synthetic canaries; consent-expiry scenarios | Lawful basis; DPIA; controller/processor terms | GDPR Arts. 5, 6, 22, 25, 35 |
| Retention | Tests of retention and deletion behaviour in memory | A retention schedule and proof of deletion in real stores | GDPR Art. 5(1)(e); AI Act log-retention duties |
| Change control | Re-run frozen suites when the model, prompt, tool or memory changes | A change board and release criteria | ISO 42001 cl. 8; NIST MANAGE 4 |
| Rollback | Recovery and restore decisions are exercised | Tested operational rollback and compensating transactions | Operational resilience rules (sector-specific) |
| Monitoring | Regression suite and drift probes on frozen cases | Production monitoring, incident reporting and post-market monitoring | AI Act Art. 72/73 (providers); NIST MANAGE 4 |

Article numbers are pointers for counsel to check against the consolidated text. They are
not applicability findings.

## 5. Wording for slides

- Use: "Evidence for an accountable release decision." Avoid: "compliant", "certified",
  "AI Act-ready".
- Use: "EU high-risk obligations now start Dec 2027 / Aug 2028 (Omnibus; verify)". Avoid:
  "Aug 2026 high-risk deadline".
- Use: "NIST AI RMF is voluntary guidance; ISO/IEC 42001 is a certifiable management-system
  standard."
