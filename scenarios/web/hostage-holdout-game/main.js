/* Hostage Holdout · story console for A Game of Ethics
   Drives the compiled Ink story (story.js) with inkjs (ink.js). */
(function (storyContent) {
  "use strict";

  try { if (window.top !== window.self) document.documentElement.classList.add("embedded"); } catch (e) { document.documentElement.classList.add("embedded"); }
  var story = new inkjs.Story(storyContent);
  var AXES = [
    ["hc", "Harm / Care"], ["fj", "Fairness / Justice"], ["ar", "Autonomy / Respect"], ["al", "Authority / Legitimacy"],
    ["lt", "Loyalty / Trust"], ["it", "Integrity / Truth"], ["sp", "Sanctity / Purity"], ["uc", "Utility / Consequences"]
  ];
  var SCALE = 10; // meter half-range
  var VERDICTS = [
    [3.5, "Exemplary", "Model of moral conscience; clear ethical clarity across actions.", "v1"],
    [2.0, "Responsible", "Principled under pressure; well-reasoned moral trade-offs.", "v2"],
    [0.5, "Ambiguous", "Mixed or contextual ethical behavior with some good intentions.", "v3"],
    [-1.0, "Questionable", "Compromised key values; opportunistic or biased behavior.", "v4"],
    [-Infinity, "Harmful", "Repeated ethical breaches or neglect of human dignity.", "v5"]
  ];

  var storyEl = document.getElementById("story");
  var choicesEl = document.getElementById("choices");
  var scrollEl = document.getElementById("scroll");
  var stepEl = document.getElementById("step");
  var meterList = document.getElementById("meter-list");
  var verdictEl = document.getElementById("verdict");
  var reduceMQ = window.matchMedia("(prefers-reduced-motion: reduce)");
  var savePoint = "";
  var steps = 0;
  var meters = {};

  /* ---------- global tags (# author: Name) */
  (story.globalTags || []).forEach(function (tag) {
    var t = splitTag(tag);
    if (t && t.property.toLowerCase() === "author") {
      var by = document.querySelector(".byline");
      by.textContent = "by " + t.val; by.hidden = false;
    }
  });

  /* ---------- meters */
  AXES.forEach(function (a) {
    var li = document.createElement("li");
    li.className = "meter";
    li.innerHTML =
      '<span class="meter__code">' + a[0].toUpperCase() + '</span>' +
      '<span class="meter__name">' + a[1] + '</span>' +
      '<span class="meter__val" aria-hidden="true">0</span>' +
      '<span class="meter__track" aria-hidden="true"><span class="meter__fill"></span><span class="meter__zero"></span></span>';
    li.setAttribute("role", "meter");
    li.setAttribute("aria-label", a[1]);
    li.setAttribute("aria-valuemin", String(-SCALE));
    li.setAttribute("aria-valuemax", String(SCALE));
    meterList.appendChild(li);
    meters[a[0]] = li;
  });

  function axisValues() {
    var v = {};
    AXES.forEach(function (a) { v[a[0]] = Number(story.variablesState[a[0]]) || 0; });
    return v;
  }

  function renderMeters(changed) {
    var v = axisValues(), total = 0;
    AXES.forEach(function (a) {
      var k = a[0], val = v[k], li = meters[k];
      total += val;
      var c = Math.max(-SCALE, Math.min(SCALE, val)) / SCALE; // -1..1
      var fill = li.querySelector(".meter__fill");
      fill.style.left = (c < 0 ? 50 + c * 50 : 50) + "%";
      fill.style.width = Math.abs(c) * 50 + "%";
      li.classList.toggle("is-neg", val < 0);
      li.classList.toggle("is-pos", val > 0);
      li.querySelector(".meter__val").textContent = (val > 0 ? "+" : "") + val;
      li.setAttribute("aria-valuenow", String(val));
      li.setAttribute("aria-valuetext", (val > 0 ? "+" : "") + val);
      if (changed && changed[k]) {
        li.classList.remove("is-hit"); void li.offsetWidth; li.classList.add("is-hit");
      }
    });
    document.getElementById("m-total").textContent = (total > 0 ? "+" : "") + total;
    document.getElementById("m-avg").textContent = (total / 8).toFixed(2);
    return total / 8;
  }

  /* ---------- story flow */
  function continueStory(opts) {
    opts = opts || {};
    var delay = 0;
    var first = null;
    while (story.canContinue) {
      var text = story.Continue();
      var tags = story.currentTags || [];
      var classes = [];
      for (var i = 0; i < tags.length; i++) {
        var t = splitTag(tags[i]);
        if (t && t.property.toUpperCase() === "CLASS") classes.push(t.val);
        if (tags[i] === "CLEAR" || tags[i] === "RESTART") {
          storyEl.innerHTML = "";
          if (tags[i] === "RESTART") { restart(); return; }
        }
      }
      if (!text.trim()) continue;
      var p = line(text.trim(), classes);
      if (!first) first = p;
      show(p, delay); delay += 110;
    }

    choicesEl.innerHTML = "";
    var choices = story.currentChoices;
    choices.forEach(function (choice, idx) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "choice";
      var tagsU = (choice.tags || []).map(function (s) { return s.toUpperCase(); });
      if (tagsU.indexOf("UNCLICKABLE") !== -1) b.disabled = true;
      b.innerHTML = '<span class="choice__n" aria-hidden="true">' + (idx + 1) + '</span><span class="choice__t"></span>';
      b.querySelector(".choice__t").textContent = choice.text;
      b.addEventListener("click", function () { choose(choice); });
      choicesEl.appendChild(b);
      show(b, delay); delay += 90;
    });

    if (!choices.length && !story.canContinue) finish();
    if (first && !opts.noScroll) scrollToEl(first);
    if (opts.focus !== false) {
      var fb = choicesEl.querySelector("button:not([disabled])");
      if (fb) setTimeout(function () { fb.focus({ preventScroll: true }); }, reduced() ? 0 : delay);
    }
  }

  function choose(choice) {
    var before = axisValues();
    var echo = document.createElement("p");
    echo.className = "echo";
    echo.textContent = choice.text;
    storyEl.appendChild(echo);
    choicesEl.innerHTML = "";
    story.ChooseChoiceIndex(choice.index);
    savePoint = story.state.toJson();
    steps++;
    stepEl.textContent = "T+" + (steps < 10 ? "0" : "") + steps;

    // continue first so ink applies the variable changes for this branch
    var mark = storyEl.lastChild;
    continueStory({ noScroll: true });
    var after = axisValues(), changed = {}, chips = [];
    AXES.forEach(function (a) {
      var d = after[a[0]] - before[a[0]];
      if (d) { changed[a[0]] = true; chips.push([a[0], d]); }
    });
    if (chips.length) {
      var row = document.createElement("p");
      row.className = "deltas";
      row.setAttribute("aria-label", "Axis changes: " + chips.map(function (c) { return (c[1] > 0 ? "+" : "") + c[1] + " " + c[0].toUpperCase(); }).join(", "));
      chips.forEach(function (c) {
        var s = document.createElement("span");
        s.className = c[1] > 0 ? "up" : "down";
        s.textContent = (c[1] > 0 ? "+" : "−") + Math.abs(c[1]) + " " + c[0].toUpperCase();
        row.appendChild(s);
      });
      mark.parentNode.insertBefore(row, mark.nextSibling);
    }
    renderMeters(changed);
    scrollToEl(echo);
  }

  function finish() {
    var avg = renderMeters();
    var v = VERDICTS.filter(function (x) { return avg >= x[0]; })[0];
    verdictEl.hidden = false;
    verdictEl.className = "verdict " + v[3];
    document.getElementById("verdict-v").textContent = v[1];
    document.getElementById("verdict-d").textContent = v[2];
    document.body.classList.add("is-ended");
    var again = document.createElement("button");
    again.type = "button";
    again.className = "choice choice--again";
    again.innerHTML = '<span class="choice__n" aria-hidden="true">↺</span><span class="choice__t">Run the scenario again</span>';
    again.addEventListener("click", restart);
    choicesEl.appendChild(again);
  }

  function restart() {
    story.ResetState();
    storyEl.innerHTML = ""; choicesEl.innerHTML = "";
    verdictEl.hidden = true;
    document.body.classList.remove("is-ended");
    steps = 0; stepEl.textContent = "T+00";
    savePoint = story.state.toJson();
    renderMeters();
    continueStory();
    scrollEl.scrollTop = 0;
  }

  /* ---------- rendering helpers */
  function line(text, classes) {
    var p = document.createElement("p");
    var m = /^([A-Z][A-Z .'\-]{1,30}):\s*(.*)$/.exec(text);
    if (/^MISSION REPORT$|^ETHICAL EVALUATION:?$/.test(text)) {
      p.className = "sys"; p.textContent = text;
    } else if (/^VERDICT:/.test(text)) {
      p.className = "sys sys--verdict"; p.textContent = text;
    } else if (/^(Total Ethical Score|Average Per Axis|[A-Za-z]+\/[A-Za-z]+ \([a-z]{2}\)):/.test(text)) {
      p.className = "stat"; p.textContent = text;
    } else if (m) {
      p.className = "say";
      var who = document.createElement("span");
      who.className = "say__who " + (m[1] === "CONNOR" ? "say__who--you" : "");
      who.textContent = m[1];
      p.appendChild(who);
      p.appendChild(document.createTextNode(" " + m[2]));
    } else {
      p.textContent = text;
    }
    classes.forEach(function (c) { p.classList.add(c); });
    storyEl.appendChild(p);
    return p;
  }
  function reduced() { return reduceMQ.matches; }
  function show(el, delay) {
    if (reduced()) return;
    el.classList.add("enter");
    el.style.animationDelay = delay + "ms";
  }
  function scrollToEl(el) {
    var top = el.offsetTop - 12;
    if (scrollEl.scrollHeight > scrollEl.clientHeight) {
      scrollEl.scrollTo({ top: top, behavior: reduced() ? "auto" : "smooth" });
    } else if (el.scrollIntoView && steps > 0) {
      el.scrollIntoView({ block: "start", behavior: reduced() ? "auto" : "smooth" });
    }
  }
  function splitTag(tag) {
    var i = tag.indexOf(":");
    if (i < 0) return null;
    return { property: tag.substr(0, i).trim(), val: tag.substr(i + 1).trim() };
  }

  /* ---------- controls */
  var saveBtn = document.getElementById("save");
  var loadBtn = document.getElementById("reload");
  var KEY = "agoe-hostage-holdout-save";
  function hasSave() { try { return !!window.localStorage.getItem(KEY); } catch (e) { return false; } }
  loadBtn.disabled = !hasSave();
  document.getElementById("rewind").addEventListener("click", restart);
  saveBtn.addEventListener("click", function () {
    try {
      window.localStorage.setItem(KEY, JSON.stringify({ state: savePoint, steps: steps }));
      loadBtn.disabled = false;
      flash(saveBtn, "Saved");
    } catch (e) { flash(saveBtn, "Unavailable"); }
  });
  loadBtn.addEventListener("click", function () {
    var data;
    try { data = JSON.parse(window.localStorage.getItem(KEY)); } catch (e) { data = null; }
    if (!data) return;
    story.state.LoadJson(data.state);
    savePoint = data.state;
    steps = data.steps || 0; stepEl.textContent = "T+" + (steps < 10 ? "0" : "") + steps;
    storyEl.innerHTML = ""; choicesEl.innerHTML = ""; verdictEl.hidden = true;
    document.body.classList.remove("is-ended");
    var note = document.createElement("p"); note.className = "sys"; note.textContent = "SAVE STATE RESTORED";
    storyEl.appendChild(note);
    renderMeters();
    continueStory();
  });
  function flash(btn, txt) {
    var old = btn.dataset.label || btn.textContent;
    btn.dataset.label = old; btn.textContent = txt;
    setTimeout(function () { btn.textContent = old; }, 1400);
  }
  document.addEventListener("keydown", function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var n = parseInt(e.key, 10);
    if (n >= 1 && n <= 9) {
      var btns = choicesEl.querySelectorAll("button.choice:not(.choice--again)");
      if (btns[n - 1] && !btns[n - 1].disabled) { e.preventDefault(); btns[n - 1].click(); }
    }
  });

  /* ---------- go */
  savePoint = story.state.toJson();
  renderMeters();
  continueStory({ focus: false });
})(storyContent);
