# Three Years in Thirty Minutes

**Time-Travel Ethics Evaluation for AI Agents** · Torin van den Bulk · Vicente Herrera
CNCF-Hosted Co-located Events North America 2026 (co-located day: Mon 9 Nov 2026,
Salt Lake City, per search results on 6 Nov 2026; **confirm room/time on the official
schedule**, as no public listing for this session was found).

**v2:** 15 main slides, **22 min 50 s** planned including a 4-minute demo, which
leaves about 7 minutes for questions. Five hidden appendix slides cover the evidence
boundary, the full calibration table, sources, the regulatory map and fallbacks.

One story runs through the talk: **incident → decision → persistent consequence →
test method → evidence → adoption decision.**

## Files

| File | Use it for |
| --- | --- |
| [`three-years.pptx`](three-years.pptx) | **Presenting.** Editable text, 44 native click reveals, auto title wipes, neon flicker-on entrances, a looping motion-path packet, 9 embedded animated GIFs |
| [`three-years-static.pptx`](three-years-static.pptx) | Low-motion / compatibility fallback: no timings, stills only |
| [`three-years.html`](three-years.html) | Fully offline browser deck (fonts and media embedded): speaker notes, timer, reduced motion |
| [`three-years.pdf`](three-years.pdf) | Handout: all 20 slides, fully revealed |
| [`speaker-notes.md`](speaker-notes.md) | Two-speaker script with `[CLICK]` cues, handoffs, timings and Q&A prep |
| [`DEMO-RUNBOOK.md`](DEMO-RUNBOOK.md) | Rehearsed demo commands, expected output and fallbacks |
| [`demo/replay.py`](demo/replay.py) | Stage-friendly retro replay of recorded trajectories |
| [`REVIEW.md`](REVIEW.md) | Critique of v1 and what v2 changed |
| [`assets/ASSET-LEDGER.md`](assets/ASSET-LEDGER.md) | Provenance of every visual and font |
| [`preview/`](preview/) | Per-slide PNGs, `contact-sheet.jpg` and a browser-recorded `motion-preview.mp4` |

**Before presenting:** install `assets/fonts/Oswald-Bold.ttf`, `Rajdhani-SemiBold.ttf`
and `ShareTechMono-Regular.ttf`, then run Slide Show (F5). GIFs and entrance effects
play only in Slide Show. If the venue player misbehaves, use the HTML deck (press F
for fullscreen) or the static PPTX.

HTML keys: →/Space next · ← back · N notes · M motion on/off · A reveal all ·
R appendix · B blank · T reset timer · F fullscreen. The closing slide doesn't run
into the appendix. `?still` or `prefers-reduced-motion` uses still images.

## Art direction

Late-80s/90s cyberpunk anime vocabulary: dusk megacity haze, dense kanji signage
(each sign is a word from the talk: 監査 audit, 例外 exception, 署名 signature, 期限
deadline…), overhead cables, CRT phosphor consoles, machine rooms, industrial robot
arms and small localized sparks. Every visual is **drawn by code** in `scenery.py` and
`motion.py`: no film frames, posters, photos or AI-generated art. The motion explains
something: a terminal types the incident; the "disable" sign is the one that sparks; a
timeline shows the three branches across 36 months; three clocks separate logical,
wall and experienced time; a robot arm seals the scenario with its real hash; the label
swap flips 36 cells; a faulting arm is labelled "logged, not scored".

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
