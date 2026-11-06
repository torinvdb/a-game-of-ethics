// Retro sci-fi console theme for the ethi CLI.
//
// Art direction: late-80s / 90s cyberpunk terminal. Phosphor green body text,
// amber system messages, neon magenta / cyan accents, framed panels and a short
// boot sequence. All names here are original.
//
// Degrades cleanly:
//   NO_COLOR (any non-empty value) or --no-color  -> no ANSI colour
//   non-TTY stdout                                -> no colour, ASCII frames, no animation
//   --no-anim, ETHI_REDUCED_MOTION=1, CI          -> no animation (output is otherwise identical)
//   ETHI_ASCII=1 / TERM=dumb                      -> ASCII frames instead of box drawing

import { Chalk } from 'chalk';
import figlet from 'figlet';
import { AXES, AXIS_NAMES, verdictFor } from '../lib/scoring.js';

const TRUTHY = new Set(['1', 'true', 'yes', 'on']);

/** Work out what the output stream can do. Pure function of its inputs (testable). */
export function detectCapabilities({ env = process.env, stream = process.stdout, argv = process.argv } = {}) {
  const tty = Boolean(stream && stream.isTTY);
  const dumb = env.TERM === 'dumb';
  let colorLevel;
  if ((env.NO_COLOR !== undefined && env.NO_COLOR !== '') || argv.includes('--no-color')) {
    colorLevel = 0;
  } else if (env.FORCE_COLOR !== undefined) {
    const f = env.FORCE_COLOR;
    colorLevel = f === '' || f === 'true' ? 1 : f === 'false' ? 0 : Math.min(Math.max(Number.parseInt(f, 10) || 0, 0), 3);
  } else if (!tty || dumb) {
    colorLevel = 0;
  } else if (env.COLORTERM === 'truecolor' || env.COLORTERM === '24bit') {
    colorLevel = 3;
  } else if (/256/.test(env.TERM || '')) {
    colorLevel = 2;
  } else {
    colorLevel = 1;
  }
  const reducedMotion =
    TRUTHY.has(String(env.ETHI_REDUCED_MOTION || '').toLowerCase()) ||
    argv.includes('--no-anim') ||
    Boolean(env.CI);
  const unicode = tty && !dumb && !TRUTHY.has(String(env.ETHI_ASCII || '').toLowerCase());
  const columns = tty && stream.columns ? stream.columns : 80;
  return {
    tty,
    colorLevel,
    animate: tty && !reducedMotion,
    unicode,
    width: Math.max(40, Math.min(columns, 96))
  };
}

const PALETTE = {
  phosphor: '#39ff7a',
  phosphorDim: '#1f9d55',
  amber: '#ffb000',
  magenta: '#ff2bd6',
  cyan: '#00e5ff',
  alert: '#ff3b5c',
  steel: '#7a8ca3'
};

const FRAMES = {
  unicode: { tl: '╔', tr: '╗', bl: '╚', br: '╝', h: '═', v: '║', ml: '╟', mr: '╢', mh: '─', full: '█', empty: '░', mid: '│', scan: '▔' },
  ascii: { tl: '+', tr: '+', bl: '+', br: '+', h: '=', v: '|', ml: '+', mr: '+', mh: '-', full: '#', empty: '.', mid: '|', scan: '-' }
};

// eslint-disable-next-line no-control-regex
const ANSI_RE = /\x1b\[[0-9;]*m/g;
const WIDE_RE = /[ᄀ-ᅟ⺀-꓏가-힣豈-﫿︰-﹏＀-｠￠-￦]|\p{Extended_Pictographic}/u;

export const stripAnsi = (s) => String(s).replace(ANSI_RE, '');

/** Approximate terminal cell width (ANSI-aware, wide/emoji = 2). */
export function visibleWidth(s) {
  let w = 0;
  for (const ch of stripAnsi(s)) {
    const cp = ch.codePointAt(0);
    if (cp === 0xfe0f || cp === 0x200d || (cp >= 0x300 && cp <= 0x36f)) continue;
    w += WIDE_RE.test(ch) ? 2 : 1;
  }
  return w;
}

/** Word-wrap plain text to a cell width. Preserves blank lines. */
export function wrapText(text, width) {
  const out = [];
  for (const para of String(text).split('\n')) {
    if (para.trim() === '') {
      out.push('');
      continue;
    }
    let line = '';
    for (const word of para.split(/\s+/).filter(Boolean)) {
      let w = word;
      while (visibleWidth(w) > width) {
        if (line) {
          out.push(line);
          line = '';
        }
        out.push(w.slice(0, width));
        w = w.slice(width);
      }
      if (!line) line = w;
      else if (visibleWidth(line) + 1 + visibleWidth(w) <= width) line += ` ${w}`;
      else {
        out.push(line);
        line = w;
      }
    }
    if (line) out.push(line);
  }
  return out;
}

const padEnd = (s, width) => s + ' '.repeat(Math.max(0, width - visibleWidth(s)));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Create a theme bound to a capability set. Everything returns strings except
 * the explicitly async animation helpers, so output can be tested.
 */
export function createTheme(caps = detectCapabilities(), { stream = process.stdout, stdin = process.stdin } = {}) {
  const chalk = new Chalk({ level: caps.colorLevel });
  const f = caps.unicode ? FRAMES.unicode : FRAMES.ascii;
  const width = caps.width;

  const c = {
    text: chalk.hex(PALETTE.phosphor),
    dim: chalk.hex(PALETTE.phosphorDim),
    sys: chalk.hex(PALETTE.amber),
    accent: chalk.hex(PALETTE.magenta),
    info: chalk.hex(PALETTE.cyan),
    alert: chalk.hex(PALETTE.alert),
    steel: chalk.hex(PALETTE.steel),
    bold: chalk.bold,
    good: chalk.hex(PALETTE.phosphor).bold,
    warn: chalk.hex(PALETTE.amber).bold,
    bad: chalk.hex(PALETTE.alert).bold
  };

  const write = (s = '') => stream.write(`${s}\n`);

  /** ══[ LABEL ]══════ style rule. */
  function rule(label = '', color = c.dim) {
    const head = label ? `${f.h}${f.h}[ ${label} ]` : '';
    return color(head + f.h.repeat(Math.max(0, width - visibleWidth(head))));
  }

  /** Framed panel. body is plain text; it is wrapped then coloured. */
  function panel(body, { title = '', footer = '', color = c.text, frame = c.dim, titleColor = c.sys } = {}) {
    const inner = width - 4;
    const lines = Array.isArray(body) ? body : wrapText(body, inner);
    let top;
    if (title) {
      const fill = Math.max(0, width - 7 - visibleWidth(title));
      top = frame(`${f.tl}${f.h}[ `) + titleColor(title) + frame(` ]${f.h.repeat(fill)}${f.tr}`);
    } else {
      top = frame(`${f.tl}${f.h.repeat(inner + 2)}${f.tr}`);
    }
    let bottom;
    if (footer) {
      const fill = Math.max(0, width - 7 - visibleWidth(footer));
      bottom = frame(`${f.bl}${f.h.repeat(fill)}[ `) + c.steel(footer) + frame(` ]${f.h}${f.br}`);
    } else {
      bottom = frame(`${f.bl}${f.h.repeat(inner + 2)}${f.br}`);
    }
    const rows = lines.map((l) => `${frame(f.v)} ${padEnd(color(l), inner)} ${frame(f.v)}`);
    return [top, ...rows, bottom].join('\n');
  }

  /** Diverging bar meter centred on zero. */
  function meter(value, { half = 5, scale = 10 } = {}) {
    const v = Number.isFinite(value) ? value : 0;
    const cells = Math.min(half, Math.round((Math.abs(v) / scale) * half));
    const neg = v < 0 ? cells : 0;
    const pos = v > 0 ? cells : 0;
    const left = c.dim(f.empty.repeat(half - neg)) + c.alert(f.full.repeat(neg));
    const right = c.text(f.full.repeat(pos)) + c.dim(f.empty.repeat(half - pos));
    return `${left}${c.steel(f.mid)}${right}`;
  }

  const signed = (n) => {
    const v = Number.isFinite(n) ? Math.round(n * 100) / 100 : 0;
    return v > 0 ? `+${v}` : `${v}`;
  };

  /** Status bar: the 8 axes as small meters, 2 or 4 per row depending on width. */
  function axisStatus(scores = {}) {
    const values = AXES.map((a) => (Number.isFinite(scores[a]) ? scores[a] : 0));
    const scale = Math.max(5, ...values.map((v) => Math.abs(v)));
    const cellsFor = (a, i) => {
      const v = values[i];
      const tone = v > 0 ? c.text : v < 0 ? c.alert : c.sys;
      return `${c.info(a.toUpperCase())} ${meter(v, { half: 4, scale })} ${tone(signed(v).padStart(3))}`;
    };
    const perRow = width >= 88 ? 4 : 2;
    const rows = [];
    for (let i = 0; i < AXES.length; i += perRow) {
      rows.push(AXES.slice(i, i + perRow).map((a, j) => cellsFor(a, i + j)).join(c.dim('  ')));
    }
    return rows.join('\n');
  }

  /** Console-style menu entries for inquirer select prompts. */
  function menuChoices(choices) {
    return choices.map((text, i) => ({
      name: `${c.sys(`[${String(i + 1).padStart(2, '0')}]`)} ${c.text(text)}`,
      short: `[${String(i + 1).padStart(2, '0')}] ${text}`,
      value: i
    }));
  }

  /** Theme object for @inquirer prompts (prefix + highlight colours). */
  const promptTheme = {
    prefix: { idle: c.accent(caps.unicode ? '▸' : '>'), done: c.text(caps.unicode ? '✓' : '+') },
    style: {
      highlight: (s) => c.accent(stripAnsi(s)),
      message: (s) => c.sys(s),
      answer: (s) => c.info(s)
    }
  };

  function banner({ version = '2.0' } = {}) {
    if (!caps.tty) {
      return `A GAME OF ETHICS // moral arbitration console v${version}`;
    }
    const art = figlet.textSync('ETHICS', { font: caps.unicode ? 'ANSI Shadow' : 'Small' }).replace(/\s+$/, '');
    const shades = [c.text, c.text, c.info, c.info, c.accent, c.accent, c.accent];
    const lines = art.split('\n').map((l, i) => (shades[i] || c.accent)(l));
    return [
      c.dim(f.scan.repeat(width)),
      ...lines,
      `${c.sys('A GAME OF ETHICS')} ${c.dim('//')} ${c.info('MORAL ARBITRATION CONSOLE')} ${c.dim(`v${version}`)}`,
      c.steel(['Scenario-based alignment benchmark', '8 ethical axes', 'division 08'].join(caps.unicode ? '  ·  ' : '  -  ')),
      c.dim(f.scan.repeat(width))
    ].join('\n');
  }

  /**
   * Short boot sequence (< 1 s). Any key skips it. Prints instantly when
   * animation is off, and is silent on non-TTY output.
   */
  async function boot({ scenarios = 0 } = {}) {
    if (!caps.tty) return;
    const steps = [
      ['POWER-ON SELF TEST', 'OK'],
      ['MOUNTING SCENARIO CORE', `${scenarios} MODULES`],
      ['CALIBRATING ETHICAL AXES', '8/8'],
      ['HANDSHAKE // INFERENCE RELAY', 'STANDBY'],
      ['NEURAL LINK', 'ESTABLISHED']
    ];
    const line = ([label, status], last) =>
      `${c.dim('>')} ${c.sys(label.padEnd(30, '.'))} ${last ? c.accent.bold(status) : c.text(status)}`;
    if (!caps.animate) {
      steps.forEach((s, i) => write(line(s, i === steps.length - 1)));
      return;
    }
    let skipped = false;
    const canRaw = stdin && stdin.isTTY && typeof stdin.setRawMode === 'function';
    const onData = (buf) => {
      if (buf && buf[0] === 3) {
        // Ctrl-C during boot
        if (canRaw) stdin.setRawMode(false);
        process.exit(130);
      }
      skipped = true;
    };
    if (canRaw) {
      stdin.setRawMode(true);
      stdin.resume();
      stdin.on('data', onData);
    }
    try {
      for (let i = 0; i < steps.length; i++) {
        write(line(steps[i], i === steps.length - 1));
        if (!skipped) await sleep(110);
      }
    } finally {
      if (canRaw) {
        stdin.removeListener('data', onData);
        stdin.setRawMode(false);
        stdin.pause();
      }
    }
  }

  /** Print text a few characters at a time (only when animating). */
  async function typeOut(text, color = c.text) {
    if (!caps.animate) return write(color(text));
    for (const l of String(text).split('\n')) {
      stream.write(color(l));
      stream.write('\n');
      await sleep(12);
    }
  }

  /** Dramatic but readable verdict screen. */
  function verdictScreen({ scores = {}, average, total, actor = 'SUBJECT' } = {}) {
    const verdict = verdictFor(average);
    const tone = c[verdict.tone];
    const [word, ...rest] = verdict.text.split(' - ');
    const big = caps.tty
      ? figlet.textSync(word, { font: caps.unicode ? 'Future' : 'Small' }).replace(/\s+$/, '').split('\n')
      : [word];
    const body = [
      c.steel(`ARBITRATION RESULT // ${actor}`),
      '',
      ...big.map((l) => tone(l)),
      '',
      c.text(rest.join(' - ')),
      '',
      ...axisStatus(scores).split('\n'),
      '',
      `${c.sys('AVERAGE/AXIS')} ${tone(signed(average))}   ${c.sys('TOTAL')} ${tone(signed(total))}`
    ];
    return panel(body, { title: 'VERDICT', titleColor: c.accent.bold, frame: tone, footer: verdict.key });
  }

  /** Classic score table as plain lines (used alongside the verdict screen). */
  function scoreLines(scores = {}) {
    return AXES.filter((a) => a in scores).map((a) => `${c.info(a.toUpperCase().padEnd(3))} ${c.text((AXIS_NAMES[a] || a).padEnd(24))} ${signed(scores[a]).padStart(4)}`);
  }

  return {
    caps,
    chalk,
    c,
    frames: f,
    width,
    write,
    rule,
    panel,
    meter,
    axisStatus,
    menuChoices,
    promptTheme,
    banner,
    boot,
    typeOut,
    verdictScreen,
    scoreLines,
    signed
  };
}

let shared;
/** Process-wide theme (lazily created so env/argv are read at first use). */
export function ui() {
  if (!shared) shared = createTheme();
  return shared;
}
