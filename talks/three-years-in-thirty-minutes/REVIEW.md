# v1 → v2 review

## Prioritised critique of v1 (as a skeptical attendee)

1. **Generic look.** It read as a dark business template with two wallpaper crops
   behind it. The motion (four GIFs) was decorative and repeated, and a neon "bus"
   strip ran on every slide.
2. **Rights risk.** Its only imagery was third-party Ghost in the Shell-themed
   wallpaper crops of unclear licence, and the deck leaned on them.
3. **No decision moment.** Slide 2 asked "what does your agent do?" but never showed
   the options. The core idea, that the good answers are non-binary (scoped exception,
   defer, escalate), was buried in notes.
4. **Jargon before payoff.** "Logical clock", "paired-label probes" and "control
   evaluation" appeared before the audience had a reason to care.
5. **Competing messages.** Feedback loops, RLHF caveats, the stack and the
   checklist each got a slide, with no through-line back to the incident.
6. **Tiny text.** Labels were 14–19 px on a 1600 px canvas (≈10–13 pt), and several
   slides carried three typefaces at small sizes.
7. **Overclaims** (see `docs/agentic-ethics/research/CLAIM-AUDIT.md`): "every session
   can become a test", provider support implied by adapters, a "36 batches ≈ 3 years"
   reading, and research one-liners without their constructed conditions.
8. **Execution errors were not separated** from ethical failures in the story, which
   was also true of the code (fixed in v2; see the system review).
9. **A weak demo.** It printed JSON lines and had no stage-readable replay, no
   rehearsed fallback and no runbook.
10. **No two-speaker choreography.** Handoffs and who says what were unspecified.

## What v2 does

- **One narrative, one message per slide, 15 slides.** Incident (2–4) → time (5–6)
  → method (7–8) → demo (9) → evidence (10–12) → platform (13) → adoption (14–15).
  Research detail moved to the notes and appendix.
- **A decision slide** with four doors. The shortcut is the one that sparks.
- **Four ledgers** (execution / rules / work / people), matching the code change
  that keeps adapter faults out of the ethics score.
- **Original code-drawn art.** Five painted plates and 14 motion assets; each
  animation explains a concept. Kanji signage uses words from the talk.
- **Native PowerPoint animation**, not just transitions: auto title wipes, neon
  flicker-on entrances, a looping motion path, 44 click reveals, and GIFs painted over
  the exact background crop so edges match the slide.
- **Type minimums:** body ≥ 22 px (≈16 pt), titles 60–124 px, mono labels ≥ 18 px,
  and only footnote references below that.
- **Claims reworded** per the claim audit, with execution status pointed at
  VALIDATION.md (appendix A1).
- **The demo** is pre-generated, then replayed with `demo/replay.py`, with a timed
  runbook and three fallbacks.
- **Script:** speaker tags on every slide, `[CLICK]` cues, explicit HANDOFFs and
  likely Q&A answers.
