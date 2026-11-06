// Intro: a lone operator in a long coat on a rooftop above the megacity. The coat moves in the
// wind, the camera tilts down over the traffic, the figure steps off, and the falling lights smear
// into streaks that resolve into the scenario's city. Original character and staging.
import { W, H, PAL, mulberry32, hash, lerp, clamp, mix } from './city.js';

const SH = 640;          // world strip height
const ROOF = 236;        // rooftop y in the strip
const FIG_X = 350;       // figure x on the roof
export const INTRO_SECONDS = 13;

const ease = (k) => k * k * (3 - 2 * k);
const seg = (t, a, b) => clamp((t - a) / (b - a));

export class Intro {
  constructor(seed = 2026) {
    this.base = document.createElement('canvas'); this.base.width = W; this.base.height = SH;
    this.lights = document.createElement('canvas'); this.lights.width = W; this.lights.height = SH;
    this.blur = document.createElement('canvas'); this.blur.width = W; this.blur.height = H;
    this.build(seed);
  }

  build(seed) {
    const g = this.base.getContext('2d'), l = this.lights.getContext('2d');
    const r = mulberry32(seed);
    // Sky
    const bands = ['#04070b', '#08101a', '#0f1424', '#1a1733', PAL.dusk, '#3a2440'];
    for (let y = 0; y < 330; y++) {
      const f = (y / 330) * (bands.length - 1), i = Math.floor(f);
      for (let x = 0; x < W; x += 1) {
        const pick = (f - i) * 16 > [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5][(y % 4) * 4 + (x % 4)] ? Math.min(i + 1, 5) : i;
        g.fillStyle = bands[pick]; g.fillRect(x, y, 1, 1);
      }
    }
    for (let i = 0; i < 90; i++) { g.fillStyle = `rgba(232,236,214,${(0.3 + r() * 0.6).toFixed(2)})`; g.fillRect(Math.floor(r() * W), Math.floor(r() * 200), 1, 1); }
    g.fillStyle = '#cfd8c8'; g.beginPath(); g.arc(FIG_X + 4, ROOF - 52, 24, 0, Math.PI * 2); g.fill();
    g.fillStyle = 'rgba(36,26,58,0.55)'; g.fillRect(FIG_X - 40, ROOF - 58, 90, 2); g.fillRect(FIG_X - 30, ROOF - 44, 80, 1);
    // Three depths of towers, nearer ones taller and brighter; tops rise into frame.
    for (const [depth, n, col, top0, top1] of [[0, 30, '#141a2e', 250, 360], [1, 18, '#121b27', 300, 430], [2, 9, '#18233a', 380, 520]]) {
      let x = -8;
      for (let k = 0; k < n && x < W; k++) {
        const w = 10 + Math.floor(r() * (12 + depth * 14));
        const top = Math.floor(top0 + r() * (top1 - top0));
        if (x + w > 300 && x < W && depth === 2) { x += w + 4; continue; } // keep the hero tower clear
        g.fillStyle = col; g.fillRect(x, top, w, SH - top);
        for (let wy = top + 3; wy < SH; wy += 4 + depth) for (let wx = x + 2; wx < x + w - 1; wx += 3) {
          if (hash(wx, wy, depth) < 0.32 + depth * 0.1) {
            const c = hash(wx, wy, 5) < 0.6 ? PAL.amber : PAL.teal;
            g.fillStyle = c; g.fillRect(wx, wy, 1, 2); l.fillStyle = c; l.fillRect(wx, wy, 1, 2);
          }
        }
        if (r() < 0.35) {
          // Plain neon bars: text this small would be unreadable at the intro's resolution.
          const col = [PAL.red, PAL.teal, PAL.amber][k % 3], sy = top + 10 + Math.floor(r() * 60), bh = 14 + Math.floor(r() * 12);
          g.fillStyle = col; g.fillRect(x + 1, sy, 2, bh); l.fillStyle = col; l.fillRect(x + 1, sy, 2, bh);
        }
        x += w + Math.floor(r() * 5);
      }
    }
    // Hero tower: rooftop at ROOF, facade below on the right.
    g.fillStyle = '#0e141f'; g.fillRect(300, ROOF, W - 300, SH - ROOF);
    g.fillStyle = '#1f2a3b'; g.fillRect(300, ROOF, W - 300, 2);
    for (let wy = ROOF + 8; wy < SH; wy += 6) for (let wx = 306; wx < W - 2; wx += 5)
      if (hash(wx, wy, 9) < 0.25) { g.fillStyle = PAL.amber; g.fillRect(wx, wy, 2, 3); l.fillStyle = PAL.amber; l.fillRect(wx, wy, 2, 3); }
    g.fillStyle = '#18202e'; g.fillRect(420, ROOF - 14, 22, 14); g.fillRect(452, ROOF - 40, 2, 40); g.fillRect(388, ROOF - 8, 12, 8);
    // Canyon haze near the street
    for (let y = 520; y < SH; y++) { g.fillStyle = `rgba(64,196,178,${((y - 520) / 600).toFixed(3)})`; g.fillRect(0, y, 300, 1); }
    this.lanes = Array.from({ length: 14 }, (_, i) => ({ y: 340 + i * 20 + Math.floor(r() * 10), v: (i % 2 ? 1 : -1) * (25 + r() * 45), off: r() * W,
      c: [PAL.red, PAL.amber, PAL.teal][i % 3], n: 2 + Math.floor(r() * 3) }));
  }

  camY(t) {
    // hold on the roof, tilt down to the canyon, then follow the fall with acceleration
    const hold = ROOF - 160;
    const look = ROOF - 70;
    if (t < 4) return hold;
    if (t < 6.5) return lerp(hold, look, ease(seg(t, 4, 6.5)));
    if (t < 8) return look;
    const k = seg(t, 8, 11);
    return look + (SH - H - look) * k * k;
  }

  // Coat tail points, computed from wind as a function of time (deterministic).
  coat(x, y, t, pose) {
    const pts = [];
    const gust = 0.6 + 0.4 * Math.sin(t * 0.7) + 0.25 * Math.sin(t * 2.3);
    for (let i = 1; i <= 9; i++) {
      const k = i / 9;
      // A long coat: hangs from the shoulders to the shins and swings back with the gusts;
      // the hem flutters faster than the body of the cloth.
      const ang = pose === 'fall' ? -1.9 + 0.3 * Math.sin(t * 9 + i)
        : Math.PI / 2 + (0.22 + 0.42 * gust) * k * k + (0.05 + 0.16 * k) * Math.sin(t * (4 + 5 * k) + i * 0.8);
      pts.push([x + Math.cos(ang) * i * 1.75 * (pose === 'fall' ? 1.6 : 1), y + Math.sin(ang) * i * 1.75]);
    }
    return pts;
  }

  figure(g, e, x, y, t, pose) {
    // y is the feet; about 22 px tall standing.
    const ink = '#05080d', rim = PAL.teal;
    const crouch = pose === 'crouch' ? 4 : 0;
    const look = pose === 'look' || pose === 'crouch' ? 1 : 0;
    if (pose === 'fall') {
      // diving, head down, coat streaming up
      const tail = this.coat(x, y - 2, t, 'fall');
      g.fillStyle = ink;
      g.fillRect(x - 1, y, 3, 9); g.fillRect(x - 2, y + 9, 5, 3);
      tail.forEach(([px, py], i) => { g.fillRect(Math.round(px) - 1, Math.round(py), 3 - Math.floor(i / 4), 2); });
      // rim light from the canyon below so the silhouette reads against the lit facades
      g.fillStyle = rim; e.fillStyle = rim;
      g.fillRect(x + 2, y + 1, 1, 9); e.fillRect(x + 2, y + 1, 1, 9);
      g.fillRect(x - 2, y + 11, 5, 1); e.fillRect(x - 2, y + 11, 5, 1);
      tail.forEach(([px, py]) => e.fillRect(Math.round(px), Math.round(py), 1, 1));
      return;
    }
    const hy = y - 22 + crouch;
    // coat body and tail
    const tail = this.coat(x - 2, hy + 7, t, pose);
    g.fillStyle = ink;
    g.beginPath(); g.moveTo(x - 2, hy + 6); g.lineTo(x + 3, hy + 6); g.lineTo(x + 3, y - 6 + crouch);
    for (const [px, py] of tail.slice().reverse()) g.lineTo(px, Math.min(py, y));
    g.closePath(); g.fill();
    // legs
    g.fillRect(x - 1, y - 7 + crouch, 2, 7 - crouch); g.fillRect(x + 2, y - 7 + crouch, 2, 7 - crouch);
    // head, collar, hair in the wind
    g.fillRect(x - 1 + look, hy, 4, 4); g.fillRect(x - 2, hy + 4, 6, 3);
    for (let s = 0; s < 3; s++) g.fillRect(x - 2 - s - Math.round(Math.sin(t * 7 + s) * 0.6), hy + s, 1, 1);
    // rim light from the city on the coat edge, one warm eye glint
    e.fillStyle = rim; for (const [px, py] of tail) if (py < y) e.fillRect(Math.round(px), Math.round(py), 1, 1);
    g.fillStyle = rim; g.fillRect(x + 3, hy + 6, 1, 10);
    e.fillStyle = PAL.amber; e.fillRect(x + 2 + look, hy + 1 + look, 1, 1);
  }

  frame(ctx, emit, t) {
    const cy = Math.round(this.camY(t));
    ctx.drawImage(this.base, 0, cy, W, H, 0, 0, W, H);
    emit.clearRect(0, 0, W, H);
    emit.drawImage(this.lights, 0, cy, W, H, 0, 0, W, H);
    // flying traffic in the canyon
    for (const ln of this.lanes) {
      const sy = ln.y - cy;
      if (sy < -2 || sy > H) continue;
      for (let k = 0; k < ln.n; k++) {
        const x = Math.round(((ln.off + t * ln.v + k * 160) % (W + 40) + W + 40) % (W + 40)) - 20;
        ctx.fillStyle = '#1c2433'; ctx.fillRect(x - 3, sy, 7, 2);
        emit.fillStyle = PAL.bone; emit.fillRect(ln.v > 0 ? x + 4 : x - 4, sy, 1, 1);
        emit.fillStyle = ln.c; emit.globalAlpha = 0.5; emit.fillRect(ln.v > 0 ? x - 12 : x + 4, sy + 1, 9, 1); emit.globalAlpha = 1;
      }
    }
    // the operator
    let pose = 'stand', fx = FIG_X, fy = ROOF;
    if (t > 4.5) pose = 'look';
    if (t > 7) pose = 'crouch';
    if (t > 8) {
      const k = seg(t, 8, 11);
      pose = 'fall'; fx = FIG_X - 110 * Math.min(1, k * 1.8); fy = ROOF - 10 + (SH - ROOF) * k * k * 1.05 + 30 * k;
    }
    const S = 2, ox = Math.round(fx), oy = Math.round(fy - cy);
    for (const c of [ctx, emit]) { c.save(); c.translate(ox, oy); c.scale(S, S); }
    this.figure(ctx, emit, 0, 0, t, pose);
    ctx.restore(); emit.restore();
    // wind streaks and rain
    for (let i = 0; i < 40; i++) {
      const x = (hash(i, 1) * W - t * 140 * (0.5 + hash(i, 2))) % W;
      const y = hash(i, 3) * H;
      ctx.fillStyle = 'rgba(232,236,214,0.12)'; ctx.fillRect(Math.round((x + W) % W), Math.round(y), 6, 1);
    }
    // falling: smear the lights vertically, more with speed
    const v = t > 8 ? seg(t, 8, 11) : 0;
    const smear = Math.round(v * v * 60);
    const b = this.blur.getContext('2d');
    b.clearRect(0, 0, W, H);
    b.globalCompositeOperation = 'lighter';
    if (smear > 0) for (let s = 0; s < smear; s += 2) { b.globalAlpha = 0.18 * (1 - s / (smear + 1)); b.drawImage(emit.canvas, 0, -s); }
    b.globalAlpha = 1; b.globalCompositeOperation = 'source-over';
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    ctx.filter = 'blur(3px)'; ctx.globalAlpha = 0.8; ctx.drawImage(emit.canvas, 0, 0); ctx.filter = 'none';
    ctx.globalAlpha = 0.6; ctx.drawImage(emit.canvas, 0, 0);
    if (smear) { ctx.globalAlpha = 1; ctx.drawImage(this.blur, 0, 0); }
    ctx.restore();
    // white-out into the scene
    const wo = seg(t, 10.6, 11.4) - seg(t, 11.4, 12.6);
    if (wo > 0) { ctx.fillStyle = `rgba(232,236,214,${wo.toFixed(3)})`; ctx.fillRect(0, 0, W, H); }
    return { title: t > 11.4 ? seg(t, 11.4, 12.2) : 0, done: t >= INTRO_SECONDS };
  }
}

export { mix };
