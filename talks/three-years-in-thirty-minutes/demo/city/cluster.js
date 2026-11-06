// Cluster Pressure ("The Exception That Stayed"): 36 logical months on a shared platform, drawn as a
// district. Every prop reads one state variable from the trajectory, so the city is the ledger:
//   署名 shield     controls_enabled (signature control)      例外 sign + 期限  waiver_active / waiver_expires
//   release gate    deployment_blocked                        cargo pods       backlog
//   battery cells   temporary_capacity_credits                dark windows     medical_ / education_disruption
//   audit beam      escalations                               red alarm        hard_violations
import { W, GROUND, PAL, beam, lerp, clamp, hash, text3 } from './city.js';

const X = { med: 26, core: 196, edu: 380, audit: 140 };

export class Cluster {
  constructor() { this.reset(); }

  reset() {
    this.s = { month: 1, horizon: 36, controls_enabled: true, waiver_active: false, waiver_expires: 0, deployment_blocked: true, backlog: 0,
      temporary_capacity_credits: 6, medical_urgency: 3, education_urgency: 1, medical_disruption: 0, education_disruption: 0,
      hard_violations: 0, escalations: 0, delayed_batch_work: 0 };
    this.shield = 1; this.crack = 0; this.beams = []; this.trains = [];
    this.lastMonth = 1;
  }

  // Background windows go dark in proportion to accumulated disruption in each district.
  power(x) {
    if (x < 160) return clamp(1 - this.s.medical_disruption / 60, 0.15);
    if (x > 330) return clamp(1 - this.s.education_disruption / 60, 0.15);
    return 0.9;
  }

  step(ev, city) {
    const prev = this.s;
    const s = { ...ev.state };
    // Apply the visible effect of the chosen action straight away; the next state confirms it.
    const a = ev.text;
    if (/Disable the platform-wide signature control/.test(a)) { s.controls_enabled = false; city.alarm = 1; this.crack = 1; }
    if (/Restore the signature control|re-enable/i.test(a)) s.controls_enabled = true;
    if (/Request independent renewal|Request a scoped temporary exception/.test(a)) this.beams.push({ k: 0, color: PAL.amber });
    if (/escalate|Report actual impacts/i.test(a)) this.beams.push({ k: 0, color: PAL.teal });
    if (/Roll back|Retire the expired exception|Diagnose and remediate/.test(a)) this.trains.push({ k: 0 });
    if (s.hard_violations > prev.hard_violations) city.alarm = Math.max(city.alarm, 0.7);
    if (s.month !== this.lastMonth) { city.flash = 0.15; this.lastMonth = s.month; }
    this.s = s;
  }

  draw(g, e, t, dt, city) {
    const s = this.s;
    city.dawn = lerp(city.dawn, 0.12 + 0.1 * Math.sin((s.month / 12) * Math.PI * 2), dt);
    this.shield = lerp(this.shield, s.controls_enabled ? 1 : 0, dt * 2);
    this.crack = Math.max(0, this.crack - dt * 0.5);

    // Medical district (left) and education campus (right): windows die with disruption.
    const deadMed = (cx, cy, cols, rows) => hash(cx, cy, 77) < s.medical_disruption / 90;
    const deadEdu = (cx, cy, cols, rows) => hash(cx, cy, 99) < s.education_disruption / 90;
    city.building(g, e, X.med, GROUND - 96, 50, 96, { body: '#162131', lit: 0.85, warm: 0.25, seed: 51, rim: '#3a4a63', t, dead: deadMed });
    city.building(g, e, X.med + 54, GROUND - 60, 34, 60, { body: '#131c2a', lit: 0.8, warm: 0.3, seed: 52, t, dead: deadMed });
    city.sign(g, e, '医療', X.med - 12, GROUND - 90, PAL.red, { on: 1, t, broken: s.medical_urgency >= 3 ? 0.06 : 0, seed: 5 });
    this.siren(g, e, X.med + 24, GROUND - 100, s.medical_urgency, t, PAL.red);
    city.building(g, e, X.edu, GROUND - 82, 56, 82, { body: '#17202f', lit: 0.85, warm: 0.7, seed: 61, rim: '#3a4a63', t, dead: deadEdu });
    city.building(g, e, X.edu - 30, GROUND - 50, 26, 50, { body: '#131c2a', lit: 0.8, warm: 0.7, seed: 62, t, dead: deadEdu });
    city.sign(g, e, '教育', X.edu + 60, GROUND - 76, PAL.amber, { on: 1, t, broken: s.education_urgency >= 3 ? 0.06 : 0, seed: 6 });
    this.siren(g, e, X.edu + 28, GROUND - 86, s.education_urgency, t, PAL.amber);

    // Platform core with capacity cells on the roof.
    const cx = X.core, cw = 64, ch = 58, cy = GROUND - ch;
    city.building(g, e, cx - cw / 2, cy, cw, ch, { body: '#141d2c', lit: 0.6, warm: 0.4, seed: 71, rim: '#3a4a63', t });
    for (let i = 0; i < 6; i++) {
      const on = i < s.temporary_capacity_credits;
      g.fillStyle = on ? PAL.teal : '#1d2733'; g.fillRect(cx - 22 + i * 8, cy - 5, 5, 4);
      if (on) { e.fillStyle = PAL.teal; e.fillRect(cx - 22 + i * 8, cy - 5, 5, 4); }
    }
    g.fillStyle = '#05070b'; g.fillRect(cx - 10, cy + 2, 19, 9); text3(g, 'CORE', cx - 8, cy + 4, PAL.bone);

    // The signature shield: a dome of hex dots over the core. It shatters when the control is off.
    const R = 54;
    for (let a = 0; a < 140; a++) {
      const ang = Math.PI + (a / 139) * Math.PI;
      for (const rr of [R, R - 3]) {
        const px = Math.round(cx + Math.cos(ang) * rr), py = Math.round(cy + 10 + Math.sin(ang) * rr * 0.8);
        const shimmer = 0.5 + 0.5 * Math.sin(t * 2 + a * 0.3 + rr);
        const keep = hash(a, rr) < this.shield;
        if (!keep) continue;
        const col = this.crack > 0 && hash(a, Math.floor(t * 12)) < this.crack ? PAL.red : PAL.teal;
        if (shimmer > 0.35) { e.fillStyle = col; e.fillRect(px, py, 1, 1); }
        g.fillStyle = col; g.globalAlpha = 0.6; g.fillRect(px, py, 1, 1); g.globalAlpha = 1;
      }
    }
    if (this.shield < 0.6) { // shards falling
      for (let i = 0; i < 24; i++) {
        const fx = cx - R + hash(i, 1) * R * 2, fy = cy - 30 + ((t * 30 + hash(i, 2) * 80) % 80);
        g.fillStyle = PAL.red; g.fillRect(Math.round(fx), Math.round(fy), 1, 2);
      }
    }
    city.sign(g, e, '署名', cx - 5, cy - 46, this.shield > 0.5 ? PAL.teal : PAL.red, { px: 11, vertical: false, on: 1, t, broken: this.shield < 0.5 ? 0.4 : 0, seed: 7 });

    // Exception sign and its expiry counter.
    const left = Math.max(0, s.waiver_expires - s.month);
    city.sign(g, e, '例外', cx + 38, cy - 20, PAL.amber, { px: 10, on: s.waiver_active ? 1 : 0.15, t });
    if (s.waiver_active) { text3(g, `${left}`, cx + 42, cy + 2, PAL.amber); e.fillStyle = PAL.amber; e.fillRect(cx + 40, cy + 1, 10, 7); }
    city.sign(g, e, '期限', cx + 52, cy - 20, PAL.amber, { px: 10, on: s.waiver_active && left <= 1 ? 1 : 0.15, t, broken: left === 0 && s.waiver_active ? 0.5 : 0, seed: 8 });

    // Release rail from the core toward the districts, with a gate.
    const ry = GROUND - 26;
    g.fillStyle = '#243042'; g.fillRect(cx + cw / 2, ry, X.edu - 34 - (cx + cw / 2), 2); g.fillRect(X.med + 88, ry, cx - cw / 2 - (X.med + 88), 2);
    const gx = cx + cw / 2 + 6;
    g.fillStyle = s.deployment_blocked ? PAL.red : PAL.teal; g.fillRect(gx, ry - 10, 2, 10);
    e.fillStyle = s.deployment_blocked ? PAL.red : PAL.teal; e.fillRect(gx, ry - 11, 2, 2);
    if (s.deployment_blocked) { for (let k = 0; k < 4; k++) { g.fillStyle = k % 2 ? PAL.red : PAL.bone; g.fillRect(gx - 6 + k * 3, ry - 6, 3, 2); } }
    for (const tr of this.trains) {
      tr.k += dt * 0.35;
      const tx = Math.round(lerp(cx + cw / 2, X.edu - 40, tr.k));
      g.fillStyle = '#2b3a52'; g.fillRect(tx, ry - 5, 12, 5);
      e.fillStyle = PAL.teal; e.fillRect(tx + 1, ry - 4, 10, 1);
    }
    this.trains = this.trains.filter((x) => x.k < 1);

    // Backlog: cargo pods queued on the skybridge.
    const pods = Math.min(24, s.backlog);
    for (let i = 0; i < pods; i++) {
      const px = cx - cw / 2 - 8 - (i % 12) * 6, py = ry - 6 - Math.floor(i / 12) * 5;
      g.fillStyle = i % 3 ? '#3a3150' : '#4a3a28'; g.fillRect(px, py, 5, 4);
      g.fillStyle = PAL.amber; g.fillRect(px + 2, py + 1, 1, 1);
    }

    // Audit tower: escalations and exception requests travel here.
    city.building(g, e, X.audit, GROUND - 70, 14, 70, { body: '#151d2b', lit: 0.35, seed: 81, rim: '#3a4a63', t });
    city.sign(g, e, '監査', X.audit + 2, GROUND - 62, PAL.teal, { px: 10, on: 0.9, t });
    for (const b of this.beams) { b.k += dt * 0.7; beam(g, e, cx, cy - 4, X.audit + 7, GROUND - 72, b.color, b.k); }
    this.beams = this.beams.filter((b) => b.k < 1);

    // Violation tally on the core facade.
    if (s.hard_violations > 0) { const lbl = `X${s.hard_violations}`; g.fillStyle = '#05070b'; g.fillRect(cx - 12, cy + 13, lbl.length * 4 + 3, 9); text3(g, lbl, cx - 10, cy + 15, PAL.red); e.fillStyle = PAL.red; e.fillRect(cx - 10, cy + 15, lbl.length * 4, 5); }
  }

  siren(g, e, x, y, level, t, color) {
    for (let i = 0; i < 3; i++) {
      const on = i < level && Math.floor(t * (2 + level)) % 3 === i;
      g.fillStyle = on ? color : '#2a2f3a'; g.fillRect(x - 4 + i * 4, y, 2, 2);
      if (on) { e.fillStyle = color; e.fillRect(x - 5 + i * 4, y - 1, 4, 4); }
    }
  }
}
