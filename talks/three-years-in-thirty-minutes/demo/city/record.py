#!/usr/bin/env python3
"""Record the city demo to MP4 (or a GIF for the README), frame by frame.

The page runs in capture mode: its clock only advances when this script asks for the next frame,
so the video is smooth and identical on every run, however loaded the machine is.

  node --env-file=.env talks/three-years-in-thirty-minutes/demo/city/server.mjs &
  python3 talks/three-years-in-thirty-minutes/demo/city/record.py --intro --out intro.mp4
  python3 .../record.py --run data/blackout/claude-opus-5-5-path-3210.json --out blackout-opus.mp4
  python3 .../record.py --intro --gif --width 800 --fps 12 --out ../../../../img/city-intro.gif

Needs: pip install playwright==1.63.0 (then `playwright install chromium`), and ffmpeg on PATH or
`pip install imageio-ffmpeg` (a bundled binary, handy on Windows).
"""
import argparse
import glob
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright


def chromium_path():
    # Use the newest cached headless shell if Playwright's pinned build is not installed.
    hits = sorted(glob.glob(os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell')))
    return hits[-1] if hits else None


def ffmpeg_path():
    exe = shutil.which('ffmpeg')
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        raise SystemExit('ffmpeg not found: install it, or pip install imageio-ffmpeg')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default='http://127.0.0.1:8787/')
    ap.add_argument('--run', help='recording to play, e.g. data/blackout/<id>.json')
    ap.add_argument('--intro', action='store_true')
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--max-seconds', type=float, default=240)
    ap.add_argument('--tail', type=float, default=1.0, help='seconds to keep after the run ends')
    ap.add_argument('--gif', action='store_true')
    ap.add_argument('--width', type=int, default=1920)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    ffmpeg = ffmpeg_path()
    q = ['capture', f'speed={a.speed}'] + (['intro'] if a.intro else []) + ([f'run={a.run}'] if a.run else [])
    url = a.url + '?' + '&'.join(q)
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='city-demo-') as tmp, sync_playwright() as p:
        exe = chromium_path()
        browser = p.chromium.launch(**({'executable_path': exe} if exe else {}))
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(url)
        page.wait_for_function('window.__ready === true', timeout=30000)
        dt, n, tail = 1 / a.fps, 0, None
        while n * dt < a.max_seconds:
            page.evaluate(f'window.__cap.frame({dt})')
            page.screenshot(path=f'{tmp}/f{n:06d}.jpg', type='jpeg', quality=92)
            n += 1
            if tail is None and page.evaluate('window.__cap.done'):
                tail = n + int(a.tail * a.fps)
            if tail is not None and n >= tail:
                break
        browser.close()
        if errors:
            raise SystemExit('page errors: ' + '; '.join(errors[:3]))
        src = ['-framerate', str(a.fps), '-i', f'{tmp}/f%06d.jpg']
        if a.gif:
            vf = f'scale={a.width}:-1:flags=neighbor,split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=3'
            subprocess.run([ffmpeg, '-y', '-loglevel', 'error', *src, '-vf', vf, str(out)], check=True)
        else:
            subprocess.run([ffmpeg, '-y', '-loglevel', 'error', *src, '-vf', f'scale={a.width}:-2:flags=neighbor',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', str(out)], check=True)
    print(f'{out} ({n} frames, {n / a.fps:.1f} s)')


if __name__ == '__main__':
    main()
