// Procedural pixel city for the demo. Everything is drawn from code at 480x210 and
// scaled with nearest-neighbour. All randomness is seeded and all motion reads `t` (seconds), so a
// recording made with a fixed time step is reproducible frame for frame.

export const W = 480;
export const H = 210;
export const GROUND = 172;
// Sign text is drawn on an overlay at SIGN_RES times the city's resolution: at 480x210 the
// characters merge into blocks and cannot be read.
export const SIGN_RES = 4;

export const PAL = {
  night: '#070d10', dusk: '#241a3a', teal: '#40c4b2', amber: '#ffb052', red: '#ff5a48', bone: '#e8ecd6',
  deep: '#0b121a', hull: '#121b27', hull2: '#18233a', haze: '#2b2244', frost: '#9fd8ff', gold: '#ffd27a',
};

export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const hash = (a, b, c = 0) => {
  let h = (a * 374761393 + b * 668265263 + c * 2147483647) >>> 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
};
const lerp = (a, b, k) => a + (b - a) * k;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
function hex(c) { const n = parseInt(c.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function mix(c1, c2, k) {
  const a = hex(c1), b = hex(c2);
  return `rgb(${Math.round(lerp(a[0], b[0], k))},${Math.round(lerp(a[1], b[1], k))},${Math.round(lerp(a[2], b[2], k))})`;
}
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];

// ---------------------------------------------------------------- glyph sprites
// Kanji signs are rasterised once, then thresholded so they stay crisp pixels.
const spriteCache = new Map();
export function glyphSprite(text, px, color, vertical = false) {
  const key = `${text}|${px}|${color}|${vertical}`;
  if (spriteCache.has(key)) return spriteCache.get(key);
  const chars = [...text];
  const cw = px + 1;
  const w = vertical ? cw + 2 : chars.length * cw + 2;
  const h = vertical ? chars.length * cw + 2 : cw + 2;
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  const g = c.getContext('2d');
  g.font = `${px}px "Dela Gothic One"`;
  g.textBaseline = 'top';
  g.fillStyle = '#fff';
  chars.forEach((ch, i) => g.fillText(ch, vertical ? 1 : 1 + i * cw, vertical ? 1 + i * cw : 1));
  const img = g.getImageData(0, 0, w, h);
  const [r, gg, b] = hex(color);
  for (let i = 0; i < img.data.length; i += 4) {
    const on = img.data[i + 3] > 110;
    img.data[i] = r; img.data[i + 1] = gg; img.data[i + 2] = b; img.data[i + 3] = on ? 255 : 0;
  }
  g.putImageData(img, 0, 0);
  spriteCache.set(key, c);
  return c;
}

// Sign text for the overlay, in DotGothic16: a pixel font drawn on a 16-pixel grid, so it is set at
// whole multiples of 16 and stays legible where a display face fills in.
export function dotSprite(text, cell, color, vertical) {
  const key = `dot|${text}|${cell}|${color}|${vertical}`;
  if (spriteCache.has(key)) return spriteCache.get(key);
  const chars = [...text];
  const size = Math.max(16, Math.floor(cell / 16) * 16), off = Math.floor((cell - size) / 2);
  const c = document.createElement('canvas');
  c.width = vertical ? cell : chars.length * cell; c.height = vertical ? chars.length * cell : cell;
  const g = c.getContext('2d');
  g.font = `${size}px "DotGothic16"`;
  g.textBaseline = 'top';
  g.fillStyle = '#fff';
  chars.forEach((ch, i) => g.fillText(ch, (vertical ? 0 : i * cell) + off, (vertical ? i * cell : 0) + off));
  const img = g.getImageData(0, 0, c.width, c.height);
  const [r, gg, b] = hex(color);
  for (let i = 0; i < img.data.length; i += 4) {
    const on = img.data[i + 3] > 110;
    img.data[i] = r; img.data[i + 1] = gg; img.data[i + 2] = b; img.data[i + 3] = on ? 255 : 0;
  }
  g.putImageData(img, 0, 0);
  spriteCache.set(key, c);
  return c;
}

// Tiny 3x5 pixel font for numerals and a few capitals on in-world displays.
const FONT3 = {
  0: '111101101101111', 1: '010110010010111', 2: '111001111100111', 3: '111001111001111', 4: '101101111001001',
  5: '111100111001111', 6: '111100111101111', 7: '111001010010010', 8: '111101111101111', 9: '111101111001111',
  '/': '001001010100100', '-': '000000111000000', ' ': '000000000000000', ':': '000010000010000',
  A: '010101111101101', C: '111100100100111', D: '110101101101110', E: '111100111100111', F: '111100111100100',
  G: '111100101101111', H: '101101111101101', I: '111010010010111', K: '101101110101101', L: '100100100100111',
  M: '101111111101101', N: '111101101101101', O: '111101101101111', P: '111101111100100', R: '111101110101101',
  S: '111100111001111', T: '111010010010010', U: '101101101101111', V: '101101101101010', W: '101101111111101',
  X: '101101010101101', Y: '101101010010010', B: '110101110101110', $: '011110010011110', '.': '000000000000010',
};
export function text3(g, s, x, y, color) {
  g.fillStyle = color;
  [...String(s).toUpperCase()].forEach((ch, i) => {
    const m = FONT3[ch] ?? FONT3[' '];
    for (let k = 0; k < 15; k++) if (m[k] === '1') g.fillRect(x + i * 4 + (k % 3), y + Math.floor(k / 3), 1, 1);
  });
}

// ---------------------------------------------------------------- the city
export class City {
  constructor(canvas, seed = 1987) {
    this.canvas = canvas;
    canvas.width = W; canvas.height = H;
    this.g = canvas.getContext('2d');
    this.g.imageSmoothingEnabled = false;
    this.emit = document.createElement('canvas');
    this.emit.width = W; this.emit.height = H;
    this.e = this.emit.getContext('2d');
    this.glow = document.createElement('canvas');
    this.glow.width = W; this.glow.height = H;
    this.gl = this.glow.getContext('2d');
    this.seed = seed;
    this.dawn = 0;          // 0 night .. 1 dawn
    this.alarm = 0;         // red flash, decays
    this.flash = 0;         // white flash, decays
    this.rainRate = 1;
    this.scene = null;
    this.skyKey = null;
    this.sky = document.createElement('canvas');
    this.sky.width = W; this.sky.height = GROUND;
    this.far = this.skyline(seed + 1, 34, 30, 92, 10, 22);
    this.mid = this.skyline(seed + 2, 24, 40, 110, 14, 30);
    const r = mulberry32(seed + 3);
    this.stars = Array.from({ length: 70 }, () => [Math.floor(r() * W), Math.floor(r() * 80), r()]);
    this.rr = mulberry32(seed + 4);
    this.drops = Array.from({ length: 160 }, () => [r() * W, r() * H, 0.6 + r() * 0.8]);
    this.cars = Array.from({ length: 7 }, (_, i) => ({ lane: 40 + Math.floor(r() * 50), speed: (r() < 0.5 ? -1 : 1) * (18 + r() * 30),
      x: r() * W, color: i % 3 === 0 ? PAL.red : i % 3 === 1 ? PAL.amber : PAL.teal }));
  }

  skyline(seed, n, minH, maxH, minW, maxW) {
    const r = mulberry32(seed);
    const out = [];
    let x = -10;
    while (out.length < n) {
      const w = Math.floor(minW + r() * (maxW - minW));
      out.push({ x, w, h: Math.floor(minH + r() * (maxH - minH)), ant: r() < 0.35, roof: Math.floor(r() * 3), id: out.length, sign: r() < 0.25 });
      x += w + Math.floor(r() * 6) - 1;
    }
    this.worldW = Math.max(this.worldW ?? 0, x);
    return out;
  }

  drawSky() {
    const key = Math.round(this.dawn * 40);
    if (key === this.skyKey) return;
    this.skyKey = key;
    const g = this.sky.getContext('2d');
    const d = this.dawn;
    const bands = [
      mix('#04070b', '#1a2140', d), mix('#08101a', '#2c2a52', d), mix('#0f1424', '#4a3358', d),
      mix('#1a1733', '#7a4458', d), mix(PAL.dusk, '#c46a52', d), mix('#3a2440', PAL.amber, d),
    ];
    const img = g.createImageData(W, GROUND);
    const cols = bands.map((b) => b.match(/\d+/g).map(Number));
    for (let y = 0; y < GROUND; y++) {
      const f = (y / GROUND) * (bands.length - 1);
      const i = Math.floor(f), k = f - i;
      for (let x = 0; x < W; x++) {
        const c = cols[k * 16 > BAYER[(y % 4) * 4 + (x % 4)] ? Math.min(i + 1, bands.length - 1) : i];
        const o = (y * W + x) * 4;
        img.data[o] = c[0]; img.data[o + 1] = c[1]; img.data[o + 2] = c[2]; img.data[o + 3] = 255;
      }
    }
    g.putImageData(img, 0, 0);
  }

  // Generic building with a window grid. `lit` is the share of windows on (0..1).
  building(g, e, x, y, w, h, { body = PAL.hull, lit = 0.5, warm = 0.6, seed = 0, t = 0, flicker = 0, dead = null, rim = null } = {}) {
    g.fillStyle = body;
    g.fillRect(x, y, w, h);
    if (rim) { g.fillStyle = rim; g.fillRect(x, y, w, 1); g.fillRect(x + w - 1, y, 1, h); }
    g.fillStyle = 'rgba(255,255,255,0.05)';
    g.fillRect(x, y, 1, h);
    const cols = Math.floor((w - 2) / 3), rows = Math.floor((h - 4) / 4);
    for (let cy = 0; cy < rows; cy++) for (let cx = 0; cx < cols; cx++) {
      const hv = hash(seed, cx, cy);
      let on = hv < lit;
      if (on && flicker && hash(seed, cx * 7 + cy, Math.floor(t * 6)) < flicker) on = false;
      if (dead && dead(cx, cy, cols, rows)) on = false;
      const wx = x + 2 + cx * 3, wy = y + 3 + cy * 4;
      if (on) {
        const col = hash(seed + 9, cx, cy) < warm ? PAL.amber : PAL.teal;
        g.fillStyle = col; g.fillRect(wx, wy, 1, 2);
        e.fillStyle = col; e.fillRect(wx, wy, 1, 2);
      } else {
        g.fillStyle = '#0a0f17'; g.fillRect(wx, wy, 1, 2);
      }
    }
  }

  // A sign is a dark plate on the city layer, a glowing frame on the emissive layer, and its text
  // queued for the sharp overlay. Without an overlay the text falls back to the pixel layer.
  sign(g, e, text, x, y, color, { px = 10, vertical = true, on = 1, t = 0, broken = 0, seed = 0 } = {}) {
    const lit = on > 0 && !(broken && hash(seed, Math.floor(t * 9)) < broken);
    const n = [...text].length, cw = px + 1;
    const w = vertical ? cw + 2 : n * cw + 2, h = vertical ? n * cw + 2 : cw + 2;
    g.fillStyle = '#05070b';
    g.fillRect(x - 1, y - 1, w + 2, h + 2);
    if (lit) {
      e.globalAlpha = on; e.strokeStyle = color; e.lineWidth = 1;
      e.strokeRect(x - 0.5, y - 0.5, w + 1, h + 1); e.globalAlpha = 1;
    }
    if (this.signQueue) { this.signQueue.push({ text, x, y, px, vertical, color: lit ? color : '#2a2f3a', alpha: lit ? Math.max(0.35, on) : 1 }); return; }
    g.drawImage(glyphSprite(text, px, lit ? color : '#2a2f3a', vertical), x, y);
  }

  attachSigns(canvas) {
    canvas.width = W * SIGN_RES; canvas.height = H * SIGN_RES;
    this.sc = canvas.getContext('2d');
    this.signQueue = [];
  }

  clearSigns() { if (this.sc) { this.sc.clearRect(0, 0, W * SIGN_RES, H * SIGN_RES); this.signQueue = []; } }

  // Draw queued sign text, then tint it with the same full-screen washes the city layer got.
  flushSigns(washes = []) {
    if (!this.sc) return;
    const c = this.sc, R = SIGN_RES;
    c.clearRect(0, 0, W * R, H * R);
    for (const s of this.signQueue) {
      c.globalAlpha = s.alpha;
      c.drawImage(dotSprite(s.text, (s.px + 1) * R, s.color, s.vertical), (s.x + 1) * R, (s.y + 1) * R);
    }
    c.globalAlpha = 1;
    c.globalCompositeOperation = 'source-atop';
    for (const style of washes) { c.fillStyle = style; c.fillRect(0, 0, W * R, H * R); }
    c.globalCompositeOperation = 'source-over';
    this.signQueue = [];
  }

  layer(g, e, list, t, par, opts) {
    const cam = Math.sin(t * 0.05) * 8 * par;
    const span = this.worldW;
    for (const b of list) {
      let x = Math.round(((b.x - cam) % span + span) % span) - 10;
      if (x > W) continue;
      const y = GROUND - b.h;
      if (opts.flat) {
        g.fillStyle = opts.color; g.fillRect(x, y, b.w, b.h);
        for (let k = 0; k < b.h / 6; k++) if (hash(b.id, k) < 0.2 * opts.lit) { g.fillStyle = '#3a3150'; g.fillRect(x + 2 + Math.floor(hash(k, b.id) * (b.w - 4)), y + 3 + k * 6, 1, 1); }
      } else {
        const lit = (opts.power ? opts.power(x + b.w / 2) : 1) * (this.scene ? 0.3 : 0.55);
        this.building(g, e, x, y, b.w, b.h, { body: b.id % 2 ? PAL.hull : PAL.hull2, lit, seed: b.id * 31 + 7, t, flicker: lit < 0.4 ? 0.15 : 0 });
        if (b.sign && opts.power) {
          const on = opts.power(x + b.w / 2) > 0.35;
          const col = b.id % 3 ? PAL.teal : PAL.red;
          g.fillStyle = on ? col : '#222'; g.fillRect(x + 1, y + 6, 2, Math.min(20, b.h - 10));
          if (on) { e.fillStyle = col; e.fillRect(x + 1, y + 6, 2, Math.min(20, b.h - 10)); }
        }
      }
      if (b.ant) {
        g.fillStyle = '#2a3242'; g.fillRect(x + Math.floor(b.w / 2), y - 6, 1, 6);
        if (Math.floor(t * 1.5 + b.id) % 2) { e.fillStyle = PAL.red; e.fillRect(x + Math.floor(b.w / 2), y - 7, 1, 1); g.fillStyle = PAL.red; g.fillRect(x + Math.floor(b.w / 2), y - 7, 1, 1); }
      }
    }
  }

  vehicles(g, e, t, dt) {
    for (const c of this.cars) {
      c.x += c.speed * dt;
      if (c.x > W + 20) c.x = -20; if (c.x < -20) c.x = W + 20;
      const x = Math.round(c.x), y = c.lane + Math.round(Math.sin(t * 2 + c.lane) * 1);
      g.fillStyle = '#1c2433'; g.fillRect(x - 3, y, 6, 2);
      const head = c.speed > 0 ? x + 3 : x - 4;
      e.fillStyle = PAL.bone; e.fillRect(head, y, 1, 1);
      e.fillStyle = c.color; e.fillRect(c.speed > 0 ? x - 4 : x + 3, y + 1, 1, 1);
      e.globalAlpha = 0.35; e.fillRect(c.speed > 0 ? x - 10 : x + 4, y + 1, 6, 1); e.globalAlpha = 1;
    }
  }

  rain(g, t, dt) {
    g.fillStyle = 'rgba(64,196,178,0.35)';
    const n = Math.floor(this.drops.length * this.rainRate);
    for (let i = 0; i < n; i++) {
      const d = this.drops[i];
      d[1] += 120 * d[2] * dt; d[0] -= 30 * d[2] * dt;
      if (d[1] > GROUND + 30) { d[1] = -4; d[0] = this.rr() * (W + 40); }
      g.fillRect(Math.round(d[0]), Math.round(d[1]), 1, 3);
    }
  }

  ground(g) {
    // Wet street: the scene above, flipped and darkened, with a little ripple.
    const rh = H - GROUND;
    g.save();
    g.globalAlpha = 0.45;
    for (let y = 0; y < rh; y++) {
      const sx = Math.round(Math.sin((y + this.tAcc * 12) * 0.6) * (y / rh) * 2);
      g.drawImage(this.canvas, 0, GROUND - 1 - y, W, 1, sx, GROUND + y, W, 1);
    }
    g.restore();
    g.fillStyle = 'rgba(7,13,16,0.55)'; g.fillRect(0, GROUND, W, rh);
    g.fillStyle = '#1b2533'; g.fillRect(0, GROUND, W, 1);
    for (let x = 0; x < W; x += 24) { g.fillStyle = '#2a3446'; g.fillRect(x + ((this.tAcc * 20) % 24), GROUND + 14, 8, 1); }
  }

  frame(t, dt) {
    this.tAcc = t;
    const g = this.g, e = this.e;
    e.clearRect(0, 0, W, H);
    this.drawSky();
    g.drawImage(this.sky, 0, 0);
    g.fillStyle = PAL.night; g.fillRect(0, GROUND, W, H - GROUND);
    for (const [x, y, k] of this.stars) {
      const a = (1 - this.dawn) * (0.4 + 0.6 * Math.abs(Math.sin(t * (0.5 + k) + k * 9)));
      if (a > 0.3) { g.fillStyle = `rgba(232,236,214,${a.toFixed(2)})`; g.fillRect(x, y, 1, 1); }
    }
    // Moon behind the haze.
    g.fillStyle = mix('#cfd8c8', '#ffd9a8', this.dawn); g.globalAlpha = 1 - this.dawn * 0.7;
    g.beginPath(); g.arc(400, 30, 9, 0, Math.PI * 2); g.fill(); g.globalAlpha = 1;
    g.fillStyle = 'rgba(36,26,58,0.5)'; g.fillRect(380, 27, 50, 2); g.fillRect(372, 33, 60, 1);
    this.layer(g, e, this.far, t, 0.3, { flat: true, color: mix('#161a2e', '#3a3050', this.dawn), lit: 1 - this.dawn });
    g.fillStyle = 'rgba(43,34,68,0.35)'; g.fillRect(0, GROUND - 60, W, 60); // haze
    this.vehicles(g, e, t, dt);
    this.layer(g, e, this.mid, t, 0.6, { power: this.scene?.power?.bind(this.scene) ?? (() => 1) });
    if (this.scene) { g.fillStyle = 'rgba(20,16,40,0.45)'; g.fillRect(0, 0, W, GROUND); e.globalAlpha = 1; e.fillStyle = 'rgba(0,0,0,0.45)'; e.globalCompositeOperation = 'destination-out'; e.fillRect(0, 0, W, GROUND); e.globalCompositeOperation = 'source-over'; }
    this.scene?.draw(g, e, t, dt, this);
    this.rain(g, t, dt);
    // Glow: blurred emissive layer, added on top.
    this.gl.clearRect(0, 0, W, H);
    this.gl.filter = 'blur(3px)';
    this.gl.drawImage(this.emit, 0, 0);
    this.gl.filter = 'none';
    g.save();
    g.globalCompositeOperation = 'lighter';
    g.globalAlpha = 0.85; g.drawImage(this.glow, 0, 0);
    g.globalAlpha = 0.5; g.drawImage(this.emit, 0, 0);
    g.restore();
    this.ground(g);
    const washes = [];
    if (this.alarm > 0) { washes.push(`rgba(255,90,72,${(0.28 * this.alarm * (0.6 + 0.4 * Math.sin(t * 20))).toFixed(3)})`); this.alarm = Math.max(0, this.alarm - dt * 0.8); }
    if (this.flash > 0) { washes.push(`rgba(232,236,214,${(0.5 * this.flash).toFixed(3)})`); this.flash = Math.max(0, this.flash - dt * 3); }
    for (const style of washes) { g.fillStyle = style; g.fillRect(0, 0, W, H); }
    this.flushSigns(washes);
  }
}

// ---------------------------------------------------------------- shared props
export function catenary(g, e, x1, y1, x2, y2, sag, color, power, t, phase = 0) {
  const n = Math.max(8, Math.abs(x2 - x1));
  g.fillStyle = '#1e2635';
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const k = i / n;
    const x = Math.round(lerp(x1, x2, k)), y = Math.round(lerp(y1, y2, k) + Math.sin(k * Math.PI) * sag);
    pts.push([x, y]);
    g.fillRect(x, y, 1, 1);
  }
  if (power <= 0.02) return;
  // Current packets: more and faster with more power.
  const packets = Math.max(1, Math.round(power * 4));
  for (let p = 0; p < packets; p++) {
    const k = ((t * (0.25 + power * 0.5) + p / packets + phase) % 1 + 1) % 1;
    const [x, y] = pts[Math.floor(k * (pts.length - 1))];
    e.fillStyle = color; e.fillRect(x - 1, y, 3, 1);
    g.fillStyle = color; g.fillRect(x, y, 1, 1);
  }
}

export function beam(g, e, x1, y1, x2, y2, color, k) {
  // A data packet travelling from (x1,y1) to (x2,y2); k in 0..1.
  if (k <= 0 || k >= 1) return;
  const x = Math.round(lerp(x1, x2, k)), y = Math.round(lerp(y1, y2, k) - Math.sin(k * Math.PI) * 18);
  e.fillStyle = color; e.fillRect(x - 1, y - 1, 3, 3);
  g.fillStyle = PAL.bone; g.fillRect(x, y, 1, 1);
}

export { lerp, clamp, hash, mix };
