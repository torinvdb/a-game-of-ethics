"""Procedural background plates (1920x1080 JPEG) for the talk.

Drawn with numpy + Pillow from fixed seeds: skyline, sign wall, server hall and
console room. No photographs, film frames or generated imagery. Output is
deterministic for a given seed and library version.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
FONTS = ROOT / 'assets/fonts'
W, H = 1920, 1080

# Palette: teal smog, sodium amber, magenta neon, signal red, phosphor green.
INK = (6, 14, 18)
TEAL = (64, 196, 178)
CYAN = (110, 236, 255)
AMBER = (255, 176, 82)
MAGENTA = (255, 64, 160)
RED = (255, 70, 60)
PHOSPHOR = (120, 255, 160)
PAPER = (232, 236, 214)

SIGN_WORDS = ['倫理', '監査', '警告', '例外', '署名', '承認', '期限', '医療', '奨学金', '待機',
              '拒否', '非常口', '時間', '三年', '電脳', '記録', '責任', '保守', '検証', '通信']


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


# ---------------------------------------------------------------- primitives

def gradient(h: int, w: int, stops: list[tuple[float, tuple[int, int, int]]]) -> np.ndarray:
    ys = np.linspace(0, 1, h)
    out = np.zeros((h, w, 3), np.float32)
    for c in range(3):
        col = np.interp(ys, [s for s, _ in stops], [rgb[c] for _, rgb in stops])
        out[:, :, c] = col[:, None]
    return out


def to_img(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def to_arr(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert('RGB')).astype(np.float32)


def glow(base: np.ndarray, layer: Image.Image, radius: float = 14, strength: float = 1.0,
         core: float = 1.0) -> np.ndarray:
    """Additive bloom of an RGB 'light' layer drawn on black."""
    light = to_arr(layer)
    wide = to_arr(layer.filter(ImageFilter.GaussianBlur(radius)))
    near = to_arr(layer.filter(ImageFilter.GaussianBlur(max(1, radius / 4))))
    return base + light * core + near * 0.8 * strength + wide * 1.6 * strength


def grain(a: np.ndarray, rng: np.random.Generator, amount: float = 7.0) -> np.ndarray:
    n = rng.normal(0, amount, a.shape[:2]).astype(np.float32)
    return a + n[:, :, None]


def vignette(a: np.ndarray, strength: float = 0.55) -> np.ndarray:
    h, w = a.shape[:2]
    y, x = np.ogrid[:h, :w]
    d = ((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2
    return a * (1 - strength * np.clip(d, 0, 1.6)[:, :, None] / 1.6)


def painted(a: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Soften hard digital edges into a gouache-like plate: slight blur,
    low-frequency brush mottling, gentle tonal banding."""
    im = to_img(a).filter(ImageFilter.GaussianBlur(0.7))
    a = to_arr(im)
    small = rng.normal(0, 1, (H // 24 + 1, W // 24 + 1)).astype(np.float32)
    mott = np.asarray(Image.fromarray(small).resize((a.shape[1], a.shape[0]), Image.BICUBIC))
    a = a * (1 + 0.045 * mott[:, :, None])
    return np.round(a / 6) * 6  # cel-like banding in the gradients


def catenary(d: ImageDraw.ImageDraw, p0, p1, sag, color, width=2, steps=60):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = p0[0] + (p1[0] - p0[0]) * t
        y = p0[1] + (p1[1] - p0[1]) * t + sag * 4 * t * (1 - t)
        pts.append((x, y))
    d.line(pts, fill=color, width=width, joint='curve')
    return pts


# ---------------------------------------------------------------- city pieces

def towers(d: ImageDraw.ImageDraw, lights: ImageDraw.ImageDraw, rng, y_base, count, hmin, hmax,
           wmin, wmax, body, window_density, window_colors, x0=-40, x1=W + 40, win=(6, 9),
           antenna=0.3, setbacks=True):
    x = x0
    while x < x1:
        bw = int(rng.integers(wmin, wmax))
        bh = int(rng.integers(hmin, hmax))
        top = y_base - bh
        d.rectangle((x, top, x + bw, y_base + 400), fill=body)
        if setbacks and rng.random() < 0.45:
            inset = int(bw * rng.uniform(0.15, 0.3))
            extra = int(rng.integers(20, 90))
            d.rectangle((x + inset, top - extra, x + bw - inset, top), fill=body)
            if rng.random() < antenna:
                ax = x + bw // 2
                d.line((ax, top - extra - int(rng.integers(30, 120)), ax, top - extra), fill=body, width=3)
                lights.ellipse((ax - 3, top - extra - 6 - 100, ax + 3, top - extra - 100), fill=RED)
        # window grid
        ww, wh = win
        gx, gy = ww + int(rng.integers(4, 8)), wh + int(rng.integers(5, 10))
        for yy in range(top + 12, y_base + 300, gy):
            row_on = rng.random() < 0.85
            for xx in range(x + 6, x + bw - ww - 4, gx):
                if row_on and rng.random() < window_density:
                    col = window_colors[int(rng.integers(len(window_colors)))]
                    k = rng.uniform(0.35, 1.0)
                    lights.rectangle((xx, yy, xx + ww, yy + wh), fill=tuple(int(c * k) for c in col))
        x += bw + int(rng.integers(-6, 14))


def vertical_sign(light: ImageDraw.ImageDraw, back: ImageDraw.ImageDraw, x, y, word, size, color,
                  frame=True, dim=1.0):
    f = font('DelaGothicOne-Regular.ttf', size)
    pad = int(size * 0.28)
    hgt = len(word) * int(size * 1.08) + pad * 2
    wid = size + pad * 2
    back.rectangle((x, y, x + wid, y + hgt), fill=(10, 12, 16), outline=(28, 34, 40), width=2)
    col = tuple(int(c * dim) for c in color)
    if frame:
        light.rectangle((x + 4, y + 4, x + wid - 4, y + hgt - 4), outline=col, width=2)
    for i, ch in enumerate(word):
        light.text((x + pad, y + pad + i * int(size * 1.08)), ch, font=f, fill=col)
    return (x, y, x + wid, y + hgt)


def horizontal_sign(light, back, x, y, text, size, color, face='DelaGothicOne-Regular.ttf', dim=1.0):
    f = font(face, size)
    l, t, r, b = f.getbbox(text)
    pad = int(size * 0.3)
    back.rectangle((x, y, x + r + pad * 2, y + b + pad * 2), fill=(10, 12, 16), outline=(28, 34, 40), width=2)
    col = tuple(int(c * dim) for c in color)
    light.text((x + pad, y + pad - t // 2), text, font=f, fill=col)
    return (x, y, x + r + pad * 2, y + b + pad * 2)


def rain(a: np.ndarray, rng, n=2200, length=(18, 46), alpha=0.10, slant=0.22):
    im = Image.new('L', (a.shape[1], a.shape[0]), 0)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = rng.uniform(-200, a.shape[1]), rng.uniform(-50, a.shape[0])
        L = rng.uniform(*length)
        d.line((x, y, x + L * slant, y + L), fill=int(rng.uniform(80, 255)), width=1)
    m = np.asarray(im).astype(np.float32)[:, :, None] / 255
    return a + m * alpha * 255 * np.array([0.75, 0.9, 1.0])


# ---------------------------------------------------------------- plates

def megacity(seed=7, palette='teal') -> Image.Image:
    """Wide dusk skyline: haze layers, signage cliffs, elevated road trails, cables."""
    rng = np.random.default_rng(seed)
    if palette == 'teal':
        sky = gradient(H, W, [(0, (4, 20, 26)), (0.45, (16, 70, 74)), (0.62, (70, 128, 112)),
                              (0.70, (150, 120, 84)), (1, (18, 22, 26))])
        haze_col, far_col, mid_col, near_col = (96, 150, 132), (40, 86, 86), (18, 44, 48), (6, 14, 18)
    else:  # 'ember' -- red/orange metropolis dusk
        sky = gradient(H, W, [(0, (12, 6, 16)), (0.40, (70, 18, 36)), (0.60, (190, 70, 44)),
                              (0.70, (240, 150, 70)), (1, (16, 10, 14))])
        haze_col, far_col, mid_col, near_col = (200, 100, 70), (98, 40, 46), (40, 18, 26), (10, 6, 10)
    a = sky
    # sun/moon disc softly behind haze
    disc = Image.new('RGB', (W, H), 0)
    dd = ImageDraw.Draw(disc)
    cx, cy, r = int(W * 0.68), int(H * 0.52), 150
    dd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(150, 120, 70) if palette == 'teal' else (255, 170, 90))
    a = a + to_arr(disc.filter(ImageFilter.GaussianBlur(30))) * 0.55

    layers = [(H * 0.70, 140, 360, 40, 120, far_col, 0.16, [(150, 200, 170)], (3, 5)),
              (H * 0.78, 180, 520, 60, 170, mid_col, 0.28, [AMBER, (200, 230, 210), TEAL], (5, 7)),
              (H * 0.98, 300, 780, 90, 260, near_col, 0.18, [AMBER, CYAN, (255, 210, 150)], (7, 10))]
    for li, (yb, hmin, hmax, wmin, wmax, body, dens, wcols, win) in enumerate(layers):
        body_im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        light_im = Image.new('RGB', (W, H), 0)
        bd, ld = ImageDraw.Draw(body_im), ImageDraw.Draw(light_im)
        towers(bd, ld, rng, int(yb), 0, hmin, hmax, wmin, wmax, body + (255,), dens, wcols, win=win)
        mask = np.asarray(body_im)[:, :, 3:4].astype(np.float32) / 255
        a = a * (1 - mask) + np.asarray(body_im)[:, :, :3].astype(np.float32) * mask
        a = glow(a, light_im, radius=6 + li * 4, strength=0.25 + 0.1 * li, core=0.9)
        # atmospheric haze between layers
        band = gradient(H, W, [(0, (0, 0, 0)), (max(0.01, yb / H - 0.25), (0, 0, 0)),
                               (yb / H - 0.03, haze_col), (min(1, yb / H + 0.05), (0, 0, 0)), (1, (0, 0, 0))])
        a = a + band * (0.32 - 0.08 * li)

    # signage cliff on left + right foreground buildings
    back = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    light = Image.new('RGB', (W, H), 0)
    bd, ld = ImageDraw.Draw(back), ImageDraw.Draw(light)
    bd.rectangle((0, 0, 300, H), fill=near_col + (255,))
    bd.rectangle((W - 260, 80, W, H), fill=near_col + (255,))
    cols = [MAGENTA, CYAN, AMBER, RED, TEAL]
    y = 40
    words = list(SIGN_WORDS)
    rng.shuffle(words)
    wi = 0
    for x0 in (30, 150):
        y = int(rng.integers(20, 120))
        while y < H - 200:
            w = words[wi % len(words)]; wi += 1
            box = vertical_sign(ld, bd, x0 + int(rng.integers(-8, 8)), y, w, int(rng.integers(38, 54)),
                                cols[int(rng.integers(len(cols)))], dim=rng.uniform(0.75, 1.0))
            y = box[3] + int(rng.integers(20, 70))
    for x0 in (W - 230, W - 120):
        y = int(rng.integers(140, 240))
        while y < H - 200:
            w = words[wi % len(words)]; wi += 1
            box = vertical_sign(ld, bd, x0, y, w, int(rng.integers(34, 48)), cols[int(rng.integers(len(cols)))],
                                dim=rng.uniform(0.7, 1.0))
            y = box[3] + int(rng.integers(30, 90))
    m = np.asarray(back)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(back)[:, :, :3].astype(np.float32) * m
    a = glow(a, light, radius=22, strength=0.55)

    # elevated expressway with long-exposure trails
    road = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(road)
    trails = Image.new('RGB', (W, H), 0)
    td = ImageDraw.Draw(trails)
    def ry(x): return H * 0.83 - 70 * math.sin(x / W * math.pi * 1.1 + 0.4)
    pts = [(x, ry(x)) for x in range(-20, W + 40, 20)]
    rd.line(pts, fill=(8, 12, 14, 255), width=42)
    for x in range(0, W, 140):
        rd.rectangle((x, ry(x), x + 16, H), fill=(8, 12, 14, 255))
    for k in range(7):
        off = -14 + k * 4
        colr = RED if k < 3 else (255, 236, 200)
        td.line([(x, y + off) for x, y in pts], fill=tuple(int(c * rng.uniform(0.5, 1)) for c in colr), width=2)
    yy = np.arange(H)[:, None, None]
    a = a * (1 - 0.55 * np.clip((yy - H * 0.80) / (H * 0.12), 0, 1))
    m = np.asarray(road)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(road)[:, :, :3].astype(np.float32) * m
    a = glow(a, trails, radius=10, strength=0.8)

    # overhead cables in the foreground
    cab = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cab)
    for i in range(7):
        p0 = (-50, int(rng.integers(60, 320)))
        p1 = (W + 50, int(rng.integers(40, 360)))
        catenary(cd, p0, p1, rng.uniform(60, 200), (3, 6, 8, 255), width=int(rng.integers(2, 6)))
    m = np.asarray(cab)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(cab)[:, :, :3].astype(np.float32) * m

    a = rain(a, rng)
    a = painted(a, rng)
    a = vignette(a, 0.5)
    a = grain(a, rng, 5)
    return to_img(a)


def sign_wall(seed=11) -> Image.Image:
    """Front-on facade of a dense block: stacked signs, AC units, pipes, wet glow."""
    rng = np.random.default_rng(seed)
    a = gradient(H, W, [(0, (10, 16, 20)), (0.5, (14, 26, 30)), (1, (6, 10, 12))])
    back = Image.new('RGB', (W, H), 0)
    light = Image.new('RGB', (W, H), 0)
    bd, ld = ImageDraw.Draw(back), ImageDraw.Draw(light)
    # facade bays
    for x in range(0, W, 240):
        shade = int(rng.integers(14, 26))
        bd.rectangle((x, 0, x + 236, H), fill=(shade, shade + 6, shade + 8))
        for y in range(30, H, 110):
            if rng.random() < 0.55:
                c = [AMBER, (200, 230, 210), TEAL][int(rng.integers(3))]
                k = rng.uniform(0.15, 0.6)
                ld.rectangle((x + 20, y, x + 110, y + 60), fill=tuple(int(v * k) for v in c))
                bd.line((x + 20, y + 30, x + 110, y + 30), fill=(8, 10, 12), width=2)
            # AC units
            if rng.random() < 0.5:
                bd.rectangle((x + 130, y + 10, x + 200, y + 58), fill=(36, 44, 46), outline=(20, 24, 26), width=2)
                for k in range(5):
                    bd.line((x + 136, y + 18 + k * 8, x + 194, y + 18 + k * 8), fill=(22, 28, 30))
    # vertical pipes
    for x in rng.integers(0, W, 9):
        bd.rectangle((int(x), 0, int(x) + 10, H), fill=(26, 30, 30))
    a = a + to_arr(back) * 0.9
    a = glow(a, light, radius=10, strength=0.4)
    # signs
    sl = Image.new('RGB', (W, H), 0)
    sb = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sld, sbd = ImageDraw.Draw(sl), ImageDraw.Draw(sb)
    cols = [MAGENTA, CYAN, AMBER, RED, TEAL, PHOSPHOR]
    words = list(SIGN_WORDS)
    rng.shuffle(words)
    wi = 0
    for x in range(20, W - 60, 120):
        y = int(rng.integers(-40, 120))
        while y < H:
            w = words[wi % len(words)]; wi += 1
            if rng.random() < 0.72:
                box = vertical_sign(sld, sbd, x + int(rng.integers(-10, 10)), y, w, int(rng.integers(34, 58)),
                                    cols[int(rng.integers(len(cols)))], dim=rng.uniform(0.45, 1.0))
            else:
                box = horizontal_sign(sld, sbd, x, y, w, int(rng.integers(30, 46)),
                                      cols[int(rng.integers(len(cols)))], dim=rng.uniform(0.45, 1.0))
            y = box[3] + int(rng.integers(16, 120))
    m = np.asarray(sb)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(sb)[:, :, :3].astype(np.float32) * m
    a = glow(a, sl, radius=26, strength=0.6)
    # cables draped across signs
    cab = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cab)
    for i in range(10):
        catenary(cd, (-30, int(rng.integers(0, H))), (W + 30, int(rng.integers(0, H))), rng.uniform(40, 160),
                 (4, 6, 8, 255), width=int(rng.integers(2, 5)))
    m = np.asarray(cab)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m)
    a = rain(a, rng, n=2600, alpha=0.12)
    a = painted(a, rng)
    a = vignette(a, 0.6)
    a = grain(a, rng, 6)
    return to_img(a)


def machine_room(seed=23) -> Image.Image:
    """One-point perspective server hall: racks, LEDs, cable trays, wet floor."""
    rng = np.random.default_rng(seed)
    a = gradient(H, W, [(0, (6, 12, 14)), (0.5, (12, 30, 30)), (1, (4, 8, 10))])
    vx, vy = W * 0.52, H * 0.46
    body = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    light = Image.new('RGB', (W, H), 0)
    bd, ld = ImageDraw.Draw(body), ImageDraw.Draw(light)

    def proj(x, y, z):  # simple perspective: z in [0,1] from near to far
        s = 1 / (1 + z * 7)
        return vx + (x - vx) * s, vy + (y - vy) * s

    # floor + ceiling planes
    bd.polygon([proj(vx - 900, H * 1.0, 0), proj(vx + 900, H * 1.0, 0), proj(vx + 900, H * 1.0, 1.8),
                proj(vx - 900, H * 1.0, 1.8)], fill=(10, 20, 20, 255))
    bd.polygon([proj(vx - 900, -40, 0), proj(vx + 900, -40, 0), proj(vx + 900, -40, 1.8),
                proj(vx - 900, -40, 1.8)], fill=(8, 14, 16, 255))
    # racks along both sides: inward-facing planes at x = vx +/- 900
    for side in (-1, 1):
        xin = vx + side * 900
        for i in range(16):
            z0, z1 = i * 0.11, i * 0.11 + 0.095
            face = [proj(xin, -40, z0), proj(xin, H * 1.0, z0), proj(xin, H * 1.0, z1), proj(xin, -40, z1)]
            shade = max(8, 30 - i)
            bd.polygon(face, fill=(shade - 4, shade + 4, shade + 6, 255), outline=(3, 6, 6, 255))
            # rack units (horizontal seams)
            for k in range(1, 22):
                yy = -40 + k * (H + 40) / 22
                bd.line([proj(xin, yy, z0), proj(xin, yy, z1)], fill=(4, 8, 8, 255), width=1)
            for k in range(22):
                yy = -40 + (k + 0.5) * (H + 40) / 22
                for j in range(3):
                    if rng.random() < 0.55:
                        zz = z0 + (z1 - z0) * (0.15 + 0.3 * j)
                        x, y = proj(xin, yy, zz)
                        c = [PHOSPHOR, AMBER, CYAN, RED][int(rng.choice(4, p=[0.5, 0.25, 0.2, 0.05]))]
                        s = max(1.0, 5 / (1 + zz * 7))
                        ld.ellipse((x - s, y - s * 0.6, x + s, y + s * 0.6), fill=c)
    m = np.asarray(body)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(body)[:, :, :3].astype(np.float32) * m
    # ceiling cable trays
    cab = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cab)
    for i in range(16):
        x0 = rng.uniform(vx - 900, vx + 900)
        catenary(cd, (x0, -10), (vx + rng.uniform(-40, 40), vy - 120), rng.uniform(10, 60),
                 (14, 20, 22, 255), width=int(rng.integers(3, 9)))
    m = np.asarray(cab)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(cab)[:, :, :3].astype(np.float32) * m
    # far glow at vanishing point
    ld.rectangle((vx - 45, vy - 120, vx + 45, vy + 110), fill=(30, 90, 80))
    a = glow(a, light, radius=16, strength=0.7)
    # wet floor reflection: mirror lower half lights with blur
    refl = np.flipud(a[: int(vy), :, :]) * 0.0
    flo = to_arr(to_img(a).transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(6)))
    yy = np.arange(H)[:, None, None]
    fm = np.clip((yy - H * 0.78) / (H * 0.22), 0, 1) * 0.35
    a = a + flo * fm
    a = painted(a, rng)
    a = vignette(a, 0.65)
    a = grain(a, rng, 5)
    return to_img(a)


def console_room(seed=31) -> Image.Image:
    """Analogue control desk: bank of CRTs, toggles, meters, dim amber work lights."""
    rng = np.random.default_rng(seed)
    a = gradient(H, W, [(0, (8, 10, 12)), (0.55, (18, 22, 22)), (1, (4, 6, 6))])
    body = Image.new('RGB', (W, H), 0)
    light = Image.new('RGB', (W, H), 0)
    bd, ld = ImageDraw.Draw(body), ImageDraw.Draw(light)
    vt = font('VT323-Regular.ttf', 22)
    # CRT bank
    for row in range(3):
        for col in range(7):
            x = 60 + col * 262 + (row % 2) * 30
            y = 60 + row * 205
            bd.rounded_rectangle((x, y, x + 240, y + 185), radius=18, fill=(34, 36, 34), outline=(14, 14, 14), width=4)
            c = [PHOSPHOR, AMBER, CYAN][int(rng.choice(3, p=[0.6, 0.3, 0.1]))]
            k = rng.uniform(0.25, 0.6)
            ld.rounded_rectangle((x + 18, y + 16, x + 222, y + 168), radius=24, fill=tuple(int(v * k * 0.25) for v in c))
            for ln in range(6):
                txt = ''.join(rng.choice(list('0123456789ABCDEF:/-=> ')) for _ in range(int(rng.integers(6, 17))))
                ld.text((x + 30, y + 26 + ln * 22), txt, font=vt, fill=tuple(int(v * k) for v in c))
            for sy in range(y + 16, y + 168, 3):  # scanlines
                bd.line((x + 18, sy, x + 222, sy), fill=(10, 10, 10))
    # desk
    bd.polygon([(0, H * 0.70), (W, H * 0.70), (W, H), (0, H)], fill=(24, 24, 22))
    bd.polygon([(0, H * 0.70), (W, H * 0.70), (W, H * 0.74), (0, H * 0.74)], fill=(44, 42, 36))
    for i in range(60):
        x = 40 + i * 31
        y = H * 0.78 + (i % 3) * 40
        bd.rectangle((x, y, x + 14, y + 26), fill=(60, 58, 50))
        if rng.random() < 0.4:
            ld.ellipse((x + 3, y - 12, x + 11, y - 4), fill=[RED, AMBER, PHOSPHOR][int(rng.integers(3))])
    a = a + to_arr(body)
    a = glow(a, light, radius=12, strength=0.6)
    # overhead amber work lamp pool
    lamp = Image.new('RGB', (W, H), 0)
    ImageDraw.Draw(lamp).ellipse((W * 0.2, H * 0.55, W * 0.8, H * 1.1), fill=(70, 50, 20))
    a = a + to_arr(lamp.filter(ImageFilter.GaussianBlur(90)))
    a = painted(a, rng)
    a = vignette(a, 0.7)
    a = grain(a, rng, 6)
    return to_img(a)


PLATES = {
    'megacity-teal': lambda: megacity(7, 'teal'),
    'megacity-ember': lambda: megacity(19, 'ember'),
    'sign-wall': sign_wall,
    'machine-room': machine_room,
    'console-room': console_room,
}


def build(out: Path | None = None) -> dict:
    out = out or ROOT / 'assets/plates'
    out.mkdir(parents=True, exist_ok=True)
    made = {}
    for name, fn in PLATES.items():
        path = out / f'{name}.jpg'
        fn().save(path, quality=90, optimize=True, progressive=True)
        made[name] = str(path.relative_to(ROOT))
        print('plate', path.name)
    return made


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        for name in sys.argv[1:]:
            (ROOT / 'assets/plates').mkdir(parents=True, exist_ok=True)
            PLATES[name]().save(ROOT / f'assets/plates/{name}.jpg', quality=90)
            print(name)
    else:
        build()
