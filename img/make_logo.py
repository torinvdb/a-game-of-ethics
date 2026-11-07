"""Procedural chibi pixel sprite logo: an original cyborg inspector.

Sprite is built on a 48x56 index grid from primitives, outlined, then scaled 6x
(nearest neighbour) onto a neon badge. Outputs:
  img/a-game-of-ethics.png     512x512 logo (README, site)
  img/logo-sprite.gif          animated badge (lens scan, port LED, idle bob)
  img/logo-sprite-sheet.png    raw 48x56 frames, 1x
  static/images/a-game-of-ethics.png  copy used as the site og:image
  static/images/favicon.ico    head crop, 16/32/48 px
Run: python3 img/make_logo.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).parent
FONTS = ROOT.parent / 'talks/three-years-in-thirty-minutes/assets/fonts'
GW, GH, PX = 48, 56, 6

PAL = {
    'ink': (10, 12, 16), 'hair': (28, 34, 52), 'hair_hi': (64, 78, 112),
    'skin': (240, 200, 160), 'skin_sh': (198, 150, 118), 'metal': (70, 78, 88), 'metal_hi': (150, 160, 170),
    'lens': (255, 168, 64), 'lens_sh': (190, 96, 30), 'lens_hi': (255, 244, 210),
    'coat': (82, 96, 70), 'coat_sh': (56, 66, 50), 'coat_hi': (120, 136, 100),
    'shirt': (226, 230, 220), 'tie': (196, 46, 46), 'badge': (240, 196, 70),
    'pants': (32, 36, 46), 'shoe': (18, 20, 24), 'cyan': (110, 236, 255), 'port': (36, 40, 46),
}


class Grid:
    def __init__(self):
        self.g = [[None] * GW for _ in range(GH)]

    def px(self, x, y, c):
        if 0 <= x < GW and 0 <= y < GH:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, half=None):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    if half == 'top' and y > cy:
                        continue
                    self.px(x, y, c)

    def outline(self):
        out = [row[:] for row in self.g]
        for y in range(GH):
            for x in range(GW):
                if self.g[y][x] is None and any(
                        0 <= x + dx < GW and 0 <= y + dy < GH and self.g[y + dy][x + dx] not in (None, 'ink')
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    out[y][x] = 'ink'
        self.g = out

    def image(self):
        im = Image.new('RGBA', (GW, GH), (0, 0, 0, 0))
        for y in range(GH):
            for x in range(GW):
                c = self.g[y][x]
                if c:
                    im.putpixel((x, y), PAL[c] + (255,))
        return im


def sprite(frame: int) -> Image.Image:
    bob = 1 if frame % 4 in (1, 2) else 0
    s = Grid()
    o = bob
    # legs and shoes
    s.rect(18, 47, 22, 52, 'pants'); s.rect(26, 47, 30, 52, 'pants')
    s.rect(17, 52, 23, 54, 'shoe'); s.rect(25, 52, 31, 54, 'shoe')
    # trench coat body, cel-shaded right side, belt and hem
    for y in range(31 + o, 49):
        half = 10 + (y - 31) // 5
        s.rect(24 - half, y, 23 + half, y, 'coat')
        s.rect(24 + half - 3, y, 23 + half, y, 'coat_sh')
    s.rect(14, 42 + o, 33, 42 + o, 'coat_sh')
    s.rect(23, 33 + o, 24, 48, 'coat_sh')
    # shirt, tie, raised lapels
    for y in range(31 + o, 38 + o):
        w = max(0, 3 - (y - 31 - o) // 2)
        s.rect(24 - w, y, 23 + w, y, 'shirt')
    s.rect(23, 32 + o, 24, 39 + o, 'tie'); s.px(23, 40 + o, 'tie'); s.px(24, 40 + o, 'tie')
    for k in range(5):
        s.px(19 + k // 2, 30 + o + k, 'coat_hi'); s.px(28 - k // 2, 30 + o + k, 'coat_hi')
    s.rect(16, 28 + o, 18, 32 + o, 'coat_hi'); s.rect(29, 28 + o, 31, 32 + o, 'coat_hi')  # collar up
    # badge
    s.rect(17, 35 + o, 19, 37 + o, 'badge')
    # arms + hands; right hand holds a field terminal
    s.rect(12, 33 + o, 14, 41 + o, 'coat'); s.rect(33, 33 + o, 35, 39 + o, 'coat_sh')
    s.rect(12, 42 + o, 14, 43 + o, 'skin'); s.rect(33, 40 + o, 35, 41 + o, 'skin')
    s.rect(33, 36 + o, 39, 41 + o, 'metal'); s.rect(34, 37 + o, 38, 40 + o, 'cyan' if frame % 8 != 5 else 'port')
    # head: big chibi skull, jaw shading
    s.ellipse(24, 17 + o, 13, 12.5, 'skin')
    s.ellipse(29, 20 + o, 7, 8, 'skin_sh')
    s.ellipse(23, 19 + o, 10, 9, 'skin')
    # hair: swept cap with a side part and fringe points
    s.ellipse(24, 12 + o, 14, 9, 'hair', half='top')
    s.rect(10, 11 + o, 37, 13 + o, 'hair')
    for x, d in ((12, 3), (16, 4), (21, 2), (27, 3), (32, 4), (36, 2)):
        s.rect(x, 14 + o, x + 1, 14 + o + d, 'hair')
    s.rect(14, 6 + o, 22, 7 + o, 'hair_hi'); s.rect(12, 9 + o, 14, 10 + o, 'hair_hi')
    # cyber goggles: strap, metal rims, amber lenses, scan line
    s.rect(10, 18 + o, 38, 19 + o, 'metal')
    for cx in (18, 30):
        s.ellipse(cx, 19 + o, 5, 4.2, 'metal')
        s.ellipse(cx, 19 + o, 3.8, 3.1, 'lens')
        s.rect(cx - 3, 21 + o, cx + 3, 22 + o, 'lens_sh')
        s.px(cx - 2, 17 + o, 'lens_hi'); s.px(cx - 1, 17 + o, 'lens_hi')
        scan = cx - 3 + (frame % 8)
        if frame % 8 < 7:
            s.rect(scan, 17 + o, scan, 21 + o, 'lens_hi')
    s.rect(23, 18 + o, 25, 19 + o, 'metal_hi')
    # mouth, jaw seam, neck ports with status LED
    s.rect(22, 26 + o, 25, 26 + o, 'skin_sh')
    s.rect(15, 23 + o, 15, 27 + o, 'skin_sh')
    s.rect(20, 29 + o, 27, 30 + o, 'skin_sh')
    s.rect(12, 22 + o, 13, 24 + o, 'port')
    s.px(12, 23 + o, 'cyan' if frame % 4 < 2 else 'port')
    s.outline()
    return s.image()


def badge(sprite_im: Image.Image, frame: int, size=512) -> Image.Image:
    bg = Image.new('RGB', (size, size), (6, 10, 14))
    d = ImageDraw.Draw(bg)
    for y in range(size):  # dusk gradient
        k = y / size
        d.line((0, y, size, y), fill=(int(8 + 30 * k), int(14 + 30 * (1 - k)), int(22 + 20 * (1 - k))))
    light = Image.new('RGB', (size, size), 0)
    ld = ImageDraw.Draw(light)
    try:
        dela = ImageFont.truetype(str(FONTS / 'DelaGothicOne-Regular.ttf'), int(58 * size / 512))
        mono = ImageFont.truetype(str(FONTS / 'ShareTechMono-Regular.ttf'), 22)
    except OSError:
        dela = mono = ImageFont.load_default()
    # skyline silhouettes with windows
    for i, (x, h) in enumerate(((20, 210), (70, 160), (120, 250), (330, 230), (390, 170), (440, 260))):
        d.rectangle((x, size - h, x + 46, size), fill=(12, 16, 22))
        for yy in range(size - h + 10, size - 20, 14):
            for xx in range(x + 6, x + 40, 10):
                if (xx * 7 + yy * 13 + i) % 5 == 0:
                    ld.rectangle((xx, yy, xx + 4, yy + 6), fill=(120, 90, 40))
    # vertical neon sign
    on = frame % 8 != 3
    k = size / 512
    ld.rectangle(tuple(int(v * k) for v in (352, 70, 422, 226)), outline=(255, 64, 160) if on else (90, 20, 60), width=4)
    ld.text((int(360 * k), int(76 * k)), '倫', font=dela, fill=(255, 64, 160) if on else (90, 20, 60))
    ld.text((int(360 * k), int(148 * k)), '理', font=dela, fill=(255, 64, 160) if on else (90, 20, 60))
    # ring
    ld.ellipse((26, 26, size - 26, size - 26), outline=(64, 196, 178), width=5)
    ld.arc((40, 40, size - 40, size - 40), 200 + frame * 6, 260 + frame * 6, fill=(110, 236, 255), width=3)
    ld.text((34, size - 52), 'AGoE // v2', font=mono, fill=(255, 176, 82))
    glow = light.filter(ImageFilter.GaussianBlur(10))
    bg = Image.fromarray(__import__('numpy').clip(
        __import__('numpy').asarray(bg, dtype='float32') + __import__('numpy').asarray(light, dtype='float32')
        + __import__('numpy').asarray(glow, dtype='float32') * 1.4, 0, 255).astype('uint8'))
    # sprite + cyan rim glow
    px = max(2, size * PX // 512)
    big = sprite_im.resize((GW * px, GH * px), Image.NEAREST)
    rim = Image.new('RGBA', big.size, (110, 236, 255, 0))
    rim.putalpha(big.getchannel('A').filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(8)).point(lambda v: v // 3))
    ox, oy = (size - big.width) // 2 - 10, size - big.height - 30
    bg.paste(rim, (ox, oy), rim)
    bg.paste(big, (ox, oy), big)
    # scanlines
    sl = Image.new('L', (size, size), 0)
    sd = ImageDraw.Draw(sl)
    for y in range(0, size, 3):
        sd.line((0, y, size, y), fill=60)
    bg.paste((0, 0, 0), (0, 0), sl)
    # circular mask with transparent corners
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((22, 22, size - 22, size - 22), fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out


def main():
    frames = [sprite(f) for f in range(8)]
    sheet = Image.new('RGBA', (GW * 8, GH), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        sheet.paste(f, (i * GW, 0))
    sheet.save(ROOT / 'logo-sprite-sheet.png')
    logo = badge(frames[0], 0)
    logo.save(ROOT / 'a-game-of-ethics.png', optimize=True)
    logo.save(ROOT.parent / 'static/images/a-game-of-ethics.png', optimize=True)  # og:image for the site
    icon = Image.new('RGBA', (48, 48), (6, 10, 14, 255))
    icon.paste(frames[0].crop((0, 0, 48, 34)), (0, 7), frames[0].crop((0, 0, 48, 34)))
    icon.save(ROOT.parent / 'static/images/favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    anim = [badge(f, i, 320) for i, f in enumerate(frames)]
    flat = []
    for a in anim:
        bgc = Image.new('RGB', a.size, (13, 17, 23))  # GitHub dark page colour behind transparent corners
        bgc.paste(a, (0, 0), a)
        flat.append(bgc.quantize(colors=128, method=Image.Quantize.MEDIANCUT))
    flat[0].save(ROOT / 'logo-sprite.gif', save_all=True, append_images=flat[1:], duration=140, loop=0, optimize=True)
    print('wrote a-game-of-ethics.png, logo-sprite.gif, logo-sprite-sheet.png')


if __name__ == '__main__':
    main()
