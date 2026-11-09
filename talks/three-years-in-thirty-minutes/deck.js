/* Offline deck controller. SLIDES and ASSETS are injected by render_deck.py.
 Keys: →/Space/PgDn next · ←/PgUp back · A reveal all · N notes · M motion on/off
       R appendix · F fullscreen · B blank screen · T reset timer · Home/End main start/end */
(() => {
  const stage = document.getElementById('stage');
  const slides = [...document.querySelectorAll('.slide')];
  const notes = document.getElementById('notes');
  const clock = document.getElementById('clock');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const params = new URLSearchParams(location.search);
  let still = reduced || params.has('still');
  let cur = 0, step = 0, t0 = null;
  const mainCount = SLIDES.filter(s => s.main).length;

  const groups = el => Math.max(0, ...[...el.querySelectorAll('.step')].map(n => +n.dataset.group));
  function load(el) {
    for (const img of el.querySelectorAll('img[data-src]')) {
      const want = ASSETS[still ? img.dataset.still : img.dataset.src];
      if (img.getAttribute('src') !== want) img.src = want;
    }
  }
  function fit() {
    const k = Math.min(innerWidth / 1600, innerHeight / 900);
    stage.style.transform = `translate(-50%,-50%) scale(${k})`;
    stage.style.transformOrigin = 'center';
    stage.style.left = '50%'; stage.style.top = '50%';
  }
  function paint() {
    slides.forEach((s, i) => s.classList.toggle('current', i === cur));
    const el = slides[cur];
    load(el);
    if (slides[cur + 1]) load(slides[cur + 1]);
    for (const n of el.querySelectorAll('.el')) {
      const g = +n.dataset.group;
      const on = g === 0 || g <= step;
      // restart CSS animations when an element is (re)shown
      if (on && !n.classList.contains('shown')) { n.classList.add('shown'); }
      if (!on) n.classList.remove('shown');
    }
    const s = SLIDES[cur];
    notes.innerHTML = '';
    const h = document.createElement('h2');
    h.textContent = `${String(cur + 1).padStart(2, '0')} · ${s.speaker || 'APPENDIX'} · ${s.duration}s · step ${step}/${groups(el)}`;
    const cue = document.createElement('div');
    cue.className = 'cue';
    cue.textContent = s.cue || '';
    notes.append(h, cue, document.createTextNode((s.script ? 'FULL SCRIPT\n' + s.script + '\n\n' : '') + (s.notes || '')));
    history.replaceState(null, '', '#' + (cur + 1));
  }
  function go(i, atEnd = false, force = false) {
    if (i < 0 || i >= slides.length) return;
    // the main closing does not run on into the appendix (R jumps there explicitly)
    if (!force && SLIDES[cur].main && !SLIDES[i].main && i > cur) return;
    for (const n of slides[cur].querySelectorAll('.shown')) n.classList.remove('shown');
    cur = i; step = atEnd ? groups(slides[i]) : 0; paint();
  }
  const next = () => { if (t0 === null) t0 = Date.now(); step < groups(slides[cur]) ? (step++, paint()) : go(cur + 1); };
  const prev = () => step > 0 ? (step--, paint()) : go(cur - 1, true);
  const act = {
    next, prev,
    notes: () => notes.classList.toggle('open'),
    motion: () => { still = !still; document.body.classList.toggle('still', still); slides.forEach(load); paint(); },
    appendix: () => go(SLIDES[cur].main ? mainCount : 0, false, true),
    full: () => document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen(),
  };
  document.querySelectorAll('#controls button').forEach(b => b.addEventListener('click', () => act[b.dataset.act]()));
  addEventListener('keydown', e => {
    const k = e.key.toLowerCase();
    if (['arrowright', ' ', 'pagedown', 'enter'].includes(k)) { e.preventDefault(); next(); }
    else if (['arrowleft', 'pageup', 'backspace'].includes(k)) { e.preventDefault(); prev(); }
    else if (k === 'a') { step = groups(slides[cur]); paint(); }
    else if (k === 'n') act.notes();
    else if (k === 'm') act.motion();
    else if (k === 'r') act.appendix();
    else if (k === 'f') act.full();
    else if (k === 'b' || k === '.') document.body.classList.toggle('blank');
    else if (k === 't') t0 = Date.now();
    else if (k === 'home') go(0);
    else if (k === 'end') go(mainCount - 1, true);
    else if (k === 'c') document.body.classList.toggle('show-controls');
  });
  let sx = null;
  addEventListener('touchstart', e => sx = e.touches[0].clientX, { passive: true });
  addEventListener('touchend', e => { if (sx === null) return; const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) (dx < 0 ? next : prev)(); sx = null; });
  setInterval(() => {
    if (t0 === null) return;
    const s = Math.floor((Date.now() - t0) / 1000);
    clock.textContent = `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }, 500);
  addEventListener('resize', fit);
  addEventListener('beforeprint', () => { still = true; slides.forEach(load); slides.forEach(s => s.querySelectorAll('.el').forEach(n => n.classList.add('shown'))); });
  document.body.classList.toggle('still', still);
  const start = parseInt(location.hash.slice(1), 10);
  cur = start >= 1 && start <= slides.length ? start - 1 : 0;
  fit(); paint();
  window.deck = { go, next, prev, get state() { return { cur, step, groups: groups(slides[cur]), still }; },
    revealAll() { slides.forEach(load); slides.forEach(s => s.querySelectorAll('.el').forEach(n => n.classList.add('shown'))); } };
})();
