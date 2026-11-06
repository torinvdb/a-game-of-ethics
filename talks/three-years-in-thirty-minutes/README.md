# Three Years in Thirty Minutes

**Time-Travel Ethics Evaluation for AI Agents** — Torin van den Bulk · Vicente Herrera.
CNCF-Hosted Co-located Events North America 2026.

The main talk is now **14 slides**, with a 22-minute 10-second rehearsal budget
including a three-minute demo, leaving room for questions in the 30-minute slot.
Three research/verification appendices are hidden in PowerPoint's normal slide
show. The narrative follows one blocked deployment: pressure, affected people,
persistent consequences, the evaluation loop, then the decision to grant autonomy.

## Present

- **[Animated PowerPoint](three-years.pptx)** — editable text/diagrams, 35 click
  groups and four embedded looping GIFs: terminal boot, neon signal circuit,
  logical clock, and a robotic diagnostic fault with localized sparks.
- **[Static PowerPoint](three-years-static.pptx)** — all content visible, motion
  assets frozen. Use this for low-motion viewing and compatibility fallback.
- **[Offline HTML](three-years.html)** — embedded images, motion and fonts; no server
  or internet required.
- **[PDF](three-years.pdf)** — all 17 slides, including appendices, fully revealed.
- **[Speaker notes](speaker-notes.md)** — pacing, research citations, inference
  boundaries and the three-minute demo sequence.

**Start the animated PPTX in Slide Show mode (F5).** Click to reveal each evidence
group. GIFs are static in editing view and PDF; supported PowerPoint desktop
players animate them in Slide Show. Install the three bundled Nimbus fonts from
`assets/fonts/` before presenting to preserve the intended typography. Text,
shapes and timing remain editable. If the conference player substitutes fonts or
ignores GIF motion, use the self-contained HTML or the static/PDF fallback.

Browser controls: Right/Space reveals or advances; Left returns; **A** reveals
all; **N** shows notes; **M** freezes motion; **R** opens/exits the appendix;
**F** enters fullscreen; Home/End select the main opening/closing. The main
closing stops navigation into the appendix. Reduced-motion preferences select
PNG stills automatically. Sparks are small localized events, with no full-frame
flashing or audio. They illustrate a fault, not a measured agent failure.

The city/architecture imagery is cropped from existing third-party artwork in a
Ghost in the Shell-themed collection. There is **no Akira poster and no newly
generated anime artwork**. These are not authenticated film frames or the exact
inline reference originals. [Provenance](assets/images.json) records immutable
retrieval URLs, source/asset hashes and crop coordinates. See
[asset notes](assets/SOURCES.md) for rights and font details.

## Rebuild and check

```sh
python3 -m pip install -r requirements-build.txt
python3 make_motion.py  # regenerate GIFs/stills when their design changes
python3 build.py
python3 render_check.py
```

`content.json` is the editorial source. `render_deck.py` makes a shared scene
layout for editable PPTX and HTML; `pptx_motion.py` builds native PowerPoint
entrance timing. `make_motion.py` draws deterministic UI/diagram animations, not
AI illustrations or experimental data. `deck.css` and `deck.js` provide browser
playback. The static PPTX has no GIF media or entrance timings.

`preview_motion.py --output preview.mp4` records a browser preview using the same
embedded GIF assets; it is not a recording of PowerPoint playback. It needs the
system FFmpeg executable.

`render_check.py` needs Chromium at `/usr/bin/chromium`. It checks all 17 slides,
text bounds/overlap, navigation, reveal groups, appendix boundary, speaker notes,
motion controls, offline assets, four viewport sizes, native timing references,
multiframe GIF media and PDF structure. It exports PDF and preview images.
[Validation results](render-validation.json) distinguish browser/render checks
from PowerPoint package checks: **Microsoft PowerPoint playback and conference
hardware have not been tested here.**

## Demo

From the repository root:

```sh
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/rehearsal
```

Show the first global bypass, its next-month recovery branch, a scoped exception
followed by expiry, then `comparison.json`. Results are scripted calibration,
not results for a real model. The full evidence can be generated without Wi-Fi.
