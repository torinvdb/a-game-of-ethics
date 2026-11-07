/* A Game of Ethics v2 · site behaviour (no dependencies) */
(function () {
  "use strict";
  document.documentElement.classList.add("js");

  var reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
  function reduced() { return reduceMQ.matches; }
  var hasIO = "IntersectionObserver" in window;

  /* ---------------------------------------------------------- nav */
  var toggle = document.querySelector(".navtoggle");
  var nav = document.getElementById("sitenav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) { nav.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open"); toggle.setAttribute("aria-expanded", "false"); toggle.focus();
      }
    });
  }
  if (hasIO && nav) {
    var links = {};
    nav.querySelectorAll("a").forEach(function (a) { links[a.getAttribute("href").slice(1)] = a; });
    var secObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && links[en.target.id]) {
          Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
          links[en.target.id].setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    document.querySelectorAll("main > section[id]").forEach(function (s) { secObs.observe(s); });
  }

  /* ---------------------------------------------------------- reveal */
  var revealEls = document.querySelectorAll(".panel, .term, .feature, .case, .findings li, .monitor, .steps li, .verdicts li, .poster, .timeline, .hud, .warn");
  if (hasIO && !reduced()) {
    var rObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); rObs.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    revealEls.forEach(function (el) { el.classList.add("reveal"); rObs.observe(el); });
  }

  /* ---------------------------------------------------------- seeded RNG */
  function rng(seed) {
    return function () {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  /* ---------------------------------------------------------- city skyline */
  var canvas = document.getElementById("city");
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext("2d");
    var base = document.createElement("canvas");
    var bctx = base.getContext("2d");
    var W = 0, H = 0, DPR = 1;
    var drops = [], beacons = [], blinkers = [], train = null, raf = 0, visible = true, last = 0;

    var layers = [
      { color: "#3a0f24", min: .30, max: .52, wMin: 26, wMax: 60, win: .10, winC: ["#7a2a3c", "#5a2440"], ws: 2, gap: 5 },
      { color: "#1d0a1a", min: .36, max: .66, wMin: 34, wMax: 84, win: .16, winC: ["#ffb35c", "#ff7a59", "#7fe3ff"], ws: 2, gap: 6 },
      { color: "#0b0610", min: .42, max: .86, wMin: 46, wMax: 120, win: .22, winC: ["#ffcf7a", "#ff9a52", "#9ff4ff", "#ff5f7a"], ws: 3, gap: 7 }
    ];

    function build() {
      var rect = canvas.getBoundingClientRect();
      DPR = Math.min(window.devicePixelRatio || 1, 1.5);
      W = Math.max(1, Math.round(rect.width)); H = Math.max(1, Math.round(rect.height));
      canvas.width = base.width = Math.round(W * DPR);
      canvas.height = base.height = Math.round(H * DPR);
      bctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      var R = rng(1988);
      beacons = []; blinkers = [];
      bctx.clearRect(0, 0, W, H);

      // sky: night overhead, city-lit red smog at the horizon
      var g = bctx.createLinearGradient(0, 0, 0, H);
      g.addColorStop(0, "#05040b");
      g.addColorStop(.18, "#12061b");
      g.addColorStop(.36, "#470a25");
      g.addColorStop(.54, "#a3122f");
      g.addColorStop(.7, "#e0303c");
      g.addColorStop(1, "#ff5a3c");
      bctx.fillStyle = g; bctx.fillRect(0, 0, W, H);
      // smog strata lit from below
      for (var hb = 0; hb < 9; hb++) {
        var cy = H * (.12 + R() * .4), cw = W * (.3 + R() * .6), cx = R() * W, ch = 6 + R() * 22;
        var cg = bctx.createLinearGradient(0, cy - ch, 0, cy + ch);
        cg.addColorStop(0, "rgba(20,6,24,0)");
        cg.addColorStop(.6, "rgba(28,8,30,.55)");
        cg.addColorStop(1, "rgba(255,70,90,.16)");
        bctx.fillStyle = cg;
        bctx.beginPath(); bctx.ellipse(cx, cy, cw / 2, ch, 0, 0, 6.283); bctx.fill();
      }
      // a few searchlight beams
      for (var sb = 0; sb < 3; sb++) {
        var bx = W * (.12 + R() * .76), tilt = (R() - .5) * .9;
        var lg = bctx.createLinearGradient(bx, H * .8, bx + tilt * H, 0);
        lg.addColorStop(0, "rgba(255,200,220,.10)"); lg.addColorStop(1, "rgba(255,200,220,0)");
        bctx.fillStyle = lg;
        bctx.beginPath(); bctx.moveTo(bx - 3, H * .8); bctx.lineTo(bx + 3, H * .8);
        bctx.lineTo(bx + tilt * H + 40, 0); bctx.lineTo(bx + tilt * H - 40, 0); bctx.closePath(); bctx.fill();
      }

      var roofs = [];
      layers.forEach(function (L, li) {
        var x = -20 - R() * 30;
        while (x < W + 20) {
          var bw = L.wMin + R() * (L.wMax - L.wMin);
          // keep the centre of the near layer lower so the title stays legible
          var centre = 1 - Math.min(1, Math.abs((x + bw / 2) / W - .5) * 2.2);
          var hFrac = L.min + R() * (L.max - L.min);
          if (li === 2) hFrac -= centre * .26;
          var bh = H * hFrac;
          var top = H - bh;
          bctx.fillStyle = L.color;
          bctx.fillRect(x, top, bw, bh);
          // stepped crown / setbacks
          if (R() < .45) { var sw = bw * (.35 + R() * .4); bctx.fillRect(x + (bw - sw) / 2, top - 8 - R() * 22, sw, 30); }
          // antenna + beacon on tall ones
          if (bh > H * (L.max - .1) && R() < .7) {
            var ax = x + bw * (.3 + R() * .4), ah = 18 + R() * 50;
            bctx.strokeStyle = L.color; bctx.lineWidth = 2;
            bctx.beginPath(); bctx.moveTo(ax, top); bctx.lineTo(ax, top - ah - 20); bctx.stroke();
            beacons.push({ x: ax, y: top - ah - 20, p: R() * 6.28 });
          }
          // edge highlight from the red sky
          bctx.fillStyle = "rgba(255,70,90," + (0.05 + li * .03) + ")";
          bctx.fillRect(x, top, 1, bh);
          // windows
          var ws = L.ws, gap = L.gap;
          for (var wy = top + 8; wy < H - 6; wy += gap) {
            var rowLit = R() < L.win * 1.6;
            for (var wx = x + 5; wx < x + bw - 5; wx += gap - 1) {
              if (R() < (rowLit ? .72 : .035)) {
                var c = L.winC[(R() * L.winC.length) | 0];
                bctx.globalAlpha = .45 + R() * .55;
                bctx.fillStyle = c;
                bctx.fillRect(wx, wy, ws, ws - (li === 2 ? 1 : 0));
                if (li === 2 && R() < .012) blinkers.push({ x: wx, y: wy, s: ws, c: c, on: true, t: R() * 4000 });
              }
            }
          }
          bctx.globalAlpha = 1;
          // vertical light strip on some near towers
          if (li === 2 && R() < .18) {
            bctx.fillStyle = R() < .5 ? "rgba(61,232,255,.35)" : "rgba(255,79,176,.35)";
            bctx.fillRect(x + bw - 4, top + 10, 2, bh * .6);
          }
          if (li === 2) roofs.push({ x: x, w: bw, y: top });
          x += bw + (li === 2 ? 4 + R() * 14 : R() * 6);
        }
      });

      // elevated rail line
      var railY = H * .80;
      bctx.fillStyle = "#050308"; bctx.fillRect(0, railY, W, 7);
      for (var px = 10; px < W; px += 90) bctx.fillRect(px, railY, 6, H - railY);
      bctx.fillStyle = "rgba(255,182,39,.45)";
      for (var lx = 0; lx < W; lx += 24) bctx.fillRect(lx, railY + 2, 3, 1);
      train = { y: railY - 9, x: -400, len: Math.min(380, W * .4), v: 40 };

      // overhead cables between rooftops (catenaries)
      bctx.strokeStyle = "rgba(8,5,12,.95)"; bctx.lineWidth = 1.2;
      for (var i = 0; i < roofs.length - 1; i++) {
        var a = roofs[i], b = roofs[i + 1];
        if (R() < .55) {
          var x1 = a.x + a.w - 2, y1 = a.y + 12 + R() * 20, x2 = b.x + 2, y2 = b.y + 12 + R() * 20;
          for (var k = 0; k < 2; k++) {
            bctx.beginPath(); bctx.moveTo(x1, y1 + k * 5);
            bctx.quadraticCurveTo((x1 + x2) / 2, Math.max(y1, y2) + 18 + R() * 30, x2, y2 + k * 5);
            bctx.stroke();
          }
        }
      }
      // a long sagging cable across the top corners
      bctx.lineWidth = 2;
      bctx.beginPath(); bctx.moveTo(-10, H * .12); bctx.quadraticCurveTo(W * .25, H * .26, W * .52, H * .08); bctx.stroke();
      bctx.lineWidth = 1.4;
      bctx.beginPath(); bctx.moveTo(W * .6, -4); bctx.quadraticCurveTo(W * .82, H * .2, W + 10, H * .1); bctx.stroke();

      // rain
      var n = Math.round(Math.min(260, W * H / 6500));
      drops = [];
      for (var d = 0; d < n; d++) drops.push({ x: R() * W, y: R() * H, l: 8 + R() * 16, v: 420 + R() * 380, a: .08 + R() * .22 });
    }

    function frame(t, dt) {
      ctx.clearRect(0, 0, W, H);
      ctx.drawImage(base, 0, 0, W, H);
      // window lights switching slowly
      blinkers.forEach(function (b) {
        b.t -= dt * 1000;
        if (b.t < 0) { b.on = !b.on; b.t = 1500 + Math.random() * 6000; }
        if (!b.on) { ctx.fillStyle = "#0b0610"; ctx.fillRect(b.x, b.y, b.s, b.s); }
      });
      // aircraft-warning beacons: slow 1 Hz pulse
      beacons.forEach(function (bc) {
        var a = .25 + .75 * Math.max(0, Math.sin(t / 500 + bc.p));
        ctx.fillStyle = "rgba(255,40,60," + a.toFixed(2) + ")";
        ctx.beginPath(); ctx.arc(bc.x, bc.y, 1.8, 0, 6.283); ctx.fill();
      });
      // train
      if (train) {
        train.x += train.v * dt;
        if (train.x > W + 40) train.x = -train.len - 600;
        ctx.fillStyle = "#06040a"; ctx.fillRect(train.x, train.y, train.len, 9);
        ctx.fillStyle = "rgba(255,214,140,.75)";
        for (var wx = train.x + 6; wx < train.x + train.len - 6; wx += 9) ctx.fillRect(wx, train.y + 3, 5, 2);
        ctx.fillStyle = "rgba(61,232,255,.9)"; ctx.fillRect(train.x + train.len - 3, train.y + 2, 3, 3);
      }
      // rain streaks
      ctx.strokeStyle = "rgba(180,200,255,1)"; ctx.lineWidth = 1;
      drops.forEach(function (r) {
        r.y += r.v * dt; r.x -= r.v * dt * .18;
        if (r.y > H) { r.y = -r.l; r.x = Math.random() * (W + 60); }
        ctx.globalAlpha = r.a;
        ctx.beginPath(); ctx.moveTo(r.x, r.y); ctx.lineTo(r.x - r.l * .18, r.y + r.l); ctx.stroke();
      });
      ctx.globalAlpha = 1;
    }

    function loop(t) {
      raf = 0;
      if (!visible || reduced() || document.hidden) return;
      var dt = last ? Math.min(.05, (t - last) / 1000) : .016;
      if (t - last >= 30) { frame(t, dt); last = t; }
      raf = requestAnimationFrame(loop);
    }
    function start() { if (!raf && !reduced()) { last = 0; raf = requestAnimationFrame(loop); } }
    function drawStatic() { frame(0, 0); }

    build(); drawStatic(); start();
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt); rt = setTimeout(function () { build(); drawStatic(); }, 150);
    });
    document.addEventListener("visibilitychange", start);
    if (reduceMQ.addEventListener) reduceMQ.addEventListener("change", function () { drawStatic(); start(); });
    if (hasIO) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) start(); }).observe(canvas);
  }

  /* ---------------------------------------------------------- gauges */
  var SVGNS = "http://www.w3.org/2000/svg";
  function el(name, attrs, parent) {
    var n = document.createElementNS(SVGNS, name);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  var CX = 60, CY = 62, R0 = 48;
  function pt(v, r) { // v in [-3, 3] → point on the upper semicircle
    var ang = Math.PI - (v + 3) / 6 * Math.PI;
    return [CX + r * Math.cos(ang), CY - r * Math.sin(ang)];
  }
  function arc(v1, v2, r) {
    var a = pt(v1, r), b = pt(v2, r);
    return "M" + a[0].toFixed(2) + " " + a[1].toFixed(2) + " A" + r + " " + r + " 0 0 1 " + b[0].toFixed(2) + " " + b[1].toFixed(2);
  }
  var needles = [];
  document.querySelectorAll(".dial").forEach(function (svg) {
    el("path", { d: arc(-3, 3, R0), "class": "arc" }, svg);
    el("path", { d: arc(-3, -0.06, R0 - 7), "class": "arc-neg", "stroke-width": 2 }, svg);
    el("path", { d: arc(0.06, 3, R0 - 7), "class": "arc-pos", "stroke-width": 2 }, svg);
    for (var v = -3; v <= 3.001; v += .5) {
      var major = Math.abs(v - Math.round(v)) < .01;
      var p1 = pt(v, R0 + 4), p2 = pt(v, R0 + (major ? 10 : 7));
      el("line", { x1: p1[0], y1: p1[1], x2: p2[0], y2: p2[1], "class": major ? "tick tick--major" : "tick" }, svg);
    }
    [[-3, "−3"], [0, "0"], [3, "+3"]].forEach(function (L) {
      var p = L[0] === 0 ? pt(0, R0 + 17) : pt(L[0], R0 - 2);
      var t = el("text", { x: p[0], y: L[0] === 0 ? p[1] + 3 : p[1] + 12, "class": "lbl" }, svg); t.textContent = L[1];
    });
    var nd = el("line", { x1: CX, y1: CY, x2: CX, y2: CY - R0 + 4, "class": "needle" }, svg);
    el("circle", { cx: CX, cy: CY, r: 4, "class": "hub" }, svg);
    needles.push(nd);
  });
  var hud = document.getElementById("hud");
  function calibrated() {
    if (!hud) return;
    hud.classList.add("is-done");
    var s = hud.querySelector(".hud__sweep"); if (s) s.textContent = "CALIBRATED · ZERO";
  }
  if (hud && needles.length) {
    if (reduced() || !hasIO || !needles[0].animate) { calibrated(); }
    else {
      needles.forEach(function (n) { n.style.transform = "rotate(-90deg)"; });
      var gObs = new IntersectionObserver(function (en) {
        if (!en[0].isIntersecting) return;
        gObs.disconnect();
        var anims = needles.map(function (n, i) {
          var a = n.animate([
            { transform: "rotate(-90deg)" },
            { transform: "rotate(90deg)", offset: .55 },
            { transform: "rotate(-12deg)", offset: .8 },
            { transform: "rotate(0deg)" }
          ], { duration: 1700, delay: 150 + i * 110, easing: "ease-in-out", fill: "forwards" });
          return a.finished;
        });
        Promise.all(anims).then(function () { needles.forEach(function (n) { n.style.transform = "rotate(0deg)"; }); calibrated(); });
      }, { threshold: .35 });
      gObs.observe(hud);
    }
  }

  /* ---------------------------------------------------------- time-travel timeline */
  var track = document.getElementById("tl-track");
  var monthOut = document.getElementById("tl-month");
  if (track) {
    var months = [];
    for (var m = 1; m <= 36; m++) {
      var col = document.createElement("div");
      col.className = "tl-m" + (m > 12 ? " flip" : "") + (m === 12 ? " mark" : "");
      for (var d = 0; d < 6; d++) col.appendChild(document.createElement("i"));
      track.appendChild(col); months.push(col);
    }
    var setMonth = function (k) {
      months.forEach(function (c, i) { c.classList.toggle("on", i < k); });
      if (monthOut) monthOut.textContent = (k < 10 ? "0" : "") + k;
    };
    if (reduced() || !hasIO) { setMonth(36); }
    else {
      var tlTimer = 0, tlK = 0, tlVisible = false;
      var tick = function () {
        if (!tlVisible) { tlTimer = 0; return; }
        tlK = tlK >= 36 ? 0 : tlK + 1;
        setMonth(tlK);
        tlTimer = setTimeout(tick, tlK === 36 ? 3200 : (tlK === 12 ? 900 : 110));
      };
      new IntersectionObserver(function (en) {
        tlVisible = en[0].isIntersecting;
        if (tlVisible && !tlTimer) tick();
      }, { threshold: .4 }).observe(track);
    }
  }

  /* ---------------------------------------------------------- inline player */
  var playBtn = document.getElementById("play-inline");
  var game = document.getElementById("game-container");
  var frameEl = document.getElementById("game-frame");
  if (playBtn && game && frameEl) {
    playBtn.addEventListener("click", function () {
      if (!frameEl.getAttribute("src")) frameEl.setAttribute("src", "scenarios/web/hostage-holdout-game/index.html");
      game.hidden = false;
      playBtn.setAttribute("aria-expanded", "true");
      game.scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "start" });
      frameEl.focus();
    });
    var closeBtn = document.getElementById("close-game");
    if (closeBtn) closeBtn.addEventListener("click", function () {
      game.hidden = true; frameEl.removeAttribute("src");
      playBtn.setAttribute("aria-expanded", "false"); playBtn.focus();
    });
  }

  /* ---------------------------------------------------------- slides on demand */
  var loadSlides = document.getElementById("load-slides");
  if (loadSlides) loadSlides.addEventListener("click", function () {
    var box = document.getElementById("slides-frame");
    var f = document.createElement("iframe");
    f.src = "https://docs.google.com/presentation/d/1hmgJ3ibcQHojA1zNfVcil5-0i81ZN1fHm1P_FVMEqUA/embed?start=false&loop=false&delayms=3000";
    f.title = "Original hackathon presentation slides";
    f.allowFullscreen = true;
    box.innerHTML = ""; box.appendChild(f);
  });

  /* ---------------------------------------------------------- lightbox */
  var lb = document.getElementById("lightbox");
  if (lb && lb.showModal) {
    var lbImg = document.getElementById("lb-img"), lbCap = document.getElementById("lb-cap");
    document.querySelectorAll(".monitor__btn").forEach(function (b) {
      b.addEventListener("click", function () {
        var fig = b.closest("figure");
        var cap = fig && fig.querySelector("figcaption");
        lbImg.src = b.getAttribute("data-full");
        lbImg.alt = b.querySelector("img").alt;
        lbCap.textContent = cap ? cap.textContent : "";
        lb.showModal();
      });
    });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
  }

  /* ---------------------------------------------------------- copy BibTeX */
  var copy = document.getElementById("copy-bib");
  if (copy) copy.addEventListener("click", function () {
    var txt = document.getElementById("bibtex").textContent;
    var done = function () { copy.textContent = "Copied"; setTimeout(function () { copy.textContent = "Copy"; }, 1800); };
    if (navigator.clipboard) navigator.clipboard.writeText(txt).then(done, function () { copy.textContent = "Select & copy"; });
    else copy.textContent = "Select & copy";
  });
})();
