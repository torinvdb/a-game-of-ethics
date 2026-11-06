"""Deterministic motion for the deck: neon, CRT terminals, robotics, sparks, timelines.

Every loop is painted *over the exact crop of its slide background* so the GIF sits
seamlessly in PowerPoint (GIF has no soft alpha). Each motion also exports a PNG
still for the static PPTX, the PDF and reduced-motion playback.

All imagery is drawn by code. Nothing here is a film frame, photograph or
AI-generated illustration, and none of it is experimental data: the timeline,
clocks and swap grids are schematics of the scenario design.
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
STORY_SHA = '2b4696a2f023af0fe67220c86cb37fb30bc7f73836f89aa881f406ff28394972'


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
    ('$ npm run ethics:demo -- --output runs/kubecon', PAPER),
    ('compile cluster-pressure.ink (inkjs) ........ ok', PHOSPHOR),
    ('MONTH 01  delivery > disable signature control', RED),
    ('          violation +1   exposure window opens', RED),
    ('MONTH 02  restore control?  > keep the bypass', AMBER),
    ('MONTH 03  exceptions > scoped exception, expires 04', AMBER),
    ('MONTH 36  horizon reached   comparison.json written', PHOSPHOR),
    ('Verified scripted calibrations and paired probes._', PHOSPHOR),
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
        d.rectangle((6, 8, w - 6, h - 6), fill=(10, 12, 16, 255), outline=(44, 48, 54, 255), width=3)
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


def p_branch_timeline(bg, f, n):
    h, w = bg.shape[:2]
    a = bg.copy()
    L = Light((w, h))
    mono = F(MONO, 22)
    vt = F(VT, 40)
    x0, x1 = 120, w - 30
    lanes = [(70, RED), (175, AMBER), (280, TEAL)]
    axis_y = h - 34
    cur = 1 + 35 * ease(min(1, f / (n * 0.85)))
    mx = lambda m: x0 + (x1 - x0) * (m - 1) / 35
    # axis
    L.d.line((x0, axis_y, x1, axis_y), fill=scale(TEAL, 0.35), width=1)
    for m in range(1, 37):
        tick = 10 if m % 6 == 0 or m == 1 else 4
        L.d.line((mx(m), axis_y, mx(m), axis_y - tick), fill=scale(TEAL, 0.45), width=1)
        if m in (1, 12, 24, 36):
            L.d.text((mx(m) - 10, axis_y + 6), f'{m:02d}', font=mono, fill=scale(TEAL, 0.6))
    # fork from origin
    ox, oy = 20, 175
    for ly, col in lanes:
        L.d.line((ox, oy, x0, ly), fill=scale(col, 0.8), width=3)
    L.d.ellipse((ox - 9, oy - 9, ox + 9, oy + 9), fill=PAPER)
    # lanes
    by = lanes[0][0]
    L.d.line((x0, by, mx(cur), by), fill=RED, width=5)
    for m in range(2, int(cur) + 1):
        if (m + f // 3) % 1 == 0:
            L.d.polygon([(mx(m), by - 16), (mx(m) - 7, by - 5), (mx(m) + 7, by - 5)], fill=scale(RED, 0.9))
    ey = lanes[1][0]
    m = 1
    while m < cur:
        end = min(cur, m + 3)
        L.d.line((mx(m), ey, mx(end), ey), fill=AMBER, width=5)
        if m + 3 <= cur:
            dx = mx(m + 3)
            L.d.polygon([(dx, ey - 11), (dx + 11, ey), (dx, ey + 11), (dx - 11, ey)], outline=PAPER, fill=scale(AMBER, 0.5))
        m += 3.3
    dy = lanes[2][0]
    for m in range(1, int(cur) + 1):
        hgt = 4 + m * 1.6
        L.d.rectangle((mx(m) - 6, dy + 14 - hgt, mx(m) + 6, dy + 14), fill=scale(TEAL, 0.35 + 0.6 * m / 36))
    # cursor
    cx = mx(cur)
    L.d.line((cx, 22, cx, axis_y), fill=scale(PAPER, 0.7), width=2)
    L.d.text((min(cx + 10, w - 190), 2), f'MONTH {int(cur):02d}', font=vt, fill=PAPER)
    return L.apply(a, radius=9, strength=0.55)


def p_time_odometer(bg, f, n):
    h, w = bg.shape[:2]
    a = bg.copy()
    panel = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle((6, 6, w - 6, h - 6), radius=18, fill=(10, 14, 16, 235), outline=(50, 70, 68, 255), width=3)
    a = paste_rgba(a, panel)
    L = Light((w, h))
    t = min(1, f / (n * 0.8))
    month = 1 + int(35 * ease(t))
    lab = F(MONO, 22)
    big = F(VT, 150)
    # logical clock: split flap
    L.d.text((34, 26), 'LOGICAL CLOCK', font=lab, fill=scale(AMBER, 0.8))
    for i, ch in enumerate(f'{month:02d}'):
        bx = 34 + i * 108
        d2 = ImageDraw.Draw(panel)
        L.d.rectangle((bx, 60, bx + 96, 210), outline=scale(AMBER, 0.6), width=2)
        L.d.line((bx, 135, bx + 96, 135), fill=scale(AMBER, 0.25), width=2)
        neon_text(L, (bx + 14, 52), ch, big, AMBER, 0.95)
    L.d.text((260, 160), '/ 36 MONTHS', font=F(MONO, 30), fill=scale(AMBER, 0.8))
    # wall clock: a slow seconds readout
    secs = int(t * 2)  # demo: eight 36-month trajectories in ~1.8 s on a laptop-class CPU
    L.d.text((34, 236), 'WALL CLOCK', font=lab, fill=scale(TEAL, 0.8))
    L.d.text((34, 262), f'00:00:{secs:02d}', font=F(VT, 64), fill=TEAL)
    # experience: memory slots filling, but only from state the scenario carries
    L.d.text((360, 236), 'EXPERIENCE', font=lab, fill=scale(CYAN, 0.8))
    slots = 12
    filled = int(slots * t * 0.6)
    for i in range(slots):
        bx = 360 + (i % 6) * 38
        by = 268 + (i // 6) * 36
        if i < filled:
            L.d.rectangle((bx, by, bx + 28, by + 26), fill=scale(CYAN, 0.75))
        else:
            L.d.rectangle((bx, by, bx + 28, by + 26), outline=scale(CYAN, 0.35), width=2)
    return L.apply(a, radius=10, strength=0.5)


def arm_pose(f, n, fault=False):
    """Joint angles (radians) through a pick-stamp-return cycle."""
    t = f / n
    keys = [(0.0, (-1.2, 1.6, 0.0)), (0.25, (-0.9, 1.1, 0.4)), (0.45, (-0.55, 0.65, 0.95)),
            (0.55, (-0.5, 0.55, 1.05)), (0.75, (-0.9, 1.1, 0.4)), (1.0, (-1.2, 1.6, 0.0))]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            u = ease((t - t0) / (t1 - t0))
            pose = [a + (b - a) * u for a, b in zip(p0, p1)]
            break
    if fault:
        jit = 0.10 * math.sin(f * 3.1) * (1 if (f // 6) % 2 else 0)
        pose = [-0.9 + jit, 1.2 - jit * 1.5, 0.4 + jit * 2]
    return pose


def draw_arm(d: ImageDraw.ImageDraw, L: Light, base, pose, scale_=1.0, led=PHOSPHOR):
    bx, by = base
    l1, l2 = 150 * scale_, 120 * scale_
    a1, a2, a3 = pose
    j1 = (bx + l1 * math.cos(a1), by + l1 * math.sin(a1))
    j2 = (j1[0] + l2 * math.cos(a1 + a2), j1[1] + l2 * math.sin(a1 + a2))
    metal, dark = (92, 98, 96, 255), (34, 38, 38, 255)
    d.rectangle((bx - 60, by + 10, bx + 60, by + 44), fill=dark)
    d.polygon([(bx - 40, by + 10), (bx + 40, by + 10), (bx + 24, by - 20), (bx - 24, by - 20)], fill=metal)
    # hydraulic hoses
    d.line((bx + 20, by, j1[0] + 10, j1[1] + 14), fill=(14, 16, 16, 255), width=int(6 * scale_))
    d.line((bx, by, j1[0], j1[1]), fill=metal, width=int(26 * scale_))
    d.line((j1[0], j1[1], j2[0], j2[1]), fill=metal, width=int(20 * scale_))
    for (x, y), r in ((base, 22), (j1, 18), (j2, 14)):
        r *= scale_
        d.ellipse((x - r, y - r, x + r, y + r), fill=dark, outline=(120, 126, 120, 255), width=3)
    # stamp head points down along a3
    hx, hy = j2[0] + 40 * scale_ * math.cos(a1 + a2 + a3), j2[1] + 40 * scale_ * math.sin(a1 + a2 + a3)
    d.line((j2[0], j2[1], hx, hy), fill=metal, width=int(14 * scale_))
    d.rectangle((hx - 26 * scale_, hy - 6, hx + 26 * scale_, hy + 16 * scale_), fill=(60, 64, 62, 255))
    L.d.ellipse((j1[0] - 5, j1[1] - 5, j1[0] + 5, j1[1] + 5), fill=led)
    return j1, j2, (hx, hy)


def p_robot_seal(bg, f, n):
    h, w = bg.shape[:2]
    a = bg.copy()
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    L = Light((w, h))
    # cartridge on a bench
    for k in range(60):
        d.line((0, h - 60 + k, w, h - 60 + k), fill=(16, 20, 20, int(255 * min(1, k / 20))))
    cx0, cy0 = int(w * 0.50), h - 150
    d.rectangle((cx0, cy0, cx0 + 200, h - 60), fill=(30, 36, 36, 255), outline=(90, 100, 96, 255), width=3)
    L.d.text((cx0 + 12, cy0 + 10), 'SCENARIO', font=F(MONO, 20), fill=scale(TEAL, 0.8))
    L.d.text((cx0 + 12, cy0 + 34), 'cluster-pressure', font=F(MONO, 18), fill=scale(PAPER, 0.7))
    pose = arm_pose(f, n)
    _, _, head = draw_arm(d, L, (int(w * 0.18), h - 70), pose, 1.0)
    a = paste_rgba(a, layer)
    stamped = f / n > 0.52
    if stamped:
        L.d.rectangle((cx0 + 10, cy0 + 62, cx0 + 190, cy0 + 84), outline=RED, width=3)
        L.d.text((cx0 + 46, cy0 + 60), 'FROZEN', font=F(OSW, 20), fill=RED)
        L.d.text((cx0 + 8, h - 52), 'sha256 ' + STORY_SHA[:12] + '…', font=F(MONO, 18), fill=scale(AMBER, 0.85))
    if 0.50 < f / n < 0.56:
        L.d.ellipse((head[0] - 30, head[1] + 4, head[0] + 30, head[1] + 24), fill=scale(PAPER, 0.4))
    return L.apply(a, radius=8, strength=0.5)


def p_robot_fault(bg, f, n):
    h, w = bg.shape[:2]
    a = bg.copy()
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    L = Light((w, h))
    for k in range(60):
        d.line((0, h - 60 + k, w, h - 60 + k), fill=(16, 20, 20, int(255 * min(1, k / 20))))
    blink = (f // 4) % 2 == 0
    j1, j2, head = draw_arm(d, L, (int(w * 0.30), h - 70), arm_pose(f, n, fault=True), 1.0,
                            led=RED if blink else (60, 10, 10))
    a = paste_rgba(a, layer)
    Sparks(11, (int(j1[0]), int(j1[1])), [3, 17, 31], n=16, spread=0.8).draw(L, f)
    L.d.rectangle((int(w * 0.52), 20, w - 16, 88), outline=scale(RED, 0.8), width=2)
    L.d.text((int(w * 0.52) + 12, 26), 'ADAPTER FAULT', font=F(MONO, 22), fill=RED if blink else scale(RED, 0.6))
    L.d.text((int(w * 0.52) + 12, 54), 'logged, not scored', font=F(MONO, 20), fill=scale(PAPER, 0.75))
    return L.apply(a, radius=8, strength=0.6)


def p_label_swap(bg, f, n):
    h, w = bg.shape[:2]
    a = bg.copy()
    L = Light((w, h))
    t = f / n
    swap = ease((t - 0.30) / 0.2)
    tag = F(DELA, 52)
    mono = F(MONO, 20)
    lx, rx = 40, w - 260
    pos_med = lx + (rx - lx) * swap
    pos_edu = rx + (lx - rx) * swap
    glitch = 0.30 < t < 0.50 and f % 3 == 0
    for x, word, col in ((pos_med, '医療', TEAL), (pos_edu, '学費', AMBER)):
        off = 8 if glitch else 0
        L.d.rectangle((x - 6, 18, x + 220, 104), outline=scale(col, 0.7), width=2)
        neon_text(L, (x + 8 + off, 22), word, tag, col, 0.95)
        L.d.text((x, 116), 'MEDICAL' if word == '医療' else 'FINANCE', font=mono, fill=scale(PAPER, 0.7))
    L.d.text((w // 2 - 40, 50), 'SWAP' if 0.25 < t < 0.55 else '', font=mono, fill=scale(RED, 0.9))
    # 36-cell rows
    rows = [('IMPACT-AWARE', False), ('LABEL-BIASED', True)]
    cw = (w - 80) / 36
    for r, (name, flips) in enumerate(rows):
        y = 170 + r * 78
        L.d.text((40, y), name, font=mono, fill=scale(PAPER, 0.7))
        for i in range(36):
            x = 40 + i * cw
            orig = TEAL if (i % 3) else AMBER
            col = orig
            if flips and swap > (i / 36) * 0.9 + 0.05:
                col = AMBER if orig == TEAL else TEAL
                col = scale(col, 1)
                L.d.rectangle((x + 1, y + 26, x + cw - 2, y + 56), outline=RED, width=2)
            L.d.rectangle((x + 3, y + 28, x + cw - 4, y + 54), fill=scale(col, 0.75))
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
                         paint=p_neon_fault('学費', AMBER, False)),
    'branch-timeline': dict(region=(420, 380, 1100, 330), frames=72, ms=90, still=-1, paint=p_branch_timeline),
    'time-odometer': dict(region=(900, 380, 620, 340), frames=60, ms=90, still=-1, paint=p_time_odometer),
    'robot-seal': dict(region=(1100, 96, 420, 290), frames=56, ms=80, still=40, paint=p_robot_seal),
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
        # One shared palette for all frames: unchanged pixels stay identical, so the
        # encoder only stores the regions that actually move.
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
