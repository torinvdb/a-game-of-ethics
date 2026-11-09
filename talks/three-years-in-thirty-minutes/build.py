"""Build every presentation export from content.json.

  python3 build.py            # plates (if missing) + motion + PPTX/HTML + notes
  python3 build.py --fast     # reuse existing motion assets
Then: python3 render_check.py  (screenshots, layout checks, PDF export)
"""
import json
import sys
from pathlib import Path

import qrcode
from PIL import Image

import motion
import scenery
from render_deck import render, cue_cards, SPEAKERS, TITLE, EVENT

ROOT = Path(__file__).parent
slides = json.loads((ROOT / 'content.json').read_text())
main = [s for s in slides if s['duration']]
assert 12 <= len(main) <= 16, len(main)

if not all((ROOT / 'assets/plates' / f'{p}.jpg').exists() for p in scenery.PLATES):
    scenery.build()
if '--fast' in sys.argv:
    for s in slides:
        motion.background(s)
else:
    motion.build(slides)

for url, name in (('https://github.com/torinvdb/a-game-of-ethics', 'qr-repo'),
                  ('https://control-plane.io/', 'qr-controlplane')):
    qr = qrcode.QRCode(border=2, box_size=10, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(url)
    qr.make_image(fill_color=(64, 196, 178), back_color=(7, 13, 16)).convert('RGB').resize((300, 300), Image.NEAREST) \
        .save(ROOT / f'assets/{name}.png')

(ROOT / 'slides.json').write_text(json.dumps(slides, indent=1, ensure_ascii=False) + '\n')
render(ROOT, slides)

# Rehearsal script (two speakers, timings, handoffs)
total = sum(s['duration'] for s in main)
out = [f'# {TITLE}', f'{SPEAKERS} · {EVENT}', '',
       f'**Main talk: {len(main)} slides, {total // 60} min {total % 60:02d} s planned** (incl. a 4-minute demo) '
       f'→ about {30 - total / 60:.0f} minutes for questions in a 30-minute slot. '
       f'{len(slides) - len(main)} hidden appendix slides follow the closing slide.', '',
       '| # | Slide | Speaker | Seconds | Cumulative |', '| ---: | --- | --- | ---: | ---: |']
cum = 0
for i, s in enumerate(main):
    cum += s['duration']
    out.append(f"| {i + 1:02d} | {s['title'].replace(chr(10), ' ')} | {s['speaker']} | {s['duration']} | "
               f"{cum // 60}:{cum % 60:02d} |")
out += ['', '`[CLICK]` marks a presenter click (one reveal group). Handoffs are marked **HANDOFF**.', '',
        '## Cue cards', '',
        'Glance-and-go version: one line per click. The same cards open first in PowerPoint presenter view '
        'and in the HTML deck (press N). The full script follows below.', '']
for cue in cue_cards(slides).values():
    head, *lines = cue.split('\n')
    out += [f'**{head}**', ''] + [f'- {ln[2:]}' for ln in lines] + ['']
out += ['## Full script', '']
for i, s in enumerate(slides):
    label = f'{i + 1:02d}' if s['duration'] else s['chapter']
    out += [f"## {label}. {s['title'].replace(chr(10), ' ')}",
            f"*{s.get('speaker') or 'appendix'} · {s['duration']} s*" if s['duration'] else '*hidden appendix*', '']
    if s.get('script'):
        out += [s['script'], '']
    if s.get('notes'):
        out += ['> ' + s['notes'], '']
    if s.get('refs'):
        out += ['Sources: ' + '; '.join(s['refs']), '']
(ROOT / 'speaker-notes.md').write_text('\n'.join(out) + '\n')
print(f'Built {len(main)} main + {len(slides) - len(main)} appendix slides; {total} s planned.')
