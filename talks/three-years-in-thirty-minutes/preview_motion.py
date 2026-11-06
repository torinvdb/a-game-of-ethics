"""Record a short MP4 walkthrough of the offline HTML deck (browser playback).

This uses the same GIFs that are embedded in the PPTX, but it is a *browser*
recording, not a recording of Microsoft PowerPoint playback.

  python3 preview_motion.py --output preview/motion-preview.mp4   (needs FFmpeg)
"""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument('--output', type=Path, required=True)
ap.add_argument('--slides', default='1,2,3,5,6,8,11,12', help='1-based slide numbers to include')
a = ap.parse_args()
a.output.parent.mkdir(parents=True, exist_ok=True)
root = Path(__file__).parent
with tempfile.TemporaryDirectory(prefix='deck-video-') as tmp, sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1280, 'height': 720}, record_video_dir=tmp,
                        record_video_size={'width': 1280, 'height': 720})
    pg = ctx.new_page()
    pg.goto((root / 'three-years.html').as_uri())
    pg.wait_for_function('window.deck !== undefined')
    for n in [int(x) for x in a.slides.split(',')]:
        pg.evaluate(f'deck.go({n - 1}, false, true)')
        pg.wait_for_timeout(1600)
        for _ in range(pg.evaluate('deck.state.groups')):
            pg.keyboard.press('ArrowRight')
            pg.wait_for_timeout(1100)
        pg.wait_for_timeout(1200)
    video = pg.video.path()
    ctx.close()
    b.close()
    subprocess.run(['ffmpeg', '-y', '-i', video, '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '24',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(a.output)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(a.output)
