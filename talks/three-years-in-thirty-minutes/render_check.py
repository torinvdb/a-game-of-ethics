"""Render + layout checks for the browser deck, PDF export and PPTX package.

Writes: preview/slide-NN.jpg (fully revealed stills), preview/contact-sheet.jpg,
three-years.pdf, render-validation.json. Needs Playwright's Chromium.
"""
import json
import zipfile
from pathlib import Path

from lxml import etree
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
PREV = ROOT / 'preview'
PREV.mkdir(exist_ok=True)
slides = json.loads((ROOT / 'content.json').read_text())
report = {'scope': 'Browser render (Chromium/Playwright) + PPTX package structure. '
                    'Microsoft PowerPoint playback is NOT exercised by this script.', 'checks': {}}
errors = []

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=__import__('shutil').which('chromium') or None) if False else p.chromium.launch()
    pg = b.new_page(viewport={'width': 1600, 'height': 900})
    pg.on('console', lambda m: m.type == 'error' and errors.append(m.text))
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto((ROOT / 'three-years.html').as_uri() + '?still')
    pg.wait_for_function('window.deck !== undefined')
    layout_issues, step_counts = [], []
    for i in range(len(slides)):
        pg.evaluate(f'deck.go({i}, true, true)')
        pg.wait_for_timeout(120)
        st = pg.evaluate('deck.state')
        step_counts.append(st['groups'])
        boxes = pg.evaluate('''() => [...document.querySelectorAll('.slide.current .el.text')].map(n => {
            const r = n.getBoundingClientRect(); return {t: n.textContent.slice(0, 40), x: r.left, y: r.top,
            w: n.scrollWidth, h: n.scrollHeight, cw: n.clientWidth, ch: n.clientHeight, r: r.right, b: r.bottom}; })''')
        for bx in boxes:
            if bx['w'] > bx['cw'] + 2:
                layout_issues.append(f'slide {i + 1}: text wider than box: {bx["t"]!r}')
            if bx['r'] > 1601 or bx['b'] > 901:
                layout_issues.append(f'slide {i + 1}: text outside stage: {bx["t"]!r}')
        for a in range(len(boxes)):
            for c in range(a + 1, len(boxes)):
                A, C = boxes[a], boxes[c]
                ox = min(A['x'] + A['cw'], C['x'] + C['cw']) - max(A['x'], C['x'])
                oy = min(A['y'] + A['ch'] * .8, C['y'] + C['ch'] * .8) - max(A['y'], C['y'])
                if ox > 4 and oy > 4:
                    layout_issues.append(f'slide {i + 1}: overlap {A["t"]!r} / {C["t"]!r}')
        pg.screenshot(path=str(PREV / f'slide-{i + 1:02d}.jpg'), type='jpeg', quality=85)
    # navigation semantics: closing slide does not run into the appendix
    main = sum(1 for s in slides if s['duration'])
    pg.evaluate(f'deck.go({main - 1}, true, true)')
    pg.keyboard.press('ArrowRight')
    report['checks']['closing_stops_before_appendix'] = pg.evaluate('deck.state.cur') == main - 1
    pg.keyboard.press('r')
    report['checks']['appendix_key_opens_appendix'] = pg.evaluate('deck.state.cur') == main
    for vw, vh in ((1280, 720), (1920, 1080), (1024, 768), (390, 844)):
        pg.set_viewport_size({'width': vw, 'height': vh})
        pg.wait_for_timeout(50)
        r = pg.evaluate("document.getElementById('stage').getBoundingClientRect().toJSON()")
        ok = r['left'] >= -1 and r['top'] >= -1 and r['right'] <= vw + 1 and r['bottom'] <= vh + 1
        report['checks'][f'fits_{vw}x{vh}'] = ok
    pg.set_viewport_size({'width': 1600, 'height': 900})
    pdf = b.new_page(viewport={'width': 1600, 'height': 900})
    pdf.goto((ROOT / 'three-years.html').as_uri() + '?still')
    pdf.wait_for_function('window.deck !== undefined')
    pdf.evaluate('deck.revealAll()')
    pdf.wait_for_timeout(300)
    pdf.pdf(path=str(ROOT / 'three-years.pdf'), width='1600px', height='900px', print_background=True)
    b.close()

report['checks']['console_errors'] = errors
report['checks']['layout_issues'] = layout_issues
report['checks']['reveal_groups_per_slide'] = step_counts
report['checks']['reveal_groups_total'] = sum(step_counts)

# PPTX package checks
for name in ('three-years.pptx', 'three-years-static.pptx'):
    z = zipfile.ZipFile(ROOT / name)
    sl = sorted(n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml'))
    timing = gifs = hidden = 0
    bad_targets = []
    for n in sl:
        x = etree.fromstring(z.read(n))
        ids = {e.get('id') for e in x.iter('{*}cNvPr')}
        if x.get('show') == '0':
            hidden += 1
        t = x.find('{*}timing')
        if t is not None:
            timing += 1
            for tg in t.iter('{*}spTgt'):
                if tg.get('spid') not in ids:
                    bad_targets.append((n, tg.get('spid')))
    media = [n for n in z.namelist() if n.startswith('ppt/media/')]
    gifs = [n for n in media if n.endswith('.gif')]
    multi = 0
    for g in gifs:
        with z.open(g) as fh:
            im = Image.open(fh)
            multi += getattr(im, 'n_frames', 1) > 1
    report['checks'][name] = dict(slides=len(sl), hidden=hidden, slides_with_timing=timing,
                                  animation_targets_missing=bad_targets, gif_media=len(gifs),
                                  multiframe_gifs=multi, size_mb=round((ROOT / name).stat().st_size / 1e6, 1))

# contact sheet
ims = [Image.open(PREV / f'slide-{i + 1:02d}.jpg').resize((400, 225)) for i in range(len(slides))]
cols = 4
sheet = Image.new('RGB', (cols * 400 + (cols + 1) * 8, ((len(ims) + cols - 1) // cols) * 233 + 8), (20, 20, 20))
for k, im in enumerate(ims):
    sheet.paste(im, (8 + (k % cols) * 408, 8 + (k // cols) * 233))
sheet.save(PREV / 'contact-sheet.jpg', quality=88)
(ROOT / 'render-validation.json').write_text(json.dumps(report, indent=1) + '\n')
print(json.dumps({k: v for k, v in report['checks'].items() if k != 'reveal_groups_per_slide'}, indent=1))
