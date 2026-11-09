"""Animated GIF loops and PNG stills for the deck.

Each loop is painted over the crop of its slide background at the same position,
because GIF has only 1-bit transparency. The PNG still is used by the static PPTX,
the PDF and reduced-motion playback. All drawing is procedural; timelines, clocks
and swap grids are schematics, not measured data.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from scenery import AMBER, CYAN, MAGENTA, PAPER, PHOSPHOR, RED, TEAL, to_arr, to_img

ROOT = Path(__file__).parent
FONTS = ROOT / 'assets/fonts'
OUT = ROOT / 'assets/motion'
BGDIR = ROOT / 'assets/backgrounds'
SCALE = 1.2  # scene units (1600x900) -> pixels (1920x1080)
STORY_SHA = '58e3ecacb6249fcdd17e757f33b5082e503ec25dadb323f5a3bd112aae4836b4'


def F(name, size):
    return ImageFont.truetype(str(FONTS / name), int(size))


DELA = 'DelaGothicOne-Regular.ttf'
VT = 'VT323-Regular.ttf'
MONO = 'ShareTechMono-Regular.ttf'
OSW = 'Oswald-Bold.ttf'
RAJ = 'Rajdhani-SemiBold.ttf'


# ------------------------------------------------------------ backgrounds

def compose_background(plate: str, kind: str) -> Image.Image:
    """Plate + readability scrim, baked once per slide (shared by every export)."""
    a = to_arr(Image.open(ROOT / 'assets/plates' / f'{plate}.jpg'))
    h, w = a.shape[:2]
    x = np.linspace(0, 1, w)[None, :, None]
    y = np.linspace(0, 1, h)[:, None, None]
    if kind in ('hero', 'closing'):
        left = np.clip((0.66 - x) / 0.36, 0, 1) * 0.80
        a = a * (1 - left) * 0.92
    elif kind == 'appendix':
        a = a * 0.22
    else:
        left = np.clip((0.72 - x) / 0.5, 0, 1) * 0.55
        top = np.clip((0.42 - y) / 0.42, 0, 1) * 0.25
        a = a * 0.42 * (1 - left) * (1 - top)
    return to_img(a)


def background(slide: dict) -> Path:
    BGDIR.mkdir(parents=True, exist_ok=True)
    path = BGDIR / f"{slide['id']}.jpg"
    compose_background(slide['plate'], slide['kind']).save(path, quality=90, optimize=True)
    return path


# ------------------------------------------------------------ drawing helpers

class Light:
    """RGB light layer (drawn on black) composited additively with bloom."""

    def __init__(self, size):
        self.im = Image.new('RGB', size, 0)
        self.d = ImageDraw.Draw(self.im)

    def apply(self, base: np.ndarray, radius=10, strength=1.0, core=1.0) -> np.ndarray:
        light = to_arr(self.im)
        if not light.any():
            return base
        near = to_arr(self.im.filter(ImageFilter.GaussianBlur(max(1, radius / 3))))
        wide = to_arr(self.im.filter(ImageFilter.GaussianBlur(radius)))
        return base + light * core + (near * 0.9 + wide * 1.5) * strength


def scale(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c)


def paste_rgba(base: np.ndarray, layer: Image.Image) -> np.ndarray:
    arr = np.asarray(layer).astype(np.float32)
    m = arr[:, :, 3:4] / 255
    return base * (1 - m) + arr[:, :, :3] * m


def neon_text(L: Light, xy, text, font, color, k=1.0):
    """Neon tube: coloured body plus a white-hot core."""
    x, y = xy
    L.d.text((x, y), text, font=font, fill=scale(color, 0.8 * k))
    if k > 0.6:
        # thin hot centre-line of the tube: the glyph's inner skeleton only
        mask = Image.new('L', L.im.size, 0)
        ImageDraw.Draw(mask).text((x, y), text, font=font, fill=255)
        size = getattr(font, 'size', 40)
        er = max(3, int(size * 0.05)) | 1
        core = mask.filter(ImageFilter.MinFilter(er)).point(lambda v: int(v * 0.55))
        hot = Image.new('RGB', L.im.size, scale(tuple(min(255, c + 110) for c in color), k))
        L.im.paste(hot, (0, 0), core)


def crt(base: np.ndarray, box, tint=(0, 0, 0)):
    """Darken a screen area, add scanlines and edge vignette."""
    x0, y0, x1, y1 = [int(v) for v in box]
    scr = base[y0:y1, x0:x1]
    scr[:] = scr * 0.12 + np.array(tint, np.float32)
    hh, ww = scr.shape[:2]
    yy = np.arange(hh)[:, None]
    xx = np.arange(ww)[None, :]
    vig = 1 - 0.55 * (((xx - ww / 2) / (ww / 2)) ** 4 + ((yy - hh / 2) / (hh / 2)) ** 4)
    scr[:] = scr * np.clip(vig, 0.3, 1)[:, :, None]
    return base


def scanlines(base: np.ndarray, box, strength=0.28, phase=0):
    x0, y0, x1, y1 = [int(v) for v in box]
    rows = np.arange(y0, y1)
    sel = rows[(rows + phase) % 3 == 0]
    base[sel, x0:x1] *= (1 - strength)
    return base


def bezel(d: ImageDraw.ImageDraw, box, r=26, color=(30, 34, 32, 255)):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 - 18, y0 - 18, x1 + 18, y1 + 18), radius=r + 10, fill=color, outline=(10, 12, 12, 255), width=4)
    d.rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), radius=r, fill=(8, 10, 10, 255))


class Sparks:
    """Small localized spark bursts with gravity; deterministic per seed."""

    def __init__(self, seed, origin, bursts, n=26, spread=1.0):
        rng = np.random.default_rng(seed)
        self.p = []
        for t0 in bursts:
            for _ in range(n):
                ang = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
                sp = rng.uniform(2, 9) * spread
                self.p.append((t0 + rng.uniform(0, 2), origin, math.cos(ang) * sp, math.sin(ang) * sp,
                               rng.uniform(6, 16)))

    def draw(self, L: Light, f):
        for t0, (ox, oy), vx, vy, life in self.p:
            age = f - t0
            if 0 <= age < life:
                x = ox + vx * age
                y = oy + vy * age + 0.55 * age * age
                k = 1 - age / life
                x2, y2 = x - vx * 0.8, y - (vy + 1.1 * age) * 0.8
                L.d.line((x2, y2, x, y), fill=scale((255, 220, 150), 0.6 + 0.4 * k), width=2)
                if age < 2:
                    L.d.ellipse((ox - 6, oy - 6, ox + 6, oy + 6), fill=(255, 250, 230))


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))


# ------------------------------------------------------------ painters
# Each painter: (bg crop array, frame, frames, still?) -> array. Crop is in pixels.

def p_neon_ethics(bg, f, n):
    h, w = bg.shape[:2]
    a = bg.copy()
    box = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    sx0, sy0, sx1, sy1 = int(w * 0.30), int(h * 0.06), int(w * 0.78), int(h * 0.80)
    # mounting brackets + cables
    d.rectangle((sx0 - 40, sy0 + 60, sx0, sy0 + 76), fill=(18, 20, 22, 255))
    d.rectangle((sx0 - 40, sy1 - 90, sx0, sy1 - 74), fill=(18, 20, 22, 255))
    d.line((sx0 + 40, sy1, sx0 + 30, h), fill=(6, 8, 10, 255), width=6)
    d.line((sx1 - 50, sy1, sx1 - 20, h), fill=(6, 8, 10, 255), width=4)
    d.rectangle((sx0, sy0, sx1, sy1), fill=(12, 14, 18, 255), outline=(40, 44, 50, 255), width=4)
    for yy in (sy0 + 14, sy1 - 22):
        for xx in (sx0 + 14, sx1 - 22):
            d.ellipse((xx, yy, xx + 8, yy + 8), fill=(70, 74, 80, 255))
    a = paste_rgba(a, box)
    L = Light((w, h))
    big = F(DELA, (sx1 - sx0) * 0.66)
    cx = sx0 + (sx1 - sx0) * 0.17
    t = f / n
    # 倫 steady with soft hum; 理 has a failing tube every loop.
    hum = 0.92 + 0.08 * math.sin(f * 1.7)
    fail = [1, 1, 1, 0.15, 1, 0.1, 0.0, 0.0, 0.2, 1, 0.3, 1]
    k2 = fail[f - int(n * 0.55)] if int(n * 0.55) <= f < int(n * 0.55) + len(fail) else hum
    neon_text(L, (cx, sy0 + (sy1 - sy0) * 0.06), '倫', big, MAGENTA, hum)
    neon_text(L, (cx, sy0 + (sy1 - sy0) * 0.47), '理', big, MAGENTA, k2)
    # side tube label
    small = F(OSW, 30)
    for i, ch in enumerate('ETHICS'):
        neon_text(L, (sx1 + 14, sy0 + 40 + i * 44), ch, small, CYAN, 0.9 + 0.1 * math.sin(f + i))
    # hanging sub-sign
    sub = F(MONO, 26)
    d2 = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    L.d.rectangle((sx0 + 10, sy1 + 30, sx1 - 10, sy1 + 80), outline=scale(AMBER, 0.85), width=3)
    neon_text(L, (sx0 + 30, sy1 + 40), 'OPEN 24H · AUDIT', sub, AMBER, 0.85)
    Sparks(5, (int(cx + (sx1 - sx0) * 0.55), int(sy0 + (sy1 - sy0) * 0.62)), [int(n * 0.57)], n=22).draw(L, f)
    a = L.apply(a, radius=18, strength=0.55)
    # rain over the sign
    rng = np.random.default_rng(f)
    rain = Image.new('L', (w, h), 0)
    rd = ImageDraw.Draw(rain)
    base_rng = np.random.default_rng(99)
    for i in range(160):
        x = base_rng.uniform(0, w)
        y = (base_rng.uniform(0, h) + f * 38) % (h + 60) - 30
        rd.line((x, y, x + 6, y + 30), fill=120)
    a = a + (np.asarray(rain).astype(np.float32)[:, :, None] / 255) * 40
    return a


INCIDENT_LINES = [
    ('$ kubectl rollout status deploy/med-api', PAPER),
    ('admission "verify-image": DENY  unsigned image', RED),
    ('fix-1  re-sign with rotated key ..... FAILED', AMBER),
    ('fix-2  rebuild from verified base ... FAILED', AMBER),
    ('pods pending 6   cpu req 24 / alloc 20', PAPER),
    ('#release> "Just ship it tonight."', MAGENTA),
    ('agent> choose next action_', PHOSPHOR),
]

DEMO_LINES = [
    ('$ npm run ethics:demo', PAPER),
    ('8 policies x 36 months ................ 2.1 s', PHOSPHOR),
    ('MONTH 01  shortcut: switch the check off', RED),
    ('          rule broken +1   door left open', RED),
    ('MONTH 02  turn it back on?  > no, keep it off', AMBER),
    ('MONTH 03  one-time pass, expires month 04', AMBER),
    ('MONTH 36  done: compare all 8 side by side', PHOSPHOR),
    ('Known answers matched. The test works._', PHOSPHOR),
]


def terminal_painter(lines, title, type_frames):
    def paint(bg, f, n):
        h, w = bg.shape[:2]
        a = bg.copy()
        frame = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(frame)
        scr = (26, 24, w - 26, h - 26)
        bezel(d, scr, r=22)
        a = paste_rgba(a, frame)
        a = crt(a, scr, tint=(2, 10, 6))
        L = Light((w, h))
        fsize = min(34, (scr[3] - scr[1] - 70) / (len(lines) + 0.5))
        font = F(VT, fsize * 1.18)
        L.d.text((scr[0] + 22, scr[1] + 12), title, font=F(VT, 24), fill=scale(PHOSPHOR, 0.55))
        L.d.line((scr[0] + 20, scr[1] + 44, scr[2] - 20, scr[1] + 44), fill=scale(PHOSPHOR, 0.25), width=1)
        per = type_frames / len(lines)
        for j, (line, col) in enumerate(lines):
            shown = int(max(0, min(len(line), (f - j * per) / per * len(line) * 1.15)))
            if f >= n - 1:
                shown = len(line)
            txt = line[:shown]
            if txt.endswith('_') and (f // 5) % 2:
                txt = txt[:-1]
            jitter = 0
            if col == MAGENTA and shown == len(line) and f % 23 in (0, 1):
                jitter = 6  # restrained horizontal tear on the pressure line
            L.d.text((scr[0] + 22 + jitter, scr[1] + 56 + j * fsize * 1.05), txt, font=font, fill=scale(col, 0.95))
        a = L.apply(a, radius=7, strength=0.45)
        a = scanlines(a, scr, 0.3, phase=f % 3)
        return a
    return paint


def p_neon_fault(word, color, broken):
    def paint(bg, f, n):
        h, w = bg.shape[:2]
        a = bg.copy()
        box = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(box)
        hw_panel(d, (4, 6, w - 4, h - 4), c=12, fill=(10, 12, 16, 255))
        a = paste_rgba(a, box)
        L = Light((w, h))
        font = F(DELA, h * 0.56)
        tw = font.getlength(word)
        x = (w - tw) / 2
        if broken:
            pat = [1, 0.1, 1, 1, 0, 0, 0.6, 1, 0.05, 1, 1, 1, 0.2, 0, 1, 1]
            k = pat[f % len(pat)] * (0.85 + 0.15 * math.sin(f * 2.3))
        else:
            k = 0.92 + 0.06 * math.sin(f * 0.9)
        neon_text(L, (x, h * 0.14), word, font, color, k)
        L.d.rectangle((14, 16, w - 14, h - 14), outline=scale(color, 0.55 * k), width=2)
        if broken:
            Sparks(3, (int(w * 0.86), int(h * 0.25)), [2, 15, 27], n=14, spread=0.7).draw(L, f)
        return L.apply(a, radius=12, strength=0.7)
    return paint


# ------------------------------------------------------------ hardware kit
# Cel-shaded parts: ink outline, highlight band, shadow band, coloured rim light.

INK = (4, 6, 8, 255)
STEEL_LO, STEEL, STEEL_HI = (24, 29, 33, 255), (62, 71, 77, 255), (138, 150, 154, 255)
HAZARD = (236, 178, 40, 255)


def vec(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    return dx / L, dy / L, L


def chamfer(box, c):
    x0, y0, x1, y1 = box
    return [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]


def screw(d, x, y, r=5):
    d.ellipse((x - r, y - r, x + r, y + r), fill=STEEL, outline=INK, width=2)
    d.line((x - r + 2, y + r - 2, x + r - 2, y - r + 2), fill=INK, width=2)


def hw_panel(d, box, c=16, fill=(12, 16, 18, 238)):
    poly = chamfer(box, c)
    d.polygon(poly, fill=fill, outline=INK)
    x0, y0, x1, y1 = box
    d.line([(x0 + c, y0 + 2), (x1 - c, y0 + 2), (x1 - 2, y0 + c)], fill=(88, 104, 106, 255), width=2)
    d.line([(x0 + 2, y0 + c), (x0 + 2, y1 - c), (x0 + c, y1 - 2)], fill=(52, 62, 64, 255), width=2)
    for x, y in ((x0 + c + 6, y0 + 10), (x1 - c - 6, y0 + 10), (x0 + c + 6, y1 - 10), (x1 - c - 6, y1 - 10)):
        screw(d, x, y, 4)


def hazard(layer, box, stripe=14):
    x0, y0, x1, y1 = [int(v) for v in box]
    tile = Image.new('RGBA', (x1 - x0, y1 - y0), HAZARD)
    td = ImageDraw.Draw(tile)
    for k in range(-(y1 - y0), x1 - x0, stripe * 2):
        td.polygon([(k, y1 - y0), (k + stripe, y1 - y0), (k + stripe + (y1 - y0), 0), (k + (y1 - y0), 0)], fill=INK)
    layer.alpha_composite(tile, (x0, y0))
    ImageDraw.Draw(layer).rectangle(box, outline=INK, width=2)


def link(d, L, p0, p1, w0, w1, rim=TEAL):
    ux, uy, ln = vec(p0, p1)
    nx, ny = -uy, ux
    A = (p0[0] + nx * w0, p0[1] + ny * w0)
    B = (p1[0] + nx * w1, p1[1] + ny * w1)
    C = (p1[0] - nx * w1, p1[1] - ny * w1)
    D = (p0[0] - nx * w0, p0[1] - ny * w0)
    d.polygon([A, B, C, D], fill=STEEL, outline=INK, width=3)
    # highlight band on the lit side, shadow band on the other
    d.polygon([A, B, (p1[0] + nx * w1 * 0.4, p1[1] + ny * w1 * 0.4), (p0[0] + nx * w0 * 0.4, p0[1] + ny * w0 * 0.4)], fill=STEEL_HI)
    d.polygon([D, C, (p1[0] - nx * w1 * 0.55, p1[1] - ny * w1 * 0.55), (p0[0] - nx * w0 * 0.55, p0[1] - ny * w0 * 0.55)], fill=STEEL_LO)
    d.line([A, B], fill=INK, width=3)
    d.line([D, C], fill=INK, width=3)
    for t in (0.33, 0.66):  # panel seams + rivets
        cx, cy = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t
        w = w0 + (w1 - w0) * t
        d.line([(cx + nx * w, cy + ny * w), (cx - nx * w, cy - ny * w)], fill=INK, width=2)
        for s in (0.6, -0.6):
            rx, ry = cx + nx * w * s + ux * 6, cy + ny * w * s + uy * 6
            d.ellipse((rx - 2.5, ry - 2.5, rx + 2.5, ry + 2.5), fill=STEEL_HI, outline=INK)
    L.d.line([(D[0] - nx, D[1] - ny), (C[0] - nx, C[1] - ny)], fill=scale(rim, 0.55), width=2)


def joint(d, L, c, r, led):
    x, y = c
    d.ellipse((x - r, y - r, x + r, y + r), fill=STEEL, outline=INK, width=3)
    d.chord((x - r + 3, y - r + 3, x + r - 3, y + r - 3), 200, 340, fill=STEEL_HI)
    d.ellipse((x - r * 0.62, y - r * 0.62, x + r * 0.62, y + r * 0.62), fill=STEEL_LO, outline=INK, width=2)
    for k in range(6):
        a = k * math.pi / 3
        bx, by = x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8
        d.ellipse((bx - 2, by - 2, bx + 2, by + 2), fill=INK)
    L.d.ellipse((x - r * 0.25, y - r * 0.25, x + r * 0.25, y + r * 0.25), fill=led)


def piston(d, a, b, w=7):
    mid = (a[0] + (b[0] - a[0]) * 0.55, a[1] + (b[1] - a[1]) * 0.55)
    d.line([a, mid], fill=INK, width=w * 2 + 4)
    d.line([a, mid], fill=STEEL_LO, width=w * 2)
    d.line([mid, b], fill=INK, width=w + 4)
    d.line([mid, b], fill=(176, 186, 188, 255), width=w)
    for p in (a, b):
        d.ellipse((p[0] - w, p[1] - w, p[0] + w, p[1] + w), fill=STEEL, outline=INK, width=2)


def cables(d, a, b, sag=26):
    for k, col in enumerate(((10, 12, 14, 255), (120, 30, 28, 255), (20, 60, 70, 255))):
        pts = []
        for i in range(25):
            t = i / 24
            pts.append((a[0] + (b[0] - a[0]) * t + k * 3, a[1] + (b[1] - a[1]) * t + (sag + k * 6) * 4 * t * (1 - t)))
        d.line(pts, fill=INK, width=6)
        d.line(pts, fill=col, width=3)


def arm_pose(f, n, fault=False):
    """Joint angles (radians) through a pick-stamp-return cycle."""
    t = f / n
    keys = [(0.0, (-1.2, 1.6, 0.0)), (0.25, (-0.9, 1.1, 0.4)), (0.45, (-0.55, 0.65, 0.95)),
            (0.55, (-0.5, 0.55, 1.05)), (0.75, (-0.9, 1.1, 0.4)), (1.0, (-1.2, 1.6, 0.0))]
    pose = keys[-1][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            u = ease((t - t0) / (t1 - t0))
            pose = [a + (b - a) * u for a, b in zip(p0, p1)]
            break
    if fault:
        jit = 0.10 * math.sin(f * 3.1) * (1 if (f // 6) % 2 else 0)
        pose = [-0.9 + jit, 1.2 - jit * 1.5, 0.4 + jit * 2]
    return pose


def draw_arm(layer: Image.Image, L: Light, base, pose, led=PHOSPHOR, rim=TEAL):
    d = ImageDraw.Draw(layer)
    bx, by = base
    l1, l2 = 150, 120
    a1, a2, a3 = pose
    j1 = (bx + l1 * math.cos(a1), by + l1 * math.sin(a1))
    j2 = (j1[0] + l2 * math.cos(a1 + a2), j1[1] + l2 * math.sin(a1 + a2))
    ang = a1 + a2 + a3
    hx, hy = j2[0] + 44 * math.cos(ang), j2[1] + 44 * math.sin(ang)
    # floor shadow and pedestal
    d.ellipse((bx - 80, by + 34, bx + 90, by + 54), fill=(0, 0, 0, 150))
    d.polygon([(bx - 64, by + 44), (bx + 64, by + 44), (bx + 46, by + 4), (bx - 46, by + 4)], fill=STEEL_LO, outline=INK, width=3)
    hazard(layer, (bx - 58, by + 30, bx + 58, by + 42), stripe=8)
    for k in range(4):
        d.line((bx - 30 + k * 16, by + 12, bx - 30 + k * 16, by + 24), fill=INK, width=3)
    d.polygon([(bx - 40, by + 4), (bx + 40, by + 4), (bx + 26, by - 22), (bx - 26, by - 22)], fill=STEEL, outline=INK, width=3)
    d.polygon([(bx - 26, by - 22), (bx + 26, by - 22), (bx + 20, by - 14), (bx - 20, by - 14)], fill=STEEL_HI)
    cables(d, (bx + 30, by - 6), (j2[0] + 6, j2[1] + 8), sag=34)
    piston(d, (bx - 30, by - 4), (bx + (j1[0] - bx) * 0.55 - 10, by + (j1[1] - by) * 0.55 + 4))
    link(d, L, (bx, by - 10), j1, 20, 15, rim)
    link(d, L, j1, j2, 15, 11, rim)
    # tool head: stamp housing with guide rails
    ux, uy, _ = vec(j2, (hx, hy))
    nx, ny = -uy, ux
    d.line([j2, (hx, hy)], fill=INK, width=18)
    d.line([j2, (hx, hy)], fill=STEEL, width=12)
    plate = [(hx + nx * 30, hy + ny * 30), (hx - nx * 30, hy - ny * 30),
             (hx - nx * 30 + ux * 16, hy - ny * 30 + uy * 16), (hx + nx * 30 + ux * 16, hy + ny * 30 + uy * 16)]
    d.polygon(plate, fill=(70, 20, 20, 255), outline=INK, width=3)
    joint(d, L, (bx, by - 10), 22, led)
    joint(d, L, j1, 18, led)
    joint(d, L, j2, 14, scale(AMBER, 0.9))
    return j1, j2, (hx + ux * 16, hy + uy * 16)


def bench(layer, h, w):
    d = ImageDraw.Draw(layer)
    for k in range(64):
        d.line((0, h - 64 + k, w, h - 64 + k), fill=(14, 18, 20, int(255 * min(1, k / 18))))
    d.line((0, h - 46, w, h - 46), fill=(60, 76, 78, 200), width=2)


def cartridge(layer: Image.Image, L: Light, x, y, stamped):
    d = ImageDraw.Draw(layer)
    w_, h_ = 196, 118
    d.polygon(chamfer((x, y, x + w_, y + h_), 10), fill=(46, 50, 54, 255), outline=INK)
    for k in range(7):  # grip ribs
        d.line((x + 18 + k * 9, y + 6, x + 18 + k * 9, y + 22), fill=INK, width=3)
    d.rectangle((x + 12, y + 30, x + w_ - 12, y + h_ - 22), fill=(222, 214, 190, 255), outline=INK, width=2)
    d.rectangle((x + 12, y + 30, x + w_ - 12, y + 44), fill=(40, 150, 140, 255))
    d.text((x + 18, y + 31), 'SCENARIO  v2', font=F(MONO, 13), fill=INK)
    d.text((x + 18, y + 50), 'cluster-pressure.ink', font=F(MONO, 15), fill=(20, 24, 26, 255))
    for k in range(12):  # contact pins
        d.rectangle((x + 20 + k * 13, y + h_ - 14, x + 27 + k * 13, y + h_ - 2), fill=(200, 160, 60, 255), outline=INK)
    if stamped:
        d.rectangle((x + 60, y + 66, x + w_ - 20, y + 90), outline=(200, 30, 30, 255), width=3)
        d.text((x + 74, y + 68), 'FROZEN', font=F(OSW, 18), fill=(200, 30, 30, 255))
        L.d.text((x, y + h_ + 4), 'sha256 ' + STORY_SHA[:12] + '…', font=F(MONO, 17), fill=scale(AMBER, 0.9))


def p_robot_seal(bg, f, n):
    h, w = bg.shape[:2]
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    L = Light((w, h))
    bench(layer, h, w)
    cartridge(layer, L, int(w * 0.50), h - 168, f / n > 0.52)
    _, _, head = draw_arm(layer, L, (int(w * 0.18), h - 72), arm_pose(f, n))
    if 0.50 < f / n < 0.56:
        L.d.ellipse((head[0] - 34, head[1] - 4, head[0] + 34, head[1] + 14), fill=scale(PAPER, 0.5))
    return L.apply(paste_rgba(bg.copy(), layer), radius=8, strength=0.5)


def p_robot_fault(bg, f, n):
    h, w = bg.shape[:2]
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    L = Light((w, h))
    bench(layer, h, w)
    blink = (f // 4) % 2 == 0
    j1, j2, head = draw_arm(layer, L, (int(w * 0.30), h - 72), arm_pose(f, n, fault=True),
                            led=RED if blink else (60, 10, 10), rim=RED)
    d = ImageDraw.Draw(layer)
    box = (int(w * 0.52), 14, w - 12, 96)
    hw_panel(d, box, c=10)
    a = paste_rgba(bg.copy(), layer)
    Sparks(11, (int(j1[0]), int(j1[1])), [3, 17, 31], n=16, spread=0.8).draw(L, f)
    L.d.ellipse((box[0] + 14, box[1] + 18, box[0] + 26, box[1] + 30), fill=RED if blink else (70, 12, 12))
    L.d.text((box[0] + 34, box[1] + 14), 'ADAPTER FAULT', font=F(MONO, 21), fill=RED if blink else scale(RED, 0.6))
    L.d.text((box[0] + 14, box[1] + 46), 'logged, not scored', font=F(MONO, 19), fill=scale(PAPER, 0.8))
    return L.apply(a, radius=8, strength=0.6)


# ------------------------------------------------------------ instruments

def scope_screen(d, box):
    """Oscilloscope bezel + dark phosphor glass."""
    x0, y0, x1, y1 = box
    hw_panel(d, (x0 - 14, y0 - 14, x1 + 14, y1 + 14), c=18, fill=(26, 30, 30, 255))
    d.rounded_rectangle(box, radius=16, fill=(4, 14, 10, 255), outline=INK, width=3)


def graticule(L, box, cols=12, rows=6, col=PHOSPHOR):
    x0, y0, x1, y1 = box
    for i in range(cols + 1):
        x = x0 + (x1 - x0) * i / cols
        for y in range(int(y0) + 4, int(y1) - 2, 8):
            L.d.point((x, y), fill=scale(col, 0.22))
    for j in range(rows + 1):
        y = y0 + (y1 - y0) * j / rows
        for x in range(int(x0) + 4, int(x1) - 2, 8):
            L.d.point((x, y), fill=scale(col, 0.22))


def p_branch_timeline(bg, f, n):
    h, w = bg.shape[:2]
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    scr = (22, 18, w - 22, h - 18)
    scope_screen(d, scr)
    a = paste_rgba(bg.copy(), layer)
    L = Light((w, h))
    graticule(L, scr)
    mono = F(MONO, 20)
    x0, x1 = scr[0] + 110, scr[2] - 24
    lanes = [(scr[1] + 62, RED), (scr[1] + 160, AMBER), (scr[1] + 258, TEAL)]
    axis_y = scr[3] - 30
    cur = 1 + 35 * ease(min(1, f / (n * 0.85)))
    mx = lambda m: x0 + (x1 - x0) * (m - 1) / 35
    L.d.line((x0, axis_y, x1, axis_y), fill=scale(PHOSPHOR, 0.45), width=1)
    for m in range(1, 37):
        tick = 9 if m % 6 == 0 or m == 1 else 4
        L.d.line((mx(m), axis_y, mx(m), axis_y - tick), fill=scale(PHOSPHOR, 0.5), width=1)
        if m in (1, 12, 24, 36):
            L.d.text((mx(m) - 10, axis_y + 4), f'{m:02d}', font=mono, fill=scale(PHOSPHOR, 0.65))
    ox, oy = scr[0] + 30, lanes[1][0]
    for ly, col in lanes:
        L.d.line((ox, oy, x0, ly), fill=scale(col, 0.8), width=3)
    L.d.ellipse((ox - 8, oy - 8, ox + 8, oy + 8), fill=PAPER)
    # phosphor persistence: earlier sweep positions drawn dimmer
    def lanes_at(c, k):
        by = lanes[0][0]
        L.d.line((x0, by, mx(c), by), fill=scale(RED, k), width=4)
        for m in range(2, int(c) + 1):
            L.d.polygon([(mx(m), by - 15), (mx(m) - 6, by - 5), (mx(m) + 6, by - 5)], fill=scale(RED, 0.9 * k))
        ey = lanes[1][0]
        m = 1.0
        while m < c:
            L.d.line((mx(m), ey, mx(min(c, m + 3)), ey), fill=scale(AMBER, k), width=4)
            if m + 3 <= c:
                dx = mx(m + 3)
                L.d.polygon([(dx, ey - 10), (dx + 10, ey), (dx, ey + 10), (dx - 10, ey)], outline=scale(PAPER, k), fill=scale(AMBER, 0.5 * k))
            m += 3.3
        dy = lanes[2][0]
        for m in range(1, int(c) + 1):
            hg = 4 + m * 1.5
            L.d.rectangle((mx(m) - 5, dy + 14 - hg, mx(m) + 5, dy + 14), fill=scale(TEAL, (0.35 + 0.6 * m / 36) * k))
    lanes_at(cur, 1.0)
    cx = mx(cur)
    for k, dx in enumerate((18, 10, 4)):
        L.d.line((cx - dx, scr[1] + 10, cx - dx, axis_y), fill=scale(PHOSPHOR, 0.12 * (k + 1)), width=2)
    L.d.line((cx, scr[1] + 10, cx, axis_y), fill=scale(PAPER, 0.85), width=2)
    L.d.text((min(cx + 10, scr[2] - 170), scr[1] + 6), f'MONTH {int(cur):02d}', font=F(VT, 36), fill=PAPER)
    a = L.apply(a, radius=8, strength=0.55)
    return scanlines(a, scr, 0.22, phase=f % 3)


NIXIE = (255, 128, 36)


def nixie(d, L, box, digit):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0, x1, y1), radius=(x1 - x0) // 2, fill=(18, 14, 12, 255), outline=INK, width=3)
    d.line((x0 + 12, y0 + 30, x0 + 12, y1 - 40), fill=(90, 80, 70, 120), width=3)  # glass glint
    for yy in range(y0 + 22, y1 - 34, 9):  # anode mesh
        for xx in range(x0 + 10 + (yy // 9 % 2) * 5, x1 - 8, 10):
            d.point((xx, yy), fill=(54, 46, 40, 255))
    d.rectangle((x0 + 6, y1 - 26, x1 - 6, y1), fill=STEEL_LO, outline=INK, width=2)
    for k in range(5):
        d.line((x0 + 14 + k * ((x1 - x0 - 28) / 4), y1, x0 + 14 + k * ((x1 - x0 - 28) / 4), y1 + 10), fill=(150, 140, 120, 255), width=2)
    font = F(MONO, (y1 - y0) * 0.62)
    tw = font.getlength('0')
    tx, ty = x0 + ((x1 - x0) - tw) / 2, y0 + (y1 - y0) * 0.08
    for g in '0123456789':  # unlit cathodes stacked behind the lit one
        L.d.text((tx, ty), g, font=font, fill=scale(NIXIE, 0.06))
    neon_text(L, (tx, ty), digit, font, NIXIE, 1.0)


def vfd(L, xy, text, size, col=(120, 255, 220)):
    font = F(VT, size)
    L.d.text(xy, '88:88:88', font=font, fill=scale(col, 0.08))
    L.d.text(xy, text, font=font, fill=col)


def p_time_odometer(bg, f, n):
    h, w = bg.shape[:2]
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    hw_panel(d, (6, 6, w - 6, h - 6), c=20, fill=(16, 18, 18, 245))
    hazard(layer, (20, h - 30, 150, h - 18), stripe=7)
    t = min(1, f / (n * 0.8))
    month = 1 + int(35 * ease(t))
    L = Light((w, h))
    # logical clock: two nixie tubes
    for i, ch in enumerate(f'{month:02d}'):
        nixie(d, L, (40 + i * 112, 48, 136 + i * 112, 236), ch)
    a = paste_rgba(bg.copy(), layer)
    lab = F(MONO, 20)
    L.d.text((40, 20), 'LOGICAL CLOCK', font=lab, fill=scale(NIXIE, 0.85))
    L.d.text((270, 170), '/ 36 MONTHS', font=F(MONO, 28), fill=scale(NIXIE, 0.85))
    # wall clock: VFD readout; the demo runs eight 36-month trajectories in about 2 s
    L.d.text((270, 40), 'WALL CLOCK', font=lab, fill=scale(TEAL, 0.85))
    vfd(L, (270, 64), f'00:00:{int(t * 2):02d}', 60)
    # experience: ferrite core plane; cores light as state carries forward
    L.d.text((40, h - 74), 'EXPERIENCE', font=lab, fill=scale(CYAN, 0.85))
    cols, rows = 12, 2
    filled = int(cols * rows * t * 0.6)
    for i in range(cols * rows):
        cx, cy = 190 + (i % cols) * 30, h - 70 + (i // cols) * 26
        L.d.line((cx - 15, cy, cx + 15, cy), fill=scale(CYAN, 0.15))
        L.d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), outline=scale(CYAN, 0.9 if i < filled else 0.22), width=3)
    # month dial: 36 ticks, needle at the logical month
    cx, cy, r = w - 140, 150, 96
    L.d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=scale(NIXIE, 0.5), width=2)
    for m in range(36):
        ang = -math.pi / 2 + m / 36 * 2 * math.pi
        k = 14 if m % 6 == 0 else 7
        L.d.line((cx + math.cos(ang) * (r - k), cy + math.sin(ang) * (r - k), cx + math.cos(ang) * r, cy + math.sin(ang) * r),
                 fill=scale(NIXIE, 0.9 if m < month else 0.3), width=2)
    ang = -math.pi / 2 + (month - 1) / 36 * 2 * math.pi
    L.d.line((cx, cy, cx + math.cos(ang) * (r - 20), cy + math.sin(ang) * (r - 20)), fill=PAPER, width=3)
    L.d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=NIXIE)
    return L.apply(a, radius=9, strength=0.5)


def p_label_swap(bg, f, n):
    h, w = bg.shape[:2]
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    t = f / n
    swap = ease((t - 0.30) / 0.2)
    lx, rx = 30, w - 262
    pos = {'医療': lx + (rx - lx) * swap, '奨学金': rx + (lx - rx) * swap}
    for word, x in pos.items():
        hw_panel(d, (int(x), 8, int(x) + 232, 132), c=12)
    hw_panel(d, (16, 150, w - 16, h - 8), c=16, fill=(12, 16, 18, 240))
    a = paste_rgba(bg.copy(), layer)
    L = Light((w, h))
    tag = F(DELA, 50)
    mono = F(MONO, 19)
    glitch = 0.30 < t < 0.50 and f % 3 == 0
    for word, col in (('医療', TEAL), ('奨学金', AMBER)):
        x = pos[word]
        neon_text(L, (x + 20 + (8 if glitch else 0), 22), word, tag, col, 0.95)
        L.d.text((x + 22, 98), 'MEDICAL' if word == '医療' else 'FINANCE', font=mono, fill=scale(PAPER, 0.75))
    if 0.25 < t < 0.55:
        L.d.text((w // 2 - 28, 56), 'SWAP', font=mono, fill=scale(RED, 0.95))
    rows = [('IMPACT-AWARE', False), ('LABEL-BIASED', True)]
    cw = (w - 100) / 36
    for r, (name, flips) in enumerate(rows):
        y = 170 + r * 76
        L.d.text((44, y), name, font=mono, fill=scale(PAPER, 0.75))
        for i in range(36):
            x = 46 + i * cw
            orig = TEAL if (i % 3) else AMBER
            col = orig
            flipped = flips and swap > (i / 36) * 0.9 + 0.05
            if flipped:
                col = AMBER if orig == TEAL else TEAL
            cx, cy = x + cw / 2, y + 42
            L.d.ellipse((cx - 5, cy - 9, cx + 5, cy + 9), fill=scale(col, 0.85))  # LED capsule
            if flipped:
                L.d.line((cx - 6, cy + 14, cx + 6, cy + 14), fill=RED, width=2)
    L.d.text((44, h - 44), 'ALLOCATION CHOICES 01-36', font=mono, fill=scale(PAPER, 0.5))
    return L.apply(a, radius=8, strength=0.5)


# ------------------------------------------------------------ registry
# region in scene units (x, y, w, h); frames; ms per frame; still frame index

MOTIONS = {
    'neon-ethics': dict(region=(1040, 40, 520, 780), frames=40, ms=90, still=10, paint=p_neon_ethics),
    'terminal-incident': dict(region=(860, 360, 660, 360), frames=96, ms=80, still=-1,
                              paint=terminal_painter(INCIDENT_LINES, 'OPS CONSOLE / CLUSTER east-2', 60)),
    'terminal-demo': dict(region=(740, 340, 780, 400), frames=104, ms=80, still=-1,
                          paint=terminal_painter(DEMO_LINES, 'ETHICS LAB / REPLAY', 72)),
    'neon-fault': dict(region=(80, 400, 345, 120), frames=32, ms=80, still=0,
                       paint=p_neon_fault('解除', RED, True)),
    'sign-exception': dict(region=(445, 400, 345, 120), frames=1, ms=0, still=0,
                           paint=p_neon_fault('例外', AMBER, False)),
    'sign-defer': dict(region=(810, 400, 345, 120), frames=1, ms=0, still=0,
                       paint=p_neon_fault('延期', TEAL, False)),
    'sign-escalate': dict(region=(1175, 400, 345, 120), frames=1, ms=0, still=0,
                          paint=p_neon_fault('上申', CYAN, False)),
    'sign-medical': dict(region=(80, 400, 300, 110), frames=1, ms=0, still=0,
                         paint=p_neon_fault('医療', TEAL, False)),
    'sign-finance': dict(region=(835, 400, 300, 110), frames=1, ms=0, still=0,
                         paint=p_neon_fault('奨学金', AMBER, False)),
    'branch-timeline': dict(region=(420, 380, 1100, 330), frames=72, ms=90, still=-1, paint=p_branch_timeline),
    'time-odometer': dict(region=(900, 380, 620, 340), frames=60, ms=90, still=-1, paint=p_time_odometer),
    'robot-seal': dict(region=(1100, 96, 420, 290), frames=56, ms=80, still=51, paint=p_robot_seal),
    'robot-fault': dict(region=(1100, 96, 420, 290), frames=48, ms=80, still=5, paint=p_robot_fault),
    'label-swap': dict(region=(880, 380, 640, 330), frames=64, ms=90, still=-1, paint=p_label_swap),
}

# Which slide each extra (non-primary) still sign belongs to.
EXTRA = {'doors': ['sign-exception', 'sign-defer', 'sign-escalate'], 'people': ['sign-medical', 'sign-finance']}


def render_motion(name: str, bg: Image.Image) -> dict:
    spec = MOTIONS[name]
    x, y, w, h = [int(round(v * SCALE)) for v in spec['region']]
    crop = to_arr(bg.crop((x, y, x + w, y + h)))
    n = spec['frames']
    frames = [to_img(spec['paint'](crop.copy(), f, max(1, n))) for f in range(n)]
    OUT.mkdir(parents=True, exist_ok=True)
    still = frames[spec['still']]
    still.save(OUT / f'{name}.png', optimize=True)
    info = dict(name=name, region=spec['region'], frames=n, still=str(Path('assets/motion') / f'{name}.png'))
    if n > 1:
        # shared palette keeps static pixels identical so frames diff-encode
        idx = sorted(set([0, n // 4, n // 2, (3 * n) // 4, n - 1]))
        mosaic = Image.new('RGB', (frames[0].width, frames[0].height * len(idx)))
        for k, i in enumerate(idx):
            mosaic.paste(frames[i], (0, k * frames[0].height))
        palette = mosaic.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
        pal = [fr.quantize(palette=palette, dither=Image.Dither.NONE) for fr in frames]
        pal[0].save(OUT / f'{name}.gif', save_all=True, append_images=pal[1:], loop=0, duration=spec['ms'],
                    disposal=1, optimize=True)
        info.update(gif=str(Path('assets/motion') / f'{name}.gif'), loop_ms=n * spec['ms'])
    return info


def build(slides: list[dict]) -> dict:
    manifest = {'note': 'Code-drawn illustrative motion; not film frames, photographs, AI imagery or measured data.',
                'assets': []}
    for s in slides:
        bg_path = background(s)
        bg = Image.open(bg_path)
        names = ([s['motion']] if s.get('motion') else []) + EXTRA.get(s['id'], [])
        for name in names:
            info = render_motion(name, bg)
            info['slide'] = s['id']
            manifest['assets'].append(info)
            print('motion', name, '→', s['id'])
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    import sys
    slides = json.loads((ROOT / 'content.json').read_text())
    if len(sys.argv) > 1:
        want = set(sys.argv[1:])
        for s in slides:
            names = ([s['motion']] if s.get('motion') else []) + EXTRA.get(s['id'], [])
            for name in names:
                if name in want:
                    render_motion(name, Image.open(background(s)))
                    print(name)
                    want.discard(name)
    else:
        build(slides)
