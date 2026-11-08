"""Procedural README art: header banner, animated banner and section strips.

Everything is drawn in code with numpy + Pillow. The skyline plate comes from
talks/three-years-in-thirty-minutes/scenery.py and the inspector sprite from
img/make_logo.py; no external images are used. Outputs (in img/readme/):
  banner.png            1280x400 static header
  banner.gif            animated header (written only if under 1.5 MB)
  section-NN-<slug>.png 1280x64 section header strips
Run: python3 img/make_readme_art.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
TALK = REPO / 'talks/three-years-in-thirty-minutes'
sys.path[:0] = [str(ROOT), str(TALK)]

import make_logo  # noqa: E402  (sprite(), GW, GH)
import scenery  # noqa: E402  (megacity(), glow helpers, palette)

OUT = ROOT / 'readme'
FONTS = TALK / 'assets/fonts'
# The deck's Dela Gothic One is subset to the deck's own kanji; the demo subset covers the section labels.
KANJI_FONT = TALK / 'demo/city/type/DelaGothicOne-demo.ttf'
BW, BH = 1280, 400
SW, SH = 1280, 112
GIF_LIMIT = 1_500_000

BG = (7, 6, 13)
TEAL = (64, 196, 178)     # #40C4B2
AMBER = (255, 176, 82)    # #FFB052
MAGENTA = (255, 79, 168)  # #FF4FA8
RED = (255, 90, 72)       # #FF5A48
CYAN = scenery.CYAN
PAPER = scenery.PAPER

SECTIONS = [
    ('01', '概要', 'OVERVIEW', 'overview', TEAL),
    ('02', '採点', 'SCORING', 'scoring', AMBER),
    ('03', 'シナリオ', 'SCENARIOS', 'scenarios', MAGENTA),
    ('04', '時間旅行', 'TIME-TRAVEL', 'time-travel', TEAL),
    ('05', '結果', 'RESULTS', 'results', RED),
    ('06', '手順', 'PROTOCOL', 'protocol', AMBER),
    ('07', '導入', 'QUICKSTART', 'quickstart', MAGENTA),
    ('08', '謝辞', 'CREDITS', 'credits', TEAL),
]


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size)


def arr(im: Image.Image) -> np.ndarray:
    return np.asarray(im.convert('RGB')).astype(np.float32)


def img(a: np.ndarray) -> Image.Image:
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def bloom(a: np.ndarray, light: Image.Image, radius: float, strength: float) -> np.ndarray:
    """Additive neon: sharp core plus two blurred halos."""
    return (a + arr(light) + arr(light.filter(ImageFilter.GaussianBlur(radius / 3))) * 0.7 * strength
            + arr(light.filter(ImageFilter.GaussianBlur(radius))) * 1.3 * strength)


def scanlines(a: np.ndarray, step: int = 3, depth: float = 0.22) -> np.ndarray:
    mask = np.ones(a.shape[0], np.float32)
    mask[::step] = 1 - depth
    return a * mask[:, None, None]


def plate() -> np.ndarray:
    """Teal dusk skyline from the talk plates, cropped to a 16:5 band and darkened on the left."""
    city = scenery.megacity(7, 'teal')                      # 1920x1080
    band = city.crop((0, 300, 1920, 900)).resize((BW, BH), Image.LANCZOS)
    a = arr(band)
    x = np.linspace(0, 1, BW)[None, :, None]
    shade = 0.28 + 0.72 * np.clip((x - 0.05) / 0.6, 0, 1) ** 1.4  # title side darker
    a = a * shade
    y = np.linspace(0, 1, BH)[:, None, None]
    a = a * (1 - 0.35 * np.clip((y - 0.75) / 0.25, 0, 1))
    return a


def banner_frame(base: np.ndarray, frame: int) -> Image.Image:
    a = base.copy()
    back = Image.new('RGBA', (BW, BH), (0, 0, 0, 0))
    light = Image.new('RGB', (BW, BH), 0)
    bd, ld = ImageDraw.Draw(back), ImageDraw.Draw(light)

    # terminal bracket frame and HUD ticks
    ld.rectangle((18, 18, BW - 18, BH - 18), outline=tuple(int(c * 0.45) for c in TEAL), width=1)
    for x0, y0, dx, dy in ((18, 18, 1, 1), (BW - 18, 18, -1, 1), (18, BH - 18, 1, -1), (BW - 18, BH - 18, -1, -1)):
        ld.line((x0, y0, x0 + 34 * dx, y0), fill=TEAL, width=3)
        ld.line((x0, y0, x0, y0 + 34 * dy), fill=TEAL, width=3)

    mono = font('ShareTechMono-Regular.ttf', 18)
    ld.text((52, 44), '> ethi-cli --boot   // SCENARIO-BASED ETHICS EVALUATION', font=mono,
            fill=tuple(int(c * 0.85) for c in TEAL))

    # title: two-line neon in Oswald, magenta under-glow + paper core
    title = font('Oswald-Bold.ttf', 104)
    bd.rectangle((44, 82, 720, 300), fill=(4, 6, 10, 150))
    flick = 0.55 if frame % 8 == 5 else 1.0
    ld.text((56, 76), 'A GAME OF', font=title, fill=tuple(int(c * flick) for c in MAGENTA))
    ld.text((56, 176), 'ETHICS', font=title, fill=tuple(int(c * 1.0) for c in TEAL))
    sub = font('Rajdhani-SemiBold.ttf', 27)
    ld.text((58, 312), 'Scenario-based ethics evaluation for LLMs and agents · v2', font=sub, fill=AMBER)
    ld.line((58, 350, 610, 350), fill=tuple(int(c * 0.6) for c in AMBER), width=2)
    tag = font('ShareTechMono-Regular.ttf', 16)
    ld.text((58, 358), '13 TIERED SCENARIOS  //  8 AXES  //  36-MONTH CLUSTER CASE', font=tag,
            fill=tuple(int(c * 0.8) for c in CYAN))

    # 倫理 vertical sign beside the inspector (flickers on one frame)
    on = frame % 8 != 3
    sx, sy = 930, 96
    bd.rectangle((sx, sy, sx + 86, sy + 190), fill=(10, 12, 16, 255), outline=(28, 34, 40, 255), width=2)
    sc = MAGENTA if on else (90, 24, 60)
    ld.rectangle((sx + 5, sy + 5, sx + 81, sy + 185), outline=sc, width=3)
    dela = font('DelaGothicOne-Regular.ttf', 60)
    ld.text((sx + 13, sy + 14), '倫', font=dela, fill=sc)
    ld.text((sx + 13, sy + 98), '理', font=dela, fill=sc)

    m = np.asarray(back)[:, :, 3:4].astype(np.float32) / 255
    a = a * (1 - m) + np.asarray(back)[:, :, :3].astype(np.float32) * m
    a = bloom(a, light, 16, 0.42)

    # chibi inspector, 4x nearest-neighbour, with cyan rim light
    spr = make_logo.sprite(frame)
    big = spr.resize((make_logo.GW * 4, make_logo.GH * 4), Image.NEAREST)
    rim = Image.new('RGBA', big.size, CYAN + (0,))
    rim.putalpha(big.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(7))
                 .point(lambda v: v // 2))
    out = img(a)
    ox, oy = 1052, BH - big.height - 26
    out.paste(rim, (ox, oy), rim)
    out.paste(big, (ox, oy), big)

    a = scanlines(arr(out))
    return img(a)


def strip(num: str, kanji: str, label: str, color) -> Image.Image:
    a = np.zeros((SH, SW, 3), np.float32) + np.array(BG, np.float32)
    x = np.linspace(0, 1, SW)[None, :, None]
    a = a + np.array(color, np.float32) * 0.12 * np.clip(1 - x * 1.6, 0, 1)
    back = Image.new('RGB', (SW, SH), 0)
    light = Image.new('RGB', (SW, SH), 0)
    ld = ImageDraw.Draw(light)
    dim = tuple(int(c * 0.45) for c in color)
    ld.rectangle((16, 22, 104, SH - 22), outline=color, width=3)
    mono = font('ShareTechMono-Regular.ttf', 44)
    ld.text((60, SH // 2), num, font=mono, fill=AMBER if color != AMBER else MAGENTA, anchor='mm')
    kf = ImageFont.truetype(str(KANJI_FONT), 64)
    ld.text((132, SH // 2), kanji, font=kf, fill=color, anchor='lm')
    lx = 132 + int(ld.textlength(kanji, font=kf)) + 32
    ld.text((lx, SH // 2), label, font=font('Oswald-Bold.ttf', 60), fill=PAPER, anchor='lm')
    # right-hand HUD: tick ruler and a status readout
    for i, xx in enumerate(range(SW - 420, SW - 160, 10)):
        h = 22 if i % 5 == 0 else 11
        ld.line((xx, SH - 24 - h, xx, SH - 24), fill=dim, width=2)
    ld.text((SW - 30, SH // 2 - 8), f'SEC.{num}', font=font('ShareTechMono-Regular.ttf', 26), fill=dim, anchor='rm')
    a = a + arr(back)
    a = bloom(a, light, 10, 0.3)
    return img(scanlines(a, 3, 0.25))


def save_png(im: Image.Image, path: Path, colors: int = 256) -> int:
    im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG) \
        .save(path, optimize=True)
    return path.stat().st_size


def main():
    OUT.mkdir(exist_ok=True)
    base = plate()
    frames = [banner_frame(base, f) for f in range(8)]
    sizes = {'banner.png': save_png(frames[0], OUT / 'banner.png')}

    # GIF: one shared palette so unchanged pixels stay identical and Pillow stores only frame diffs
    pal = frames[0].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    gif = OUT / 'banner.gif'
    q[0].save(gif, save_all=True, append_images=q[1:], duration=150, loop=0, optimize=True)
    if gif.stat().st_size > GIF_LIMIT:
        print(f'banner.gif {gif.stat().st_size} B exceeds {GIF_LIMIT} B; removed')
        gif.unlink()
    else:
        sizes['banner.gif'] = gif.stat().st_size

    for num, kanji, label, slug, color in SECTIONS:
        name = f'section-{num}-{slug}.png'
        sizes[name] = save_png(strip(num, kanji, label, color), OUT / name, colors=64)

    for k, v in sizes.items():
        print(f'{k:32s} {v / 1024:8.1f} KiB')
    print(f'{"total":32s} {sum(sizes.values()) / 1024:8.1f} KiB')


if __name__ == '__main__':
    main()
