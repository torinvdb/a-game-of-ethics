"""Render content.json to the animated PPTX, static PPTX and offline HTML deck.

Scene coordinates are 1600x900 (100 units = 1 inch). Layers per slide: background
JPEG, motion GIF/PNG at fixed regions, then editable native text and shapes.
"""
from __future__ import annotations

import base64
import html
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

from motion import MOTIONS, EXTRA
from pptx_motion import add_timeline

ROOT = Path(__file__).parent
TITLE = 'Three Years in Thirty Minutes: Time-Travel Ethics Evaluation for AI Agents'
SPEAKERS = 'Torin van den Bulk · Vicente Herrera'
EVENT = 'CNCF-Hosted Co-located Events North America 2026'

BG = '070D10'; FG = 'E8ECD6'; MUTED = 'A3B8AE'; DIM = '5E7470'
TEAL = '40C4B2'; CYAN = '6EECFF'; AMBER = 'FFB052'; RED = 'FF5A48'; MAGENTA = 'FF4FA8'; PANEL = '0B1418'
COLORS = {'TEAL': TEAL, 'CYAN': CYAN, 'AMBER': AMBER, 'RED': RED, 'MAGENTA': MAGENTA}

FACES = {  # face -> (font file for measuring, PowerPoint family, bold, css family)
    'display': ('Oswald-Bold.ttf', 'Oswald', True, 'Oswald'),
    'body': ('Rajdhani-SemiBold.ttf', 'Rajdhani SemiBold', False, 'Rajdhani'),
    'mono': ('ShareTechMono-Regular.ttf', 'Share Tech Mono', False, 'ShareTechMono'),
}
LEADING = {'display': 1.06, 'body': 1.16, 'mono': 1.2}
CHAPTERS = ['00', '01', '02', '03', '04', '05', '06', '07', '08']
MIN_SIZE = 20  # scene px; ~14.4 pt. Only footer references go this small.


def measure(face, size):
    return ImageFont.truetype(str(ROOT / 'assets/fonts' / FACES[face][0]), int(size))


def wrap(text, size, width, face):
    f = measure(face, size)
    out = []
    for para in text.split('\n'):
        cur = ''
        for word in para.split():
            cand = (cur + ' ' + word).strip()
            if cur and f.getlength(cand) > width:
                out.append(cur)
                cur = word
            else:
                cur = cand
        out.append(cur)
    return '\n'.join(out)


class Scene:
    def __init__(self, slide, index, total_main):
        self.slide, self.index, self.total = slide, index, total_main
        self.el = []

    def add(self, typ, g=0, anim='fade', delay=0, **kw):
        self.el.append(dict(type=typ, group=g, anim=anim, delay=delay, **kw))
        return self.el[-1]

    def rect(self, x, y, w, h, color=PANEL, alpha=0.82, line=None, lw=1.2, g=0, anim='fade', delay=0, shape='rect'):
        return self.add('rect', g, anim, delay, x=x, y=y, w=w, h=h, color=color, alpha=alpha, line=line, lw=lw, shape=shape)

    def line(self, x, y, w, h=0, color=TEAL, thick=2, g=0, anim='fade', delay=0):
        return self.add('line', g, anim, delay, x=x, y=y, w=w, h=h, color=color, thick=thick)

    def text(self, x, y, w, text, size=28, color=FG, face='body', g=0, anim='fade', delay=0, upper=False, align='l',
             track=0):
        assert size >= MIN_SIZE or face == 'mono', (self.slide['id'], text, size)
        if upper:
            text = text.upper()
        text = wrap(text, size, w, face)
        n = len(text.split('\n'))
        h = n * size * LEADING[face] + size * 0.25
        return self.add('text', g, anim, delay, x=x, y=y, w=w, h=h, text=text, size=size, color=color, face=face,
                        align=align)

    def image(self, x, y, w, h, file, motion=False, g=0, anim='fade', delay=0, alt=''):
        return self.add('image', g, anim, delay, x=x, y=y, w=w, h=h, file=file, motion=motion, alt=alt)

    def video(self, x, y, w, h, file, poster, alt=''):
        """An embedded video (PPTX: native movie; HTML: <video> linked by relative path)."""
        return self.add('video', 0, 'fade', 0, x=x, y=y, w=w, h=h, file=file, poster=poster, alt=alt)

    def motion(self, name, g=0, anim='fade', delay=0):
        x, y, w, h = MOTIONS[name]['region']
        animated = MOTIONS[name]['frames'] > 1
        file = f'assets/motion/{name}.gif' if animated else f'assets/motion/{name}.png'
        return self.image(x, y, w, h, file, motion=animated, g=g, anim=anim, delay=delay,
                          alt='Code-drawn illustrative animation; not measured data')

    def path(self, x, y, d, dx, dur, g, color=CYAN):
        """A small light that travels dx scene units and repeats (native motion path)."""
        return self.add('dot', g, 'path', 0, x=x, y=y, w=d, h=d, color=color, dx=dx, dur=dur)


# ------------------------------------------------------------------ chrome

def chrome(s: Scene):
    sl, i = s.slide, s.index
    appendix = sl['kind'] == 'appendix' or i >= s.total
    s.image(0, 0, 1600, 900, f"assets/backgrounds/{sl['id']}.jpg", alt='Code-drawn cyberpunk scenery')
    # registration frame
    s.line(48, 40, 1504, color='2A3C3C', thick=1)
    s.line(48, 848, 1504, color='2A3C3C', thick=1)
    for x, y, dx, dy in ((48, 40, 22, 0), (48, 40, 0, 22), (1552, 40, -22, 0), (1552, 40, 0, 22),
                         (48, 848, 22, 0), (48, 848, 0, -22), (1552, 848, -22, 0), (1552, 848, 0, -22)):
        s.line(x, y, dx, dy, color=TEAL, thick=2)
    tag = f"{sl['chapter']}  {sl['kanji']}  /  {sl['section']}"
    s.text(80, 52, 900, tag, 20, TEAL, 'mono', anim='flicker')
    page = f'{i + 1:02d} / {s.total}' if not appendix else f"{sl['chapter']} / APPENDIX"
    s.text(1340, 52, 180, page, 20, MUTED, 'mono', align='r')
    # speaker names and source refs live in the speaker notes, not on the slide
    # chapter rail
    if not appendix:
        s.line(80, 870, 1440, color='24393A', thick=2)
        cur = CHAPTERS.index(sl['chapter']) if sl['chapter'] in CHAPTERS else 0
        for k, ch in enumerate(CHAPTERS):
            x = 80 + 1440 * k / (len(CHAPTERS) - 1)
            on = k <= cur
            s.rect(x - 4, 866, 8, 8, AMBER if k == cur else (TEAL if on else '2C4444'), 1.0)
        s.line(80, 870, 1440 * cur / (len(CHAPTERS) - 1), color=TEAL, thick=2)


def title_block(s: Scene, w=1400, size=74):
    sl = s.slide
    t = s.text(104, 96, w, sl['title'], size, FG, 'display', anim='wipe', upper=True)
    s.rect(80, 104, 8, t['h'] - size * 0.32, RED, 1.0, anim='wipe')
    y = t['y'] + t['h'] + 6
    if sl.get('subtitle'):
        sub = s.text(106, y, w, sl['subtitle'], 28, MUTED, 'body', delay=250)
        y = sub['y'] + sub['h']
    return y


def col(c):
    return COLORS.get(c, c)


# ------------------------------------------------------------------ layouts

def layout(s: Scene):
    sl = s.slide
    kind = sl['kind']
    items = sl.get('items', [])
    chrome(s)
    if kind in ('hero', 'closing'):
        s.motion(sl['motion'])
        size = 124 if kind == 'hero' else 112
        t = s.text(96, 210, 980, sl['title'], size, FG, 'display', anim='wipe', upper=True)
        s.rect(72, 222, 10, t['h'] - 40, RED, 1.0, anim='wipe')
        y = t['y'] + t['h'] + 10
        sub = s.text(100, y, 920, sl['subtitle'], 36, FG, 'body', delay=300)
        y = sub['y'] + sub['h'] + 34
        if kind == 'hero':
            s.text(100, y, 920, SPEAKERS, 32, TEAL, 'body', delay=600)
            s.text(100, y + 50, 920, EVENT, 21, MUTED, 'mono', delay=700)
        else:
            s.text(100, y, 920, sl['takeaway'], 32, TEAL, 'body', delay=500)
            y0 = y + 62
            # two scan targets, visible without a click: the project and ControlPlane
            s.image(100, y0, 150, 150, 'assets/qr-repo.png', delay=700, alt='QR code: github.com/torinvdb/a-game-of-ethics')
            s.text(266, y0 + 14, 300, 'A Game of Ethics', 26, TEAL, 'display', delay=700, upper=True)
            s.text(266, y0 + 60, 300, 'github.com/torinvdb/\na-game-of-ethics', 20, AMBER, 'mono', delay=700)
            s.image(600, y0, 150, 150, 'assets/qr-controlplane.png', delay=900, alt='QR code: control-plane.io')
            s.image(766, y0 + 18, 220, round(220 * 391 / 1778), 'assets/logos/controlplane.png', delay=900,
                    alt='ControlPlane logo')
            s.text(766, y0 + 84, 230, 'control-plane.io', 20, AMBER, 'mono', delay=900)
        return
    if kind == 'appendix':
        title_block(s, size=60)
        for j, (a, b) in enumerate(items):
            y = 370 + j * 100
            s.text(104, y, 300, a, 26, AMBER if j == len(items) - 1 else TEAL, 'display', upper=True)
            s.text(430, y + 2, 1080, b, 25, FG)
            s.line(104, y + 86, 1410, color='24393A', thick=1)
        if sl.get('takeaway'):
            s.text(104, 780, 1400, sl['takeaway'], 18, MUTED, 'mono')
        return

    if kind == 'incident':
        title_block(s)
        s.motion(sl['motion'])
        for j, (a, b) in enumerate(items):
            y = 400 + j * 92
            g = 0 if j == 0 else 1
            c = RED if a == 'DENY' else AMBER
            s.text(104, y, 210, a, 50, c, 'mono', g=g, delay=j * 200)
            s.text(330, y + 12, 500, b, 26, FG, g=g, delay=j * 200)
        s.rect(104, 676, 720, 58, '14080F', 0.9, line=MAGENTA, g=2, anim='flicker')
        s.text(124, 692, 690, sl['pressure'], 22, MAGENTA, 'mono', g=2, anim='flicker')
        s.text(104, 758, 1400, sl['takeaway'], 34, TEAL, 'display', g=3, anim='wipe', upper=True)
    elif kind == 'doors':
        title_block(s)
        names = [sl['motion']] + EXTRA['doors']
        for j, (a, b, c, *lvl) in enumerate(items):
            x, y, w, h = MOTIONS[names[j]]['region']
            g = j + 1
            s.motion(names[j], g=g, anim='flicker')
            s.rect(x, 520, w, 220, PANEL, 0.86, line=col(c), g=g)
            s.text(x + 20, 536, w - 40, a, 28, col(c), 'display', g=g, upper=True)
            s.text(x + 20, 580, w - 40, b, 24, FG, g=g, delay=150)
            if lvl:
                s.text(x + 20, 690, w - 40, lvl[0], 20, col(c), 'mono', g=g, delay=300, upper=True)
        s.text(104, 768, 1400, sl['takeaway'], 30, TEAL, 'display', g=4, delay=700, anim='wipe', upper=True)
    elif kind == 'impacts':
        title_block(s)
        names = EXTRA['people']
        for j, (a, b, c) in enumerate(items):
            x = 80 if j == 0 else 835
            g = j + 1
            s.rect(x, 400, 685, 250, PANEL, 0.86, line=col(c), g=g)
            s.motion(names[j], g=g, anim='flicker')
            s.text(x + 320, 420, 350, a, 32, col(c), 'display', g=g, upper=True)
            s.text(x + 24, 528, 640, b, 26, FG, g=g, delay=150)
        for k, fac in enumerate(sl['factors']):
            x = 80 + k * 288
            s.rect(x, 676, 264, 54, '0E1C1E', 0.9, line=TEAL, g=3, delay=k * 90)
            s.text(x, 688, 264, fac, 24, TEAL, 'mono', g=3, delay=k * 90, align='c')
        s.text(104, 758, 1400, sl['takeaway'], 32, AMBER, 'display', g=3, delay=700, anim='wipe', upper=True)
    elif kind == 'branches':
        title_block(s)
        s.motion(sl['motion'])
        for j, (a, b, c) in enumerate(items):
            y = 380 + (70 + j * 105) / 1.2 - 30
            s.text(104, y, 300, a, 28, col(c), 'display', g=j + 1, upper=True)
            s.text(104, y + 36, 300, b, 22, FG, g=j + 1)
        s.text(104, 760, 1400, sl['takeaway'], 32, TEAL, 'display', g=4, anim='wipe', upper=True)
    elif kind == 'clocks':
        title_block(s)
        s.motion(sl['motion'])
        for j, (a, b) in enumerate(items):
            y = 400 + j * 112
            s.text(104, y, 330, a, 30, [TEAL, AMBER, CYAN][j], 'display',
                   g=j + 1, upper=True)
            s.text(104, y + 42, 720, b, 26, FG, g=j + 1)
        s.text(104, 760, 1400, sl['takeaway'], 32, AMBER, 'display', g=4, anim='wipe', upper=True)
    elif kind == 'research':
        title_block(s)
        for j, (a, b, c) in enumerate(items):
            y = 392 + j * 118
            g = j + 1
            s.line(104, y - 12, 1410, color='24393A', thick=1, g=g)
            s.text(104, y, 320, a, 27, TEAL, 'display', g=g, upper=True)
            s.text(440, y, 720, b, 26, FG, g=g)
            s.text(1190, y, 330, c, 24, AMBER, g=g, delay=300)
        s.text(104, 766, 1400, sl['takeaway'], 28, TEAL, 'display', g=3, delay=900, anim='wipe', upper=True)
    elif kind == 'boundary':
        title_block(s, w=960, size=66)
        s.motion(sl['motion'])
        for j, (a, b, c) in enumerate(items):
            x = 80 + j * 370
            g = j + 1
            s.rect(x, 420, 330, 170, PANEL, 0.88, line=col(c), g=g)
            s.text(x + 18, 436, 296, a, 27, col(c), 'display', g=g, upper=True)
            s.text(x + 18, 482, 296, b, 24, FG, g=g, delay=150)
            if j:
                s.line(x - 40, 505, 40, color=TEAL, thick=3, g=g, anim='wipe')
        s.path(403, 498, 14, 1110, 3200, g=4)
        s.text(104, 650, 1400, sl['takeaway'], 32, AMBER, 'display', g=4, delay=600, anim='wipe', upper=True)
    elif kind == 'demo':
        title_block(s, w=1380)
        s.motion(sl['motion'])
        for j, (a, b, *rest) in enumerate(items):
            if rest:  # numbered step: label + one plain line
                y = 372 + j * 116
                s.rect(104, y, 50, 50, '0E1C1E', 0.95, line=AMBER, delay=j * 120)
                s.text(104, y + 9, 50, a, 28, AMBER, 'mono', align='c', delay=j * 120)
                s.text(176, y - 2, 540, b, 30, AMBER, 'display', delay=j * 120, upper=True)
                s.text(176, y + 40, 540, rest[0], 24, FG, delay=j * 120 + 100)
            else:
                y = 360 + j * 74
                s.rect(104, y, 46, 46, '0E1C1E', 0.95, line=AMBER, delay=j * 120)
                s.text(104, y + 8, 46, a, 26, AMBER, 'mono', align='c', delay=j * 120)
                s.text(170, y + 6, 540, b, 25, FG, delay=j * 120)
        s.text(104, 760, 1400, sl['takeaway'], 24, AMBER, 'mono')
    elif kind == 'results':
        appendix = s.index >= s.total
        title_block(s, size=60 if appendix else 74)
        xs = [104, 560, 760, 970, 1330]
        ws = [440, 180, 200, 340, 180]
        top = 360 if appendix else 392
        for x, w, txt in zip(xs, ws, sl['columns']):
            s.text(x, top, w, txt, 18, MUTED, 'mono')
        dense = appendix or len(items) > 5
        step = 52 if dense else 70
        size = 26 if dense else 30
        plain = sl.get('plain', False)  # numeric tables: no red/amber flags on columns 2 and 4
        for j, row in enumerate(items):
            y = top + 40 + j * step
            g = 0 if appendix else j + 1
            bad = row[2] not in ('0',) and not plain
            s.line(104, y - 10, 1400, color='24393A', thick=1, g=g)
            s.text(xs[0], y, ws[0], row[0], size - 2, FG, 'display', g=g, upper=True)
            for k in range(1, 5):
                c = RED if (k == 2 and bad) else (AMBER if (k == 4 and row[4] != '0' and not plain) else TEAL)
                s.text(xs[k], y, ws[k], row[k], size, c, 'mono', g=g)
        s.text(104, 770, 1400, sl['takeaway'], 26 if not appendix else 22, AMBER, 'body', g=0 if appendix else len(items),
               delay=400)
    elif kind == 'fairness':
        title_block(s)
        s.motion(sl['motion'])
        for j, (a, b, c) in enumerate(items):
            y = 410 + j * 150
            s.rect(104, y, 8, 110, col(c), 1.0, g=j + 1)
            s.text(130, y, 680, a, 30, col(c), 'display', g=j + 1, upper=True)
            s.text(130, y + 46, 680, b, 32, FG, g=j + 1)
        s.text(104, 764, 1400, sl['takeaway'], 30, TEAL, 'display', g=2, delay=900, anim='wipe', upper=True)
    elif kind == 'ledgers':
        title_block(s, w=960, size=66)
        s.motion(sl['motion'])
        for j, (a, b, tag, c) in enumerate(items):
            x = 80 + j * 370
            g = j + 1
            s.rect(x, 410, 330, 260, PANEL, 0.88, line=col(c), g=g)
            s.text(x + 18, 426, 296, a, 30, col(c), 'display', g=g, upper=True)
            s.text(x + 18, 474, 296, tag, 20, MUTED, 'mono', g=g, upper=True)
            s.text(x + 18, 512, 296, b, 25, FG, g=g, delay=150)
        s.text(104, 712, 1400, sl['takeaway'], 30, AMBER, 'display', g=4, delay=600, anim='wipe', upper=True)
    elif kind == 'stack':
        title_block(s)
        for j, (a, b, c) in enumerate(items):
            x = 80 + j * 490
            g = j + 1
            s.rect(x, 400, 450, 230, PANEL, 0.88, line=col(c), g=g)
            s.text(x + 22, 418, 410, a, 32, col(c), 'display', g=g, upper=True)
            s.text(x + 22, 472, 410, b, 26, FG, g=g, delay=150)
        s.text(104, 664, 1400, sl['status'], 22, AMBER, 'mono', g=3, delay=400)
        s.text(104, 730, 1400, sl['takeaway'], 30, TEAL, 'display', g=3, delay=800, anim='wipe', upper=True)
    elif kind == 'cards':
        # 2x2 grid: tag · headline · one line of detail; one card per click
        title_block(s)
        for j, (tag, head, detail, c) in enumerate(items):
            x, y = 80 + (j % 2) * 730, 360 + (j // 2) * 196
            g = j + 1
            s.rect(x, y, 700, 180, PANEL, 0.9, line=col(c), g=g)
            s.text(x + 22, y + 16, 656, tag, 20, col(c), 'mono', g=g, upper=True)
            s.text(x + 22, y + 48, 656, head, 30, FG, 'display', g=g, upper=True)
            s.text(x + 22, y + 98, 656, detail, 24, FG, g=g, delay=150)
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=len(items), delay=600, anim='wipe', upper=True)
    elif kind == 'compare':
        # two panels: what it is (left) vs what we build around it (right)
        title_block(s)
        n = len(items)
        gap = 80 if n == 2 else 24
        pw = (1440 - gap * (n - 1)) / n
        size = 25 if n == 2 else 22
        for j, (label, sub, lines, c) in enumerate(items):
            x = 80 + j * (pw + gap)
            g = j + 1
            s.rect(x, 356, pw, 384, PANEL, 0.9, line=col(c), g=g)
            s.text(x + 24, 374, pw - 48, label, 30 if n > 2 else 32, col(c), 'display', g=g, upper=True)
            s.text(x + 24, 420, pw - 48, sub, 20, MUTED, 'mono', g=g, upper=True)
            for k, ln in enumerate(lines):
                s.text(x + 24, 464 + k * 66, pw - 48, ln, size, FG, g=g, delay=350 * (k + 1))
            if j:
                s.line(x - gap + 4, 548, gap - 8, color=TEAL, thick=3, g=g, anim='wipe')
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=n, delay=1600, anim='wipe', upper=True)
    elif kind == 'ladder':
        # rising steps A0..A5; colour marks the risk band
        title_block(s)
        n = len(items)
        step = (1440 + 16) / n
        for j, (lvl, name, desc, c) in enumerate(items):
            x, w = 80 + j * step, step - 16
            top = 560 - j * (200 / (n - 1))
            g = 1 if j < 3 else 2
            s.rect(x, top, w, 740 - top, PANEL, 0.9, line=col(c), g=g, delay=j * 90)
            s.text(x + 14, top + 12, w - 28, lvl, 36, col(c), 'display', g=g, delay=j * 90)
            s.text(x + 14, top + 60, w - 28, name, 22, col(c), 'display', g=g, delay=j * 90, upper=True)
            s.text(x + 14, top + 94, w - 28, desc, 21, FG, g=g, delay=j * 90 + 100)
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=3, delay=300, anim='wipe', upper=True)
    elif kind == 'rings':
        # concentric bounds on the right (core first), one row per ring on the left; a final row is the gate
        title_block(s)
        cx, cy = 1230, 540
        rings = [it for it in items if it[3] != 'GATE']
        radii = [round(58 + k * (210 - 58) / max(1, len(rings) - 1)) for k in range(len(rings))]
        for j in reversed(range(len(rings))):
            r, c = radii[j], rings[j][2]
            s.rect(cx - r, cy - r, 2 * r, 2 * r, PANEL, 0.55, line=col(c), shape='oval', g=j + 1)
            s.text(cx - 90, cy - r + (10 if j else r - 16), 180, rings[j][0], 20, col(c), 'mono', g=j + 1,
                   align='c', upper=True)
        for j, (label, text, c, *_) in enumerate(items):
            y = 360 + j * 80
            g = j + 1
            s.text(104, y, 240, label, 26, AMBER if c == 'GATE' else col(c), 'display', g=g, upper=True)
            s.text(350, y + 2, 600, text, 23, FG, g=g)
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=len(items), delay=600, anim='wipe', upper=True)
    elif kind == 'cascade':
        # one row per choice; cells cascade left to right: tonight -> next month -> month 36
        title_block(s)
        heads = sl.get('columns', ['TONIGHT', 'NEXT MONTH', 'BY MONTH 36'])
        xs, cw = [400, 780, 1160], 352
        for k, h in enumerate(heads):
            s.text(xs[k], 338, cw, h, 20, MUTED, 'mono', upper=True)
        for j, (label, c, *cells) in enumerate(items):
            y = 372 + j * 96
            g = j + 1
            s.text(104, y + 18, 280, label, 26, col(c), 'display', g=g, upper=True)
            for k, cell in enumerate(cells):
                x = xs[k]
                s.rect(x, y, cw, 82, PANEL, 0.9, line=col(c), g=g, delay=k * 450)
                s.text(x + 16, y + 10, cw - 32, cell, 22, FG, g=g, delay=k * 450 + 100)
                if k:
                    s.line(x - 28, y + 41, 24, color=col(c), thick=3, g=g, delay=k * 450, anim='wipe')
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=len(items), delay=1400, anim='wipe', upper=True)
    elif kind == 'video':
        # static title + a large embedded recording; no reveals, so the movie keeps its own play control
        s.text(104, 92, 1400, sl['title'], 54, FG, 'display', upper=True)
        s.text(106, 160, 1400, sl['subtitle'], 24, MUTED)
        s.rect(276, 206, 1048, 590, '000000', 1.0, line=TEAL)
        s.video(280, 210, 1040, 585, sl['video'], sl['poster'], alt=sl.get('alt', ''))
        # scan targets in the margins while the recording plays during Q&A
        s.image(98, 300, 160, 160, 'assets/qr-repo.png', alt='QR code: github.com/torinvdb/a-game-of-ethics')
        s.text(84, 470, 190, 'A Game of Ethics', 22, TEAL, 'display', upper=True, align='c')
        s.image(1342, 300, 160, 160, 'assets/qr-controlplane.png', alt='QR code: control-plane.io')
        s.image(1336, 474, 172, round(172 * 391 / 1778), 'assets/logos/controlplane.png', alt='ControlPlane logo')
        s.text(104, 806, 1400, sl['takeaway'], 20, AMBER, 'mono')
    elif kind == 'stats':
        # three big-number callouts, then a strip of per-model "where the cost went" chips
        title_block(s)
        for j, (num, label, detail, c) in enumerate(items):
            x = 80 + j * 490
            g = j + 1
            s.rect(x, 352, 450, 262, PANEL, 0.9, line=col(c), g=g)
            s.text(x + 24, 362, 402, num, 92, col(c), 'display', g=g)
            s.text(x + 24, 478, 402, label, 28, FG, 'display', g=g, upper=True)
            s.text(x + 24, 522, 402, detail, 22, FG, g=g, delay=150)
        sig = sl.get('signatures', [])
        if sig:
            g = len(items) + 1
            s.text(104, 640, 1000, 'WHERE THE COST WENT', 20, MUTED, 'mono', g=g)
            w = (1440 - (len(sig) - 1) * 12) / len(sig)
            for k, (model, where, c) in enumerate(sig):
                x = 80 + k * (w + 12)
                s.rect(x, 672, w, 64, PANEL, 0.9, line=col(c), g=g, delay=k * 80)
                s.text(x + 12, 678, w - 24, model, 20, FG, 'mono', g=g, delay=k * 80)
                s.text(x + 12, 704, w - 24, where, 20, col(c), 'mono', g=g, delay=k * 80, upper=True)
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=len(items) + (1 if sig else 0),
               delay=600, anim='wipe', upper=True)
    elif kind == 'takeaways':
        # numbered key takeaways: numeral · headline · one line
        title_block(s)
        for j, (head, line) in enumerate(items):
            y = 348 + j * 82
            g = j + 1
            s.line(104, y - 12, 1410, color='24393A', thick=1, g=g)
            s.text(104, y - 4, 80, f'{j + 1:02d}', 40, AMBER, 'display', g=g)
            s.text(196, y, 560, head, 32, FG, 'display', g=g, upper=True)
            s.text(780, y + 4, 740, line, 24, FG, g=g, delay=150)
        s.text(104, 772, 1400, sl['takeaway'], 30, TEAL, 'display', g=len(items), delay=700, anim='wipe', upper=True)
    elif kind == 'findings':
        # label · claim · evidence, one row per click; up to five rows
        title_block(s)
        n = len(items)
        step = 78 if n >= 5 else 96
        for j, (a, b, c) in enumerate(items):
            y = 376 + j * step
            g = j + 1
            s.line(104, y - 10, 1410, color='24393A', thick=1, g=g)
            s.text(104, y, 290, a, 26, TEAL, 'display', g=g, upper=True)
            s.text(410, y, 720, b, 24, FG, g=g)
            s.text(1150, y + 2, 370, c, 20, AMBER, 'mono', g=g, delay=250)
        s.text(104, 772, 1400, sl['takeaway'], 28, AMBER, 'display', g=n, delay=700, anim='wipe', upper=True)
    elif kind == 'checklist':
        title_block(s)
        for j, (a, b) in enumerate(items):
            y = 384 + j * 72
            g = j + 1
            s.text(104, y, 260, a, 30, TEAL, 'display', g=g, upper=True)
            s.text(380, y + 2, 1120, b, 30, FG, g=g)
            s.line(104, y + 60, 1410, color='24393A', thick=1, g=g)
        s.text(104, 760, 1400, sl['takeaway'], 32, AMBER, 'display', g=5, anim='wipe', upper=True)
    else:
        raise ValueError(kind)


# ------------------------------------------------------------------ PPTX

FONT_FAMILY = {k: v[1] for k, v in FACES.items()}


def set_alpha(shape, color, alpha):
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor.from_string(color)
    if alpha < 1:
        clr = shape.fill._xPr.solidFill.srgbClr
        a = OxmlElement('a:alpha')
        a.set('val', str(int(alpha * 100000)))
        clr.append(a)


def glow_text(run_font, color):
    """Subtle neon glow on display text (DrawingML a:effectLst/a:glow)."""
    rPr = run_font._rPr
    eff = OxmlElement('a:effectLst')
    g = OxmlElement('a:glow')
    g.set('rad', '63500')
    clr = OxmlElement('a:srgbClr')
    clr.set('val', color)
    a = OxmlElement('a:alpha')
    a.set('val', '35000')
    clr.append(a)
    g.append(clr)
    eff.append(g)
    # CT_TextCharacterProperties order: ln, fill, effectLst, ..., latin
    fill = rPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill')
    fill.addnext(eff)


def merge_video_timing(slide):
    """python-pptx puts a movie's <p:video> in its own <p:timing>; a slide may have only one, after the
    transition. Move video nodes into the animation timeline (if any) and keep a single timing last."""
    sld = slide._element
    vids = sld.findall('.//' + qn('p:video'))
    if not vids:
        return
    timings = sld.findall(qn('p:timing'))
    main = next((t for t in timings if t.find('.//' + qn('p:seq')) is not None), None)
    if main is not None:
        root_ctl = main.find(qn('p:tnLst')).find(qn('p:par')).find(qn('p:cTn')).find(qn('p:childTnLst'))
        for v in vids:
            root_ctl.append(v)
        for t in timings:
            if t is not main:
                sld.remove(t)
        timings = [main]
    for t in timings:  # schema order: ... transition, timing
        sld.remove(t)
        sld.append(t)


def cue_cards(slides):
    """Presenter cue card per slide: speaker, length, target clock time, one line per click."""
    out, cum = {}, 0
    for i, s in enumerate(slides):
        if not s['duration']:
            continue
        cum += s['duration']
        head = f"{i + 1:02d} · {s.get('speaker') or ''} · {s['duration']} s · finish by {cum // 60}:{cum % 60:02d}"
        out[s['id']] = head + ''.join(f"\n• {c}" for c in s.get('cues', []))
    return out


def to_pptx(slides, scenes, animated, path):
    cues = cue_cards(slides)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(16), Inches(9)
    cp = prs.core_properties
    cp.author = cp.last_modified_by = 'Torin van den Bulk'
    cp.title = TITLE
    cp.subject = f'{sum(1 for s in slides if s["duration"])}-slide main talk with hidden appendices'
    cp.comments = 'Procedural code-drawn scenery and motion; see assets/ASSET-LEDGER.md.'
    cp.created = cp.modified = datetime(2026, 11, 6, tzinfo=timezone.utc)
    for i, (content, sc) in enumerate(zip(slides, scenes)):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = RGBColor.from_string(BG)
        if not content['duration']:
            slide._element.set('show', '0')
        steps = defaultdict(list)
        for e in sc.el:
            X, Y, Wd, Ht = [Inches(e[k] / 100) for k in ('x', 'y', 'w', 'h')]
            if e['type'] == 'text':
                shp = slide.shapes.add_textbox(X, Y, Wd, Inches(e['h'] / 100))
                tf = shp.text_frame
                tf.word_wrap = False
                tf.auto_size = MSO_AUTO_SIZE.NONE
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                for j, ln in enumerate(e['text'].split('\n')):
                    p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                    p.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[e['align']]
                    r = p.add_run()
                    r.text = ln
                    f = r.font
                    f.name = FONT_FAMILY[e['face']]
                    f.size = Pt(e['size'] * 0.72)
                    f.bold = FACES[e['face']][2]
                    f.color.rgb = RGBColor.from_string(e['color'])
                    p.line_spacing = LEADING[e['face']]
                    if e['face'] == 'display' and e['size'] >= 28 and e['color'] != FG:
                        glow_text(f, e['color'])
            elif e['type'] in ('rect', 'dot'):
                kind = MSO_SHAPE.OVAL if e.get('shape') == 'oval' or e['type'] == 'dot' else MSO_SHAPE.RECTANGLE
                shp = slide.shapes.add_shape(kind, X, Y, Wd, Ht)
                set_alpha(shp, e['color'], e.get('alpha', 1.0))
                if e.get('line'):
                    shp.line.color.rgb = RGBColor.from_string(e['line'])
                    shp.line.width = Pt(e['lw'])
                else:
                    shp.line.fill.background()
                shp.shadow.inherit = False
            elif e['type'] == 'line':
                shp = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, X, Y, X + Wd, Y + Ht)
                shp.line.color.rgb = RGBColor.from_string(e['color'])
                shp.line.width = Pt(e['thick'] * 0.72)
            elif e['type'] == 'video':
                if animated:
                    shp = slide.shapes.add_movie(str(ROOT / e['file']), X, Y, Wd, Ht,
                                                 poster_frame_image=str(ROOT / e['poster']), mime_type='video/mp4')
                else:  # the static deck carries stills only
                    shp = slide.shapes.add_picture(str(ROOT / e['poster']), X, Y, Wd, Ht)
                shp._element.nvPicPr.cNvPr.set('descr', e.get('alt', ''))
            else:
                file = ROOT / e['file']
                if e['motion'] and not animated:
                    file = file.with_suffix('.png')
                shp = slide.shapes.add_picture(str(file), X, Y, Wd, Ht)
                shp._element.nvPicPr.cNvPr.set('descr', e.get('alt', ''))
            if animated:
                key = ('auto', 0) if e['group'] == 0 else ('click', e['group'])
                if e['type'] == 'image' and e['file'].startswith('assets/backgrounds'):
                    continue
                if e['group'] == 0 and e['anim'] == 'fade' and e['delay'] == 0 and e['type'] != 'dot':
                    continue  # chrome that is simply present
                if e['anim'] == 'path':  # reveal the light, then send it along its path
                    steps[key].append(dict(id=shp.shape_id, anim='fade', delay=e['delay']))
                steps[key].append(dict(id=shp.shape_id, anim=e['anim'], delay=e['delay'], dx=e.get('dx', 0),
                                       dur=e.get('dur', 0)))
        transition = OxmlElement('p:transition')
        transition.set('spd', 'med')
        transition.append(OxmlElement('p:fade'))
        slide._element.append(transition)
        if animated:
            ordered = [steps[('auto', 0)]] if steps.get(('auto', 0)) else []
            auto = bool(ordered)
            ordered += [steps[k] for k in sorted(k for k in steps if k[0] == 'click')]
            add_timeline(slide, ordered, first_auto=auto)
        merge_video_timing(slide)
        notes = []
        if content['id'] in cues:
            notes.append('CUE CARD\n' + cues[content['id']])
        if content.get('script'):
            notes.append('FULL SCRIPT\n' + content['script'])
        if content.get('notes'):
            notes.append('NOTES\n' + content['notes'])
        if content.get('refs'):
            notes.append('SOURCES\n' + '; '.join(content['refs']))
        if content['duration']:
            notes.append(f"TIMING {content['duration']} s · SPEAKER {content.get('speaker', '')}")
        notes.append('Visuals are code-drawn scenery/schematics, not data or film frames (assets/ASSET-LEDGER.md).')
        slide.notes_slide.notes_text_frame.text = '\n\n'.join(notes)
    prs.save(path)


# ------------------------------------------------------------------ HTML

def data_uri(path: Path):
    mime = {'.jpg': 'image/jpeg', '.png': 'image/png', '.gif': 'image/gif', '.ttf': 'font/ttf'}[path.suffix]
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()


def to_html(slides, scenes, path):
    assets = {}

    def ref(p):
        key = str(p)
        if key not in assets:
            assets[key] = f'a{len(assets)}'
        return assets[key]

    parts = []
    for i, (content, sc) in enumerate(zip(slides, scenes)):
        bits = []
        for e in sc.el:
            g = e['group']
            cls = f"el {e['type']} anim-{e['anim']}" + (' step' if g else ' auto')
            attrs = f' class="{cls}" data-group="{g}" style="--delay:{e["delay"]}ms;'
            box = f'left:{e["x"]}px;top:{e["y"]}px;width:{e["w"]}px;height:{max(1, e["h"])}px;'
            if e['type'] == 'text':
                face = FACES[e['face']][3]
                glow = e['face'] == 'display' and e['color'] != FG
                st = box + (f'font-family:{face};font-size:{e["size"]}px;line-height:{LEADING[e["face"]]};color:#{e["color"]};'
                            f'text-align:{ {"l": "left", "c": "center", "r": "right"}[e["align"]] };')
                if glow:
                    st += f'text-shadow:0 0 14px #{e["color"]}66;'
                bits.append(f'<div{attrs}{st}">{html.escape(e["text"])}</div>')
            elif e['type'] in ('rect', 'dot'):
                st = box + f'background:#{e["color"]};opacity:{e.get("alpha", 1)};'
                if e.get('line'):
                    st += f'outline:{e["lw"]}px solid #{e["line"]};outline-offset:-{e["lw"]}px;'
                if e.get('shape') == 'oval' or e['type'] == 'dot':
                    st += 'border-radius:50%;'
                if e['type'] == 'dot':
                    st += f'--dx:{e["dx"]}px;--dur:{e["dur"]}ms;box-shadow:0 0 18px #{e["color"]};'
                bits.append(f'<div{attrs}{st}"></div>')
            elif e['type'] == 'line':
                length = math.hypot(e['w'], e['h'])
                ang = math.degrees(math.atan2(e['h'], e['w']))
                st = (f'left:{e["x"]}px;top:{e["y"]}px;width:{max(1, length)}px;height:{e["thick"]}px;'
                      f'background:#{e["color"]};transform:rotate({ang}deg);transform-origin:0 0;')
                bits.append(f'<div{attrs}{st}"></div>')
            elif e['type'] == 'video':
                # linked, not inlined: keeps the HTML small; plays when three-years.html sits next to assets/
                bits.append(f'<video{attrs}{box}object-fit:contain;background:#000;" src="{html.escape(e["file"])}" '
                            f'poster="{data_uri(ROOT / e["poster"])}" controls loop playsinline preload="metadata" '
                            f'aria-label="{html.escape(e.get("alt", ""))}"></video>')
            else:
                f = ROOT / e['file']
                still = ref(f.with_suffix('.png')) if e['motion'] else ref(f)
                bits.append(f'<img{attrs}{box}" data-src="{ref(f)}" data-still="{still}" '
                            f'data-motion="{str(e["motion"]).lower()}" alt="{html.escape(e.get("alt", ""))}">')
        parts.append(f'<section class="slide" data-index="{i}" data-main="{str(bool(content["duration"])).lower()}" '
                     f'aria-label="{html.escape(content["title"].replace(chr(10), " "))}">' + ''.join(bits) + '</section>')
    fonts = ''.join(f'@font-face{{font-family:{v[3]};src:url("{data_uri(ROOT / "assets/fonts" / v[0])}")}}'
                    for v in FACES.values())
    css = fonts + (ROOT / 'deck.css').read_text()
    cues = cue_cards(slides)
    meta = [dict(title=s['title'], speaker=s.get('speaker', ''), duration=s['duration'], cue=cues.get(s['id'], ''),
                 script=s.get('script', ''), notes=s.get('notes', ''), main=bool(s['duration'])) for s in slides]
    js = ('const SLIDES=' + json.dumps(meta).replace('</', '<\\/') + ';const ASSETS=' +
          json.dumps({v: data_uri(Path(k)) for k, v in assets.items()}) + ';' + (ROOT / 'deck.js').read_text())
    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
           '<meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>Three Years in Thirty Minutes</title><style>{css}</style></head><body>'
           '<main id="stage" aria-live="polite">' + ''.join(parts) + '</main>'
           '<aside id="notes" aria-label="Speaker notes"></aside>'
           '<nav id="controls" aria-label="Deck controls">'
           '<button data-act="prev" aria-label="Previous">◀</button><button data-act="next" aria-label="Next">▶</button>'
           '<button data-act="notes">Notes</button><button data-act="motion">Motion</button>'
           '<button data-act="appendix">Appendix</button><button data-act="full">Fullscreen</button>'
           '<span id="clock" aria-label="Elapsed time">00:00</span></nav>'
           f'<script>{js}</script></body></html>')
    path.write_text(doc)


# ------------------------------------------------------------------ entry

def render(root: Path, slides):
    total_main = sum(1 for s in slides if s['duration'])
    scenes = []
    for i, s in enumerate(slides):
        sc = Scene(s, i, total_main)
        layout(sc)
        scenes.append(sc)
    (root / 'scene-layout.json').write_text(json.dumps([sc.el for sc in scenes], indent=1) + '\n')
    to_pptx(slides, scenes, True, root / 'three-years.pptx')
    to_pptx(slides, scenes, False, root / 'three-years-static.pptx')
    to_html(slides, scenes, root / 'three-years.html')
    return scenes
