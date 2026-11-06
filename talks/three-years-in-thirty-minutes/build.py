"""Build the concise, animated PowerPoint and its offline companion exports."""
import json
from pathlib import Path
from make_motion import build as motion
from render_deck import render
ROOT=Path(__file__).parent
if not (ROOT/'assets/motion/manifest.json').exists():motion()
slides=json.loads((ROOT/'content.json').read_text())
assert len([s for s in slides if s['duration']])==14
(ROOT/'slides.json').write_text(json.dumps(slides,indent=2)+'\n')
render(ROOT,slides)
