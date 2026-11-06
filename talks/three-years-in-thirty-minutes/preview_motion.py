"""Record the browser deck with the same GIF assets embedded in PowerPoint.

This is a visual preview, not a recording of Microsoft PowerPoint playback.
"""
import argparse, subprocess, tempfile, time
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
root=Path(__file__).parent
with tempfile.TemporaryDirectory(prefix='ethics-motion-') as frames_dir, sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1280,'height':720})
    page=context.new_page();page.set_content((root/'three-years.html').read_text())
    page.evaluate('document.fonts.ready');page.evaluate('Promise.all([...document.images].map(i=>i.decode()))')
    page.add_style_tag(content='nav{display:none!important}')
    frame=0
    def capture(seconds):
        global frame
        start=time.monotonic()
        for n in range(round(seconds*8)):
            page.screenshot(path=str(Path(frames_dir)/f'{frame:04d}.png'));frame+=1
            page.wait_for_timeout(max(0,((n+1)/8-(time.monotonic()-start))*1000))
    page.evaluate('show(0)');capture(2.5)
    page.evaluate('show(1)');capture(0.75)
    for _ in range(3):page.evaluate('next()');capture(1.25)
    capture(1)
    page.evaluate('show(3)');page.evaluate('revealAll()');capture(6)
    page.evaluate('show(4)');page.evaluate('revealAll()');capture(5)
    page.evaluate('show(13)');page.evaluate('revealAll()');capture(2.25)
    context.close();browser.close()
    subprocess.run(['ffmpeg','-y','-framerate','8','-i',str(Path(frames_dir)/'%04d.png'),'-an','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print(a.output)
