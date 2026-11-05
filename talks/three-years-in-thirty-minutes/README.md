# Three Years in Thirty Minutes

**Time-Travel Ethics Evaluation for AI Agents** — Torin van den Bulk and Vicente
Herrera. CNCF-Hosted Co-located Events North America 2026. Names, event date and
location follow the supplied PDF; the event schedule was not independently checked.

- Open [three-years.html](three-years.html) for the animated presentation.
- [three-years.pptx](three-years.pptx) is editable, with native fade transitions.
- [three-years.pdf](three-years.pdf) is the static fallback.
- [speaker-notes.md](speaker-notes.md) contains timing, caveats and source references.

The original visual theme uses navy, mint and amber, diagram cards, progressive
reveals and subtle ambient motion. No third-party anime artwork is embedded.
Right/Space reveals a card or advances; Left returns; N toggles speaker notes;
F enters fullscreen; M disables motion. Reduced-motion preferences are respected.

Rebuild from this directory:

```sh
python3 -m pip install -r requirements-build.txt
python3 build.py
python3 render_check.py
```

`build.py` is the editable source and writes HTML, PPTX, slide JSON and notes.
`render_check.py` expects Chromium at `/usr/bin/chromium`, validates navigation and
layout at 1600×900, generates preview images and exports PDF. It uses Playwright;
adapt the executable path for another machine. PowerPoint playback needs a final
check in the actual conference software. HTML and PDF were browser-validated.

For the three-minute demo, run `npm run ethics:demo -- --output
extensions/time-travel-ethics/runs/rehearsal` from the repository root before the
talk. Show the first global bypass, its next-month recovery branch, a scoped
exception followed by expiry, then `comparison.json`. The numbers are scripted
instrument calibration, not results for a real model. See the optional
[DeepEval bridge](../../extensions/time-travel-ethics/docs/DEEPEVAL.md) to attach
the policy and completion checks. Full evidence can be generated without Wi-Fi.
