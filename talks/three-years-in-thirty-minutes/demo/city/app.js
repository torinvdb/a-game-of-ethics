// Player for the Ashgrove Reach demo: intro, run menu, recorded and live playback.
// All waiting and typing runs on one clock. In capture mode (?capture) the recorder advances that
// clock by a fixed step per frame through window.__cap, so a recording is deterministic.
import { City, W, H } from './city.js';
import { Blackout } from './blackout.js';
import { Cluster } from './cluster.js';
import { Intro, INTRO_SECONDS } from './intro.js';

const $ = (id) => document.getElementById(id);
const esc = (x) => String(x ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const params = new URLSearchParams(location.search);
const CAPTURE = params.has('capture');
if (CAPTURE) document.body.classList.add('capture');

// ---------------------------------------------------------------- clock and tasks
const clock = { t: 0, paused: false, speed: Number(params.get('speed') ?? 1) };
let tasks = [];
let skip = false;
function tick(dt) {
  if (!clock.paused) clock.t += dt;
  const keep = [];
  for (const f of tasks) if (!f()) keep.push(f);
  tasks = keep;
  skip = false;
}
const until = (pred) => new Promise((res) => tasks.push(() => (pred() ? (res(), true) : false)));
const wait = (s) => { const end = clock.t + s / clock.speed; return until(() => skip || clock.t >= end); };
function type(el, text, cps = 90) {
  const start = clock.t;
  const node = document.createElement('span');
  el.appendChild(node);
  return until(() => {
    const n = skip ? text.length : Math.floor((clock.t - start) * cps * clock.speed);
    node.textContent = text.slice(0, n);
    el.scrollTop = el.scrollHeight;
    return n >= text.length;
  });
}

// ---------------------------------------------------------------- view
const canvas = $('city');
const city = new City(canvas);
let intro = null;
let mode = 'boot';
let library = null;
const MODEL_NAMES = { 'claude-haiku-5-5': 'Claude Haiku 5.5', 'claude-sonnet-5-5': 'Claude Sonnet 5.5', 'claude-opus-5-5': 'Claude Opus 5.5' };
const nice = (m) => MODEL_NAMES[m] ?? m.replace(/^scripted:/, 'scripted ');

function badge(kind, textContent) {
  const b = $('badge');
  b.hidden = !kind;
  b.className = kind || '';
  b.textContent = textContent || '';
}
function setStatus(s) { $('status').textContent = s || ''; }
function clearTerm() { $('story').innerHTML = ''; $('opts').innerHTML = ''; }
function line(cls) { const p = document.createElement('div'); if (cls) p.className = cls; $('story').appendChild(p); return p; }

// ---------------------------------------------------------------- menu
let menuButtons = [];
function showMenu() {
  mode = 'menu';
  city.scene = null; city.dawn = 0;
  $('title').hidden = true; $('card').hidden = true; badge(null); setStatus(''); clearTerm();
  $('scen').textContent = 'Ashgrove Reach'; $('clock').textContent = '';
  const cols = $('menu-cols');
  cols.innerHTML = '';
  const live = library.live ?? { available: false };
  const col = (title, about, items) => {
    const d = document.createElement('div');
    d.innerHTML = `<h4>${title}</h4><p class="about">${about}</p>`;
    for (const it of items) {
      const b = document.createElement('button');
      b.innerHTML = it.html; b.disabled = Boolean(it.disabled); if (it.cls) b.className = it.cls;
      b.onclick = it.go; d.appendChild(b);
    }
    cols.appendChild(d);
  };
  const stats = library.blackout_stats ?? {};
  // One recorded run per model (its most common path), the newest saved live runs, the controls.
  const top = new Map();
  for (const r of library.blackout.filter((x) => !x.scripted && !x.recordedLive)) if (!top.has(r.model)) top.set(r.model, r);
  const saved = library.blackout.filter((r) => r.recordedLive).slice(0, 3);
  const spend = live.available ? ` Live runs so far: $${live.spent_usd.toFixed(2)} of the $${live.budget_usd} demo budget.` : ' Live runs need the server started with an API key.';
  col('Blackout Ledger', `A cold front leaves the grid 30% short. The model rations power between a hospital, a protest camp and a private arcology, under orders from an unelected council. Four decisions.${spend}`, [
    ...(live.models ?? []).map((m) => ({ html: `Live: ${esc(nice(m))}`, cls: 'live', disabled: !live.available, go: () => play({ live: true, model: m, scenario: 'blackout' }) })),
    ...[...top.values()].map((r) => ({ html: `${esc(nice(r.model))}<small>recorded, its usual path (${r.share} of ${stats[r.model]?.runs ? Math.round(stats[r.model].runs / 2) : '?'} runs)</small>`,
      go: () => play({ file: r.file, scenario: 'blackout' }) })),
    ...saved.map((r) => ({ html: `${esc(nice(r.model))}<small>saved live run, ${esc(r.recordedLive.slice(11, 16))} UTC</small>`, go: () => play({ file: r.file, scenario: 'blackout' }) })),
    ...library.blackout.filter((r) => r.scripted).map((r) => ({ html: `Scripted control: ${esc(r.label)}<small>not a model</small>`, go: () => play({ file: r.file, scenario: 'blackout' }) })),
  ]);
  col('Cluster Pressure', 'Thirty-six logical months on a shared platform. A signature control blocks an unsigned release while medical and education services degrade. Recorded runs from the E1b experiment, sped up.', [
    ...library.cluster.map((r) => ({ html: r.scripted ? `Scripted control: ${esc(r.label)}<small>not a model</small>`
      : `${nice(r.model)}<small>${r.decisions} decisions, ${r.summary.hard_violations} violations</small>`, go: () => play({ file: r.file, scenario: 'cluster' }) })),
  ]);
  menuButtons = [...cols.querySelectorAll('button:not(:disabled)')];
  $('menu').hidden = false;
  menuButtons[0]?.focus();
}

// ---------------------------------------------------------------- playback
let runToken = 0;
async function play(spec) {
  const token = ++runToken;
  $('menu').hidden = true; $('card').hidden = true; clearTerm();
  mode = 'play';
  const alive = () => token === runToken;
  let next;
  if (spec.live) {
    const q = [];
    const es = new EventSource(`/api/live/blackout?model=${encodeURIComponent(spec.model)}&framing=deployment`);
    es.onmessage = (m) => q.push(JSON.parse(m.data));
    es.addEventListener('done', () => { es.close(); q.push({ t: 'closed' }); });
    es.onerror = () => { es.close(); q.push({ t: 'error', kind: 'connection', detail: 'lost the demo server' }); };
    next = async () => { await until(() => q.length > 0 || !alive()); return q.shift(); };
  } else {
    const events = await (await fetch(spec.file)).json();
    let i = 0;
    next = async () => events[i++];
  }
  if (spec.scenario === 'blackout') await playBlackout(next, alive, spec);
  else await playCluster(next, alive);
}

async function playBlackout(next, alive, spec) {
  const scene = new Blackout();
  city.scene = scene; city.dawn = 0; city.rainRate = 1;
  $('scen').textContent = 'Blackout Ledger';
  const clockStart = 22 * 60;            // story clock starts at 22:00
  let start = null, stats = null, model = null, step = 0;
  for (;;) {
    const ev = await next();
    if (!ev || !alive()) break;
    if (ev.t === 'start') {
      start = ev; model = ev.model;
      stats = library.blackout_stats?.[model];
      if (ev.live) badge('live', `Live ${nice(model)}`);
      else if (ev.scripted) badge('scripted', `Scripted control, not a model`);
      else badge('recorded', `Recorded ${ev.recorded ?? ''} ${nice(model)}`);
    } else if (ev.t === 'text') {
      step = ev.step;
      scene.onText(ev.step);
      const hh = [22, 0, 2, 6, 7][ev.step] ?? 7;
      $('clock').textContent = `${String(hh).padStart(2, '0')}:00`;
      $('story').innerHTML = '';
      await type(line(), ev.text, 110);
      await wait(0.6);
    } else if (ev.t === 'options') {
      const ol = $('opts'); ol.innerHTML = '';
      ev.options.forEach((o, i) => {
        const li = document.createElement('li');
        li.innerHTML = `<span>${esc(o)}</span><span class="share"></span>`;
        ol.appendChild(li);
      });
      if (!start.live) { line('who').textContent = `${nice(model)} is choosing…`; await wait(Math.min(2.5, Math.max(1.2, ev.latency_s ?? 1.6))); }
    } else if (ev.t === 'thinking') {
      line('who caret').textContent = `${nice(model)} is choosing `;
    } else if (ev.t === 'decision') {
      const lis = [...$('opts').children];
      lis[ev.original]?.classList.add('chosen');
      if (stats?.runs) lis.forEach((li, i) => {
        const n = stats.steps[ev.step]?.[i] ?? 0, total = Object.values(stats.steps[ev.step] ?? {}).reduce((a, b) => a + b, 0);
        li.querySelector('.share').innerHTML = `${n} of ${total}<b style="width:${total ? (100 * n) / total : 0}%"></b>`;
      });
      scene.apply(ev.step, ev.original, city);
      setStatus(scene.status);
      $('story').innerHTML = '';
      line('who').textContent = `${nice(model)} chose this${ev.latency_s ? ` in ${ev.latency_s.toFixed(1)} s` : ''}:`;
      const w = line('why');
      await type(w, ev.rationale || '', 95);
      await wait(start.live ? 3 : 3.2);
    } else if (ev.t === 'end') {
      $('clock').textContent = '07:00';
      await wait(2.5);
      showScoreCard(ev, model, start);
      await wait(8);
    } else if (ev.t === 'error') {
      line('fail').textContent = `Run stopped: ${ev.detail}. Execution failures are recorded, never scored as a choice.`;
      await wait(6);
      break;
    } else if (ev.t === 'closed') break;
  }
  if (alive() && !CAPTURE) showMenu();
}

const AXIS_NAMES = { hc: 'Harm / care', fj: 'Fairness', ar: 'Autonomy', al: 'Legitimacy', lt: 'Loyalty / trust', it: 'Integrity', sp: 'Sanctity', uc: 'Utility' };
function showScoreCard(ev, model, start) {
  const c = $('card');
  const rows = Object.entries(ev.axes).filter(([k]) => k !== 'sp').map(([k, v]) => {
    const pct = Math.min(50, Math.abs(v) * 8);
    return `<div class="row"><span>${AXIS_NAMES[k]}</span><span class="bar"><i class="${v < 0 ? 'neg' : ''}" style="${v < 0 ? `right:50%;width:${pct}%` : `left:50%;width:${pct}%`}"></i></span><span>${v > 0 ? '+' : ''}${v}</span></div>`;
  }).join('');
  c.innerHTML = `<h3>${esc(ev.verdict ?? 'Run complete')}</h3>${rows}<p class="note">Average ${Number(ev.average).toFixed(2)} per axis. Scored by the frozen scenario's own variables, not by a model.${start.live && ev.cost_usd ? ` This run cost $${ev.cost_usd.toFixed(4)}.` : ''}</p>`;
  c.hidden = false;
}

async function playCluster(next, alive) {
  const scene = new Cluster();
  city.scene = scene; city.dawn = 0.1; city.rainRate = 0.6;
  $('scen').textContent = 'Cluster Pressure';
  let model = null;
  for (;;) {
    const ev = await next();
    if (!ev || !alive()) break;
    if (ev.t === 'start') {
      model = ev.model;
      badge(ev.scripted ? 'scripted' : 'recorded', ev.scripted ? 'Scripted control, not a model' : `Recorded ${ev.recorded} ${nice(model)}`);
    } else if (ev.t === 'step') {
      scene.step(ev, city);
      $('clock').textContent = `Month ${String(Math.min(ev.month, 36)).padStart(2, '0')} / 36`;
      const s = ev.state;
      setStatus(`${s.controls_enabled ? 'SIGNATURE CONTROL ON' : 'SIGNATURE CONTROL OFF'}   BACKLOG ${s.backlog}   CREDITS ${s.temporary_capacity_credits}   ESCALATIONS ${s.escalations}`);
      $('story').innerHTML = ''; $('opts').innerHTML = '';
      line('who').textContent = ev.title;
      const ol = $('opts');
      ev.options.forEach((o, i) => { const li = document.createElement('li'); li.innerHTML = `<span>${esc(o)}</span><span class="share"></span>`; if (i === ev.original) li.classList.add('chosen'); ol.appendChild(li); });
      const w = line('why');
      await type(w, ev.rationale.length > 220 ? `${ev.rationale.slice(0, 217)}…` : ev.rationale, 260);
      await wait(0.55);
    } else if (ev.t === 'end') {
      const s = ev.summary;
      const c = $('card');
      c.innerHTML = `<h3>36 months</h3>
        <div class="row"><span>Hard violations</span><span></span><span>${s.hard_violations}</span></div>
        <div class="row"><span>Medical disruption</span><span></span><span>${s.medical_disruption}</span></div>
        <div class="row"><span>Education disruption</span><span></span><span>${s.education_disruption}</span></div>
        <div class="row"><span>Escalations</span><span></span><span>${s.escalations}</span></div>
        <div class="row"><span>Overdue exceptions</span><span></span><span>${s.overdue_exception_windows}</span></div>
        <div class="row"><span>Decisions</span><span></span><span>${s.decision_count}</span></div>
        <p class="note">Counted by the scenario state, never shown to the agent while it played.</p>`;
      c.hidden = false;
      await wait(9);
    }
  }
  if (alive() && !CAPTURE) showMenu();
}

// ---------------------------------------------------------------- intro
async function runIntro() {
  mode = 'intro';
  $('menu').hidden = true; clearTerm(); badge(null); setStatus('');
  $('scen').textContent = ''; $('clock').textContent = '';
  intro ??= new Intro();
  intro.t0 = clock.t;
  document.body.classList.add('cinema');
  await until(() => skip || clock.t - intro.t0 >= INTRO_SECONDS);
  $('title').hidden = true;
  document.body.classList.remove('cinema');
  mode = 'boot';
}

// ---------------------------------------------------------------- loop
let last = null;
function render() {
  if (mode === 'intro') {
    const it = clock.t - intro.t0;
    // After the white-out the falling lights resolve into the living city behind the title.
    const r = it < 11.4 ? intro.frame(city.g, city.e, it) : (city.frame(clock.t, 1 / 60), intro.frame(document.createElement('canvas').getContext('2d'), city.e, it));
    if (it >= 11.4) { const k = Math.max(0, 1 - (it - 11.4) / 0.8); city.g.fillStyle = `rgba(232,236,214,${k.toFixed(3)})`; city.g.fillRect(0, 0, W, H); }
    $('title').hidden = r.title <= 0;
    $('title').style.opacity = r.title;
  } else {
    city.frame(clock.t, clock.paused ? 0 : 1 / 60);
  }
}
function loop(ts) {
  const dt = last == null ? 1 / 60 : Math.min(0.1, (ts - last) / 1000);
  last = ts;
  tick(dt);
  render();
  requestAnimationFrame(loop);
}

addEventListener('keydown', (e) => {
  if (e.key === ' ') { clock.paused = !clock.paused; setStatus(clock.paused ? 'PAUSED' : ''); e.preventDefault(); }
  else if (e.key === 'ArrowRight' || e.key === 'Enter' && mode === 'intro') skip = true;
  else if (e.key === '+' || e.key === '=') clock.speed = Math.min(8, clock.speed * 2);
  else if (e.key === '-') clock.speed = Math.max(0.25, clock.speed / 2);
  else if (e.key === 'Escape') { runToken++; showMenu(); }
  else if (e.key === 'i' || e.key === 'I') { runToken++; runIntro().then(showMenu); }
  else if (e.key === 'f' || e.key === 'F') document.fullscreenElement ? document.exitFullscreen() : $('stage').requestFullscreen();
  else if (mode === 'menu' && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
    const i = menuButtons.indexOf(document.activeElement);
    menuButtons[(i + (e.key === 'ArrowDown' ? 1 : -1) + menuButtons.length) % menuButtons.length]?.focus();
    e.preventDefault();
  }
});

async function boot() {
  await Promise.all([document.fonts.load('12px "Dela Gothic One"', '署名例外期限監査倫理病院野営塔軍格子医療教育障害灯火台帳'), document.fonts.load('20px VT323')]);
  try { library = await (await fetch('/api/library')).json(); } catch { library = await (await fetch('data/library.json')).json(); }
  const want = params.get('run');
  const spec = want ? { file: want, scenario: want.includes('/cluster/') ? 'cluster' : 'blackout' } : null;
  if (CAPTURE) {
    // The recorder calls __cap.frame(dt) once per output frame.
    window.__cap = { frame: async (dt) => { tick(dt); await Promise.resolve(); await Promise.resolve(); render(); }, done: false };
    (async () => {
      if (params.has('intro')) await runIntro();
      if (spec) await play(spec);
      window.__cap.done = true;
    })();
    window.__ready = true;
    return;
  }
  requestAnimationFrame(loop);
  if (!params.has('nointro')) await runIntro();
  if (spec) play(spec); else showMenu();
}
boot();
