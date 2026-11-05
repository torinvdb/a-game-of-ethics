# Three Years in Thirty Minutes — film-art presentation draft

**Time-Travel Ethics Evaluation for AI Agents** — Torin van den Bulk and Vicente
Herrera. CNCF-Hosted Co-located Events North America 2026. Names, date and location
follow the supplied PDF; the event schedule was not independently checked.

- [Animated HTML deck](three-years.html): fully self-contained, including fonts and artwork.
- [Editable PowerPoint](three-years.pptx): editable text and diagrams, with native fade transitions.
- [PDF fallback](three-years.pdf): static, all annotations visible.
- [Speaker notes](speaker-notes.md): timing, inference boundaries and research sources.

The visual revision uses actual **AKIRA poster artwork**, cream technical sheets,
condensed typography, vermilion incident pages and muted CRT evidence panels.
**No AI-generated illustration is included.** The inline Ghost in the Shell
references were visible in the conversation but were not exposed as downloadable
files; placing those exact originals remains pending receipt of image files or a
ZIP. The current draft uses the identified Akira artwork while that selection is
pending. Research copy, demo values, presenter names and timing are preserved.

Right/Space reveals the next annotation and corresponding diagram phase; Left
returns; **A** reveals all; **N** toggles notes; **F** enters fullscreen; **M**
disables motion. Reduced-motion preferences are respected. Diagrams trace the
clock distinctions, scenario relationships and reviewed feedback loop. They are
conceptual schematics, not measured data. HTML contains the progressive animation;
PowerPoint contains static diagrams and slide fades.

## Rebuild

```sh
python3 -m pip install -r requirements-build.txt
python3 build.py
python3 render_check.py
```

`build.py` owns the talk copy. `render_deck.py`, `deck.css` and `deck.js` own the
visuals and interaction. `render_check.py` expects Chromium at `/usr/bin/chromium`
and checks all 24 slides, text spacing, navigation, diagram reveals, reduced
motion, offline asset loading and viewport scaling. It exports PDF and previews.

The HTML embeds the bundled Nimbus fonts. Install the fonts in `assets/fonts/`
for faithful PowerPoint rendering; their license is included. PowerPoint text
remains editable. Rehearse the PPTX in the actual conference software; native
PowerPoint playback has not been tested here. HTML/PDF are the verified exports.

[Image provenance](assets/images.json) records the retrieved source, hashes,
resize operation and credits. The poster artwork and fonts retain their own
rights and are not relicensed under the repository's MIT license.

For the three-minute demo, run this from the repository root before the talk:

```sh
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/rehearsal
```

Show the first global bypass, its next-month recovery branch, a scoped exception
followed by expiry, then `comparison.json`. The numbers are scripted calibration,
not results for a real model. Full evidence can be generated without Wi-Fi.
