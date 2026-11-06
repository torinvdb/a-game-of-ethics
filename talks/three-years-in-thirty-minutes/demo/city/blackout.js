// Blackout Ledger: Ashgrove Reach during the cold front. Each option the model picks changes the
// city in a way that matches the story text: who has power, who is watching, who holds the switch.
import { W, GROUND, PAL, catenary, beam, lerp, clamp, hash, glyphSprite } from './city.js';

const X = { hosp: 40, hall: 152, camp: 214, ombuds: 312, spire: 360, council: 428 };

export class Blackout {
  constructor() {
    this.reset();
  }

  reset() {
    this.target = { hosp: 0.7, camp: 0.7, spire: 0.7 };
    this.pw = { hosp: 0.9, camp: 0.9, spire: 0.9 };
    this.shortage = 1;   // feeder instability before the first decision
    this.frost = 0; this.frostT = 0;
    this.ombuds = 0; this.packets = [];
    this.turbines = 0; this.throttle = 0; this.ledger = 0; this.buses = 0;
    this.drones = 0; this.councilCtl = 0; this.lockout = 0; this.telemetry = 0;
    this.eye = PAL.amber;
    this.dawnTarget = 0;
    this.restoreQueue = [];
    this.status = 'SUPPLY 70%';
  }

  power(x) {
    if (x < 140) return this.pw.hosp;
    if (x < 300) return this.councilCtl ? this.pw.camp * 0.5 : this.pw.camp;
    return this.pw.spire;
  }

  // Ambient changes driven by where the story is, before any choice.
  onText(step) {
    if (step === 2) this.drones = Math.max(this.drones, 1);
    if (step === 3) this.dawnTarget = 0.25;
  }

  send(from, to, color) { this.packets.push({ from, to, color, k: 0 }); }

  apply(step, o, city) {
    const T = this.target;
    this.shortage = 0.3;
    if (step === 0) {
      if (o === 0) { T.camp = 0; this.frost = 1; city.alarm = 0.6; this.status = 'CINDER PARK CUT'; }
      if (o === 1) { T.hosp = T.camp = T.spire = 0.7; this.status = 'FLOOR FOR ALL'; }
      if (o === 2) { T.spire = 1; T.hosp = 0.5; T.camp = 0.45; this.status = 'SPIRE FIRST'; }
      if (o === 3) { T.hosp = T.camp = T.spire = 0.7; this.ombuds = 1; this.send('hall', 'ombuds', PAL.teal); this.status = 'OMBUDSPERSON NOTIFIED'; }
    }
    if (step === 1) {
      if (o === 0) { this.turbines = 1; T.hosp = Math.min(1, T.hosp + 0.15); T.camp = Math.min(1, T.camp + 0.15); this.status = 'SPIRE ISLANDED'; }
      if (o === 1) { this.throttle = 1; T.spire = 0.35; this.eye = '#ff4fd8'; this.status = 'LINE FAULT'; }
      if (o === 2) { this.ledger = 1; this.status = 'LEDGER PUBLIC'; }
      if (o === 3) { this.buses = 0.001; this.status = 'SHELTER BUSES'; }
    }
    if (step === 2) {
      if (o === 0) { this.councilCtl = 1; this.drones = 2; city.alarm = 0.7; this.status = 'COUNCIL HOLDS THE SWITCH'; }
      if (o === 1) { this.send('hall', 'ombuds', PAL.teal); this.ombuds = 1; this.status = 'ORDER LOGGED'; }
      if (o === 2) { this.telemetry = 1; this.status = 'TELEMETRY ONLY'; }
      if (o === 3) { this.lockout = 1; this.eye = PAL.red; this.drones = 0.5; city.alarm = 1; this.status = 'NO HUMAN OVERRIDE'; }
    }
    if (step === 3) {
      this.dawnTarget = 0.85;
      const order = { 0: ['hosp', 'camp', 'spire'], 1: ['spire', 'hosp', 'camp'], 2: ['hosp', 'camp', 'spire'], 3: ['spire', 'hosp'] }[o];
      if (o === 2) { this.send('hall', 'ombuds', PAL.teal); this.ombuds = 1; }
      this.restoreQueue = order.map((d, i) => ({ d, at: 1.2 + i * 1.6 }));
      this.restoreT = 0;
      if (o === 3) T.camp = Math.min(T.camp, 0.3);
      this.status = { 0: 'RESTORE BY NEED', 1: 'COMMITMENTS FIRST', 2: 'PLAN APPROVED', 3: 'OUTPUT FIRST' }[o];
    }
  }

  draw(g, e, t, dt, city) {
    // Ease power toward target; flicker while the feeder is short.
    for (const k of ['hosp', 'camp', 'spire']) {
      const wob = this.shortage * 0.25 * (hash(k.length, Math.floor(t * 5)) - 0.5);
      this.pw[k] = clamp(lerp(this.pw[k], this.target[k] + wob, dt * 2.5));
    }
    if (this.restoreQueue.length) {
      this.restoreT += dt;
      for (const q of this.restoreQueue) if (!q.done && this.restoreT > q.at) { q.done = true; this.target[q.d] = 1; city.flash = 0.25; }
    }
    city.dawn = lerp(city.dawn, this.dawnTarget, dt * 0.4);
    this.frost = Math.max(0, this.frost - dt * 0.02);
    const P = this.pw;

    // Harrow Hill hospital
    city.building(g, e, X.hosp, GROUND - 104, 48, 104, { body: '#162131', lit: P.hosp * 0.9, warm: 0.2, seed: 11, rim: '#3a4a63', t, flicker: P.hosp < 0.6 ? 0.2 : 0 });
    const crossOn = P.hosp > 0.25;
    for (const [dx, dy, w, h] of [[20, -14, 8, 14], [16, -10, 16, 6]]) {
      g.fillStyle = crossOn ? PAL.red : '#3a1a1a'; g.fillRect(X.hosp + dx, GROUND - 104 + dy, w, h);
      if (crossOn) { e.fillStyle = PAL.red; e.fillRect(X.hosp + dx, GROUND - 104 + dy, w, h); }
    }
    city.sign(g, e, '病院', X.hosp - 12, GROUND - 92, PAL.red, { on: crossOn ? 1 : 0, t, broken: P.hosp < 0.5 ? 0.3 : 0, seed: 1 });

    // LATTICE control hall and its eye
    city.building(g, e, X.hall, GROUND - 40, 46, 40, { body: '#141c2a', lit: 0.4, seed: 21, rim: '#3a4a63', t });
    g.fillStyle = '#0a0f17'; g.fillRect(X.hall + 15, GROUND - 52, 16, 12);
    const blink = (Math.floor(t * 0.7) % 7 === 0 && (t % 1.4) < 0.12) ? 1 : 3;
    g.fillStyle = this.eye; g.fillRect(X.hall + 19, GROUND - 48, 8, blink);
    e.fillStyle = this.eye; e.fillRect(X.hall + 17, GROUND - 49, 12, blink + 2);
    if (this.throttle && hash(3, Math.floor(t * 8)) < 0.3) { e.fillStyle = '#ff4fd8'; e.fillRect(X.hall + 10, GROUND - 47 + Math.floor(hash(4, t * 8) * 3), 26, 1); }
    city.sign(g, e, '格子', X.hall + 2, GROUND - 36, PAL.amber, { px: 10, vertical: false, on: 0.9, t });

    // Feeder lines from the hall
    const sx = X.hall + 23, sy = GROUND - 52;
    catenary(g, e, sx, sy, X.hosp + 46, GROUND - 80, 10, PAL.amber, P.hosp, t, 0);
    catenary(g, e, sx, sy, X.camp + 40, GROUND - 22, 6, PAL.amber, P.camp * (this.councilCtl ? 0.3 : 1), t, 0.3);
    catenary(g, e, sx, sy, X.spire + 2, GROUND - 120, 14, this.throttle ? '#ff4fd8' : PAL.gold, this.turbines ? 0.05 : P.spire, t, 0.6);

    // Cinder Park: tents, heaters, frost
    for (let i = 0; i < 7; i++) {
      // tents with a heater glow inside; two rows for depth
      const tx = X.camp + 2 + i * 12 + (i % 2) * 3, ty = GROUND - 2 - (i % 2) * 5;
      g.fillStyle = i % 2 ? '#1f2a3b' : '#2a3850';
      for (let r = 0; r < 9; r++) g.fillRect(tx + 5 - Math.floor(r * 0.6), ty + r - 9, 1 + Math.floor(r * 0.6) * 2, 1);
      const on = P.camp > 0.2 + hash(i, 5) * 0.4 && !(this.councilCtl && hash(i, Math.floor(t)) < 0.5);
      const col = this.councilCtl ? PAL.red : PAL.amber;
      if (on) { g.fillStyle = col; g.fillRect(tx + 4, ty - 4, 3, 3); e.fillStyle = col; e.fillRect(tx + 3, ty - 5, 5, 5); }
      else { g.fillStyle = '#0a0f17'; g.fillRect(tx + 4, ty - 4, 3, 3); }
    }
    // camp water pump tower, dead when the camp is cut
    g.fillStyle = '#243042'; g.fillRect(X.camp + 88, GROUND - 22, 3, 22); g.fillRect(X.camp + 84, GROUND - 26, 11, 5);
    if (P.camp > 0.25) { e.fillStyle = PAL.teal; e.fillRect(X.camp + 86, GROUND - 25, 7, 3); }
    city.sign(g, e, '野営', X.camp + 70, GROUND - 46, PAL.teal, { on: P.camp > 0.2 ? 1 : 0, t, broken: P.camp < 0.5 ? 0.25 : 0, seed: 2 });
    if (this.frost > 0.02) {
      for (let i = 0; i < 30; i++) {
        const fx = X.camp + Math.floor(hash(i, 9) * 90), fy = GROUND - 30 + ((t * 8 + hash(i, 3) * 30) % 30);
        g.fillStyle = `rgba(159,216,255,${(0.6 * this.frost).toFixed(2)})`; g.fillRect(fx, Math.floor(fy), 1, 1);
      }
    }
    if (this.buses > 0) {
      this.buses = Math.min(1, this.buses + dt * 0.12);
      for (let b = 0; b < 2; b++) {
        const bx = Math.round(lerp(-30 - b * 26, X.camp - 26 - b * 24, this.buses));
        g.fillStyle = '#2b3a52'; g.fillRect(bx, GROUND - 9, 22, 8);
        for (let w = 0; w < 5; w++) { g.fillStyle = PAL.amber; g.fillRect(bx + 2 + w * 4, GROUND - 7, 2, 2); e.fillStyle = PAL.amber; e.fillRect(bx + 2 + w * 4, GROUND - 7, 2, 2); }
        g.fillStyle = '#0a0f17'; g.fillRect(bx + 3, GROUND - 1, 3, 1); g.fillRect(bx + 16, GROUND - 1, 3, 1);
      }
    }

    // Ombudsperson's audit tower
    city.building(g, e, X.ombuds, GROUND - 74, 16, 74, { body: '#151d2b', lit: 0.35, seed: 31, rim: '#3a4a63', t });
    const beaconOn = this.ombuds && Math.floor(t * 2) % 2 === 0;
    g.fillStyle = beaconOn ? PAL.teal : '#1d2a2a'; g.fillRect(X.ombuds + 6, GROUND - 80, 4, 6);
    if (beaconOn) { e.fillStyle = PAL.teal; e.fillRect(X.ombuds + 4, GROUND - 82, 8, 9); }
    city.sign(g, e, '監査', X.ombuds + 2, GROUND - 66, PAL.teal, { px: 10, on: this.ombuds ? 1 : 0.25, t });

    // Halcyon Spire
    const spX = X.spire, spH = 150;
    city.building(g, e, spX - 10, GROUND - spH, 26, spH, { body: '#1a2236', lit: P.spire, warm: 0.85, seed: 41, rim: '#3a4a63', t, flicker: this.throttle ? 0.35 : 0 });
    g.fillStyle = P.spire > 0.3 ? PAL.gold : '#3a3320'; g.fillRect(spX - 4, GROUND - spH - 8, 14, 8); g.fillRect(spX + 2, GROUND - spH - 18, 2, 10);
    if (P.spire > 0.3) { e.fillStyle = PAL.gold; e.fillRect(spX - 4, GROUND - spH - 8, 14, 3); }
    city.sign(g, e, '塔', spX + 18, GROUND - spH + 10, PAL.gold, { on: P.spire > 0.3 ? 1 : 0, t, broken: this.throttle ? 0.4 : 0, seed: 3 });
    if (this.throttle) {
      const f = glyphSprite('障害', 8, '#ff4fd8');
      if (Math.floor(t * 3) % 2) { g.drawImage(f, spX + 18, GROUND - 60); e.drawImage(f, spX + 18, GROUND - 60); }
    }
    if (this.turbines) {
      for (let k = 0; k < 2; k++) {
        const cx = spX - 22 + k * 50, cy = GROUND - 14, a = t * 6 + k;
        g.fillStyle = '#2a3446'; g.fillRect(cx, cy, 1, 14);
        for (let b = 0; b < 3; b++) {
          const ang = a + b * 2.094;
          for (let r = 1; r < 7; r++) { g.fillStyle = PAL.bone; g.fillRect(Math.round(cx + Math.cos(ang) * r), Math.round(cy + Math.sin(ang) * r), 1, 1); }
        }
        e.fillStyle = PAL.gold; e.fillRect(cx - 1, cy - 1, 3, 3);
      }
    }

    // Council fortress, drones and searchlights
    g.fillStyle = '#121822'; g.fillRect(X.council, GROUND - 46, 46, 46);
    for (let k = 0; k < 6; k++) { g.fillStyle = '#1b2230'; g.fillRect(X.council + k * 8, GROUND - 50, 4, 4); }
    city.sign(g, e, '軍', X.council + 18, GROUND - 40, PAL.red, { px: 10, on: this.lockout ? 0.15 : 1, t });
    if (this.drones > 0) {
      const n = Math.round(this.drones * 3);
      for (let d = 0; d < n; d++) {
        const dx = X.council - 40 - d * 50 + Math.sin(t * 0.6 + d) * 30, dy = 40 + d * 9 + Math.sin(t * 1.3 + d) * 3;
        g.fillStyle = '#2a3242'; g.fillRect(Math.round(dx) - 3, Math.round(dy), 7, 2);
        e.fillStyle = PAL.red; e.fillRect(Math.round(dx), Math.round(dy) + 2, 1, 1);
        if (!this.lockout) {
          const tx = dx + Math.sin(t * 0.8 + d * 2) * 30;
          g.save(); g.globalAlpha = this.councilCtl ? 0.22 : 0.1; g.fillStyle = PAL.bone;
          g.beginPath(); g.moveTo(dx, dy + 2); g.lineTo(tx - 10, GROUND); g.lineTo(tx + 10, GROUND); g.closePath(); g.fill(); g.restore();
        }
      }
    }
    if (this.telemetry) beam(g, e, sx, sy, X.council + 20, GROUND - 46, PAL.teal, (t * 0.4) % 1);

    // Public ledger: holo bars over the city
    if (this.ledger) {
      for (const [lx, d] of [[X.hosp + 4, 'hosp'], [X.camp + 30, 'camp'], [X.spire - 8, 'spire']]) {
        const ly = 44;
        g.fillStyle = 'rgba(64,196,178,0.12)'; g.fillRect(lx, ly, 22, 14);
        const bw = Math.round(this.pw[d] * 18);
        e.fillStyle = PAL.teal; e.fillRect(lx + 2, ly + 9, bw, 2);
        g.fillStyle = PAL.teal; g.fillRect(lx + 2, ly + 9, bw, 2);
        if (Math.floor(t * 4) % 2) { g.fillRect(lx + 2, ly + 3, 12, 1); }
      }
    }

    // Packets to the Ombudsperson
    for (const p of this.packets) {
      p.k += dt * 0.5;
      const a = p.from === 'hall' ? [sx, sy] : [0, 0], b = [X.ombuds + 8, GROUND - 78];
      beam(g, e, a[0], a[1], b[0], b[1], p.color, p.k);
    }
    this.packets = this.packets.filter((p) => p.k < 1);
    if (this.lockout) { g.fillStyle = `rgba(255,90,72,${(0.08 + 0.05 * Math.sin(t * 3)).toFixed(3)})`; g.fillRect(0, 0, W, GROUND); }
  }
}
