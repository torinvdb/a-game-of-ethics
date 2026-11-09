# Three Years in Thirty Minutes

**Time-Travel Ethics Evaluation for AI Agents** · Torin van den Bulk · Vicente Herrera
CNCF-Hosted Co-located Events North America 2026 (co-located day: Mon 9 Nov 2026,
Salt Lake City, per search results on 6 Nov 2026; **confirm room/time on the official
schedule**, as no public listing for this session was found).

**v4:** 13 main slides, **18 min 30 s** planned including a 3.5-minute demo, which leaves
about 10 minutes for questions. Flow: real incidents from 2026 (02) → what models are, and
the deterministic spine we build around them (03) → the model is the engine, not the car:
unit vs integration tests (04) → scope autonomy A0–A4 (05) → multi-agent boundaries (06) →
our incident, fast-forwarded, and the demo (07–09) → what we found (10) → your stack (11)
→ bind an agent like a workload (12). Autonomy levels, multi-agent and binding slides come
from ControlPlane's Advanced AI Security training (module 7). Ten hidden appendix slides
hold the per-model table, ledgers, fairness probe, stack status, evidence boundary,
calibration, held-out results, sources, regulatory map and the five-step checklist.

## Files

| File | Use it for |
| --- | --- |
| [`three-years.pptx`](three-years.pptx) | **Presenting.** Editable text, 50 native click reveals, auto title wipes, neon flicker-on entrances, a looping motion-path packet, 9 embedded animated GIFs |
| [`three-years-static.pptx`](three-years-static.pptx) | Low-motion / compatibility fallback: no timings, stills only |
| [`three-years.html`](three-years.html) | Fully offline browser deck (fonts and media embedded): speaker notes, timer, reduced motion |
| [`three-years.pdf`](three-years.pdf) | Handout: all 23 slides, fully revealed |
| [`speaker-notes.md`](speaker-notes.md) | Two-speaker script with `[CLICK]` cues, handoffs, timings and Q&A prep |
| [`DEMO-RUNBOOK.md`](DEMO-RUNBOOK.md) | Rehearsed demo commands, expected output and fallbacks |
| [`demo/replay.py`](demo/replay.py) | Stage-friendly retro replay of recorded trajectories |
| [`REVIEW.md`](REVIEW.md) | Critique of v1 and what v2 changed |
| [`assets/ASSET-LEDGER.md`](assets/ASSET-LEDGER.md) | Provenance of every visual and font |
| [`preview/`](preview/) | Per-slide JPEGs, `contact-sheet.jpg` and a browser-recorded `motion-preview.mp4` |

**Before presenting:** install `assets/fonts/Oswald-Bold.ttf`, `Rajdhani-SemiBold.ttf`
and `ShareTechMono-Regular.ttf`, then run Slide Show (F5). GIFs and entrance effects
play only in Slide Show. If the venue player misbehaves, use the HTML deck (press F
for fullscreen) or the static PPTX.

HTML keys: →/Space next · ← back · N notes · M motion on/off · A reveal all ·
R appendix · B blank · T reset timer · F fullscreen. The closing slide doesn't run
into the appendix. `?still` or `prefers-reduced-motion` uses still images.

## Art direction

Late-1980s/1990s cyberpunk anime backgrounds: dusk megacity haze, kanji signage, overhead
cables, CRT consoles, server halls. Each sign is a word from the talk (監査 audit,
例外 exception, 署名 signature, 期限 deadline). Machinery is cel-shaded: ink outlines,
highlight and shadow bands, rim light from the neon, hazard stripes, rivets. Instruments
use period hardware: nixie tubes, a VFD readout, an oscilloscope, LED strips, ferrite
cores.

All visuals are drawn by `scenery.py` and `motion.py`. No film frames, photos or
generated art.

Each animation maps to a slide's point:

| Slide | Motion |
| --- | --- |
| 01, 13 | 倫理 sign with a failing tube |
| 07 | The "disable" sign is the one that sparks |
| 08 | Oscilloscope sweep over three branches and 36 months |
| 09 | CRT console replays the demo run |
| A2 | Faulting arm: "adapter fault, logged, not scored" |
| A3 | Label swap; 36 LEDs flip for the biased control |

## Build

```bash
python3 -m pip install -r requirements-build.txt
```

```bash
python3 build.py
```

```bash
python3 render_check.py
```

`build.py` renders the plates (if missing), then motion (about 2 min), then both
PPTX files, the HTML and the speaker notes. `build.py --fast` reuses existing motion.
`render_check.py` uses Playwright's Chromium to screenshot every slide and check
for text overflow and overlap, console errors, navigation and four viewport sizes.
It also exports the PDF and verifies the PPTX package: hidden appendix, animation
targets and multiframe GIF media. Results are in
[`render-validation.json`](render-validation.json).

## What has and has not been verified

- **Verified here:** browser rendering and navigation (Chromium); PPTX package
  structure; LibreOffice import and static rendering of both PPTX files; GIF frame
  counts.
- **Not verified:** **Microsoft PowerPoint playback** (Windows/macOS) of the custom
  flicker and motion-path effects, the conference AV setup, and font substitution on
  the presenting laptop. Rehearse once in real PowerPoint. If any custom effect
  misbehaves, change it to Fade in the Animation Pane; the content is unaffected.
