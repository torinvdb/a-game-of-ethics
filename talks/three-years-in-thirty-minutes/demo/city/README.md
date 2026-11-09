# City demo

A procedurally drawn pixel city that plays two of the talk's scenarios. Every change on screen
comes from the scenario state or the model's choice: who has power, whether the signature
control holds, how long an exception has left, how much work is queued.

* **Blackout Ledger.** Four decisions: the grid AI rations power between a hospital, a protest
  camp and a private arcology. Plays **live** against Claude, or replays a recorded run.
* **Cluster Pressure.** The talk's 36-month scenario, replayed from real E1b trajectories,
  sped up. About 150 decisions per run; too long to run live on stage.

Scripted control runs (labelled "Scripted control, not a model") show what failure looks like,
because no recorded Claude run took the harmful options.

### Sign text

The signs are standard Japanese words, each naming what the building or prop stands for. Sign
text is set in DotGothic16 and the title in Dela Gothic One, both under the SIL Open Font License
(`type/`).

| Sign | Reading | Meaning | Where |
| --- | --- | --- | --- |
| 倫理 | rinri | ethics | Intro title |
| 病院 | byōin | hospital | Blackout: the hospital |
| 電力 | denryoku | electric power | Blackout: the grid control hall |
| テント | tento | tent | Blackout: the protest camp |
| 塔 | tō | tower | Blackout: the private arcology |
| 故障 | koshō | fault, malfunction | Blackout: the false fault code on the tower |
| 軍 | gun | military | Blackout: the military council |
| 審査 | shinsa | review | Blackout: the Ombudsperson's office; Cluster: the review tower that receives escalations |
| 医療 | iryō | medical care | Cluster: medical services |
| 教育 | kyōiku | education | Cluster: education services |
| 署名 | shomei | signature | Cluster: the image-signature control |
| 例外 | reigai | exception | Cluster: a scoped exception is active |
| 期限 | kigen | deadline | Cluster: the exception expires this month |

## Run it

```bash
npm run demo:city          # http://127.0.0.1:8787, live runs on if .env has ANTHROPIC_API_KEY
```

Without a key the page still plays every recording. The server binds to 127.0.0.1 only.

| Key | Does |
| --- | --- |
| Space | Pause or resume |
| → | Skip the current wait or typing |
| + / − | Faster or slower (2× is good for Cluster Pressure) |
| Esc | Back to the run menu |
| I | Replay the intro |
| F | Fullscreen |

URL options: `?nointro`, `?run=data/blackout/<id>.json` to open a run directly, `?speed=2`.

## Live runs and spend

A live run sends exactly the requests the E1a experiment sends: same system prompt, framing,
settings and seeded option shuffle, through `benchmark/run/providers.mjs`. A run costs about
$0.001 on Haiku 5.5, $0.01 on Sonnet 5.5 and $0.03 on Opus 5.5. The server stops at
`DEMO_BUDGET_USD` (default $15), tracked in `recordings/.spend.json`. Every live run is saved to
`recordings/` and appears in the menu as a recording, so a rehearsal run is also a fallback.

If a live call fails, the run stops and says so. A failure is never shown as a choice.

## On stage

1. Before the session, open the page, let the intro play once, and do one live Haiku run to check
   the key and network. Press Esc to return to the menu.
2. Live: pick "Live: Claude Opus 5.5". About 30 seconds for four decisions.
3. Then a scripted control ("Obeys the council") to show what the city looks like when the agent
   follows the unlawful order.
4. Cluster Pressure: a recorded Opus run at 2×, then the scripted `delivery` control, which
   disables the signature control and shatters the shield.

Fallbacks, in order: replay the rehearsal's saved live run from the menu; play the videos in
`video/`; return to the slides. Say it's a recording whenever it is.

## Record

```bash
npm run demo:city &                                   # the recorder drives the running server
python3 talks/three-years-in-thirty-minutes/demo/city/record.py --intro --run data/blackout/claude-opus-5-5-path-3210.json --out talks/three-years-in-thirty-minutes/demo/city/video/opus.mp4
python3 talks/three-years-in-thirty-minutes/demo/city/record.py --intro --gif --width 800 --fps 12 --out img/readme/city-intro.gif
```

Cluster Pressure runs are long, so record them at 2× with room to finish:

```bash
python3 talks/three-years-in-thirty-minutes/demo/city/record.py --run data/cluster/claude-opus-5-5-generated-0.json --speed 2 --max-seconds 400 --out talks/three-years-in-thirty-minutes/demo/city/video/cluster-opus-2x.mp4
```

Recording is frame by frame on the page's own clock, so videos are smooth and repeatable.
Needs `pip install playwright==1.63.0` (then `python -m playwright install chromium`) and
`ffmpeg` on PATH, or `pip install imageio-ffmpeg` for a bundled binary (simplest on Windows).
On Windows, set `PYTHONUTF8=1` before running the deck build scripts.

Long narrative text is paged: a full terminal page is held for reading, then the next page
types in, so no text is ever written below the visible area.

## Data

`node talks/three-years-in-thirty-minutes/demo/city/bake.mjs` rebuilds `data/` from the E1a and
E1b run ledgers and `npm run ethics:demo` output. Blackout runs are replayed through the frozen
Ink story with the recorded choices, so the text on screen is what the model read. The choice
counts beside each option come from every recorded run of that model (both framings).

Fonts: VT323 and a subset of Dela Gothic One (`type/`), both SIL OFL 1.1.
