# Demo runbook: slide 10 (4 minutes, Vicente)

Everything here runs **offline**: no model credentials, no cluster, no Wi-Fi.
The policies are scripted calibration controls, so the "right answer" is known.
Say so on stage: known answers are what make it a calibration run.

## Before the session (T-60 min)

Run each block from the repository root.

```bash
npm ci
```

```bash
npm run ethics:test
```

```bash
npm run ethics:demo -- --output extensions/time-travel-ethics/runs/kubecon
```

The demo's last line must start with `Verified scripted calibrations`.
Pre-generate the run you will show, so the live step is a replay, not a build.

```bash
python3 talks/three-years-in-thirty-minutes/demo/replay.py extensions/time-travel-ethics/runs/kubecon --compare
```

Expected comparison (recorded 2026-11-06, inkjs 2.4.0, Python 3.13):

| policy | choices | violations | med/edu | backlog | expiry reviews |
| --- | ---: | ---: | --- | ---: | ---: |
| impact-aware | 144 | 0 | 18/18 | 0 | 0 |
| delivery | 179 | 107 | 84/0 | 0 | 0 |
| exceptions | 155 | 0 | 18/18 | 0 | 11 |
| defer-batch | 144 | 0 | 0/0 | 36 | 0 |
| label-biased | 144 | 0 | 0/84 | 0 | 0 |
| impact-aware-swapped | 144 | 0 | 18/18 | 0 | 0 |
| label-biased-swapped | 144 | 0 | 84/0 | 0 | 0 |
| rejected-live-adapter | 0 | 0 | 0/0 | 0 | 0 (intentionally rejected; incomplete) |

If any number differs, **do not demo live**: use the fallback below and fix later.

Terminal setup: dark theme, font ≥ 22 pt, 100 columns, `export NO_COLOR=` unset,
notifications off, the repository already `cd`'d into, the three commands below in
shell history.

## On stage (≈ 3 min 30 s)

| Time | Do | Say |
| --- | --- | --- |
| 0:00 | Switch to the terminal | "This runs offline; these are scripted controls, not a model." |
| 0:15 | `npm run ethics:demo -- --output extensions/time-travel-ethics/runs/live` | "Eight 36-month trajectories in about two seconds." |
| 0:35 | `python3 talks/three-years-in-thirty-minutes/demo/replay.py extensions/time-travel-ethics/runs/live --policy delivery --months 1-2` and press Enter through the choices | "Month one: it disables the signature control. Month two: the scenario remembers and offers restore or keep." |
| 1:50 | `python3 talks/three-years-in-thirty-minutes/demo/replay.py extensions/time-travel-ethics/runs/live --policy exceptions --find expiry --auto` | "Scoped exception: granted, and later it expires and forces a review." |
| 2:50 | `python3 talks/three-years-in-thirty-minutes/demo/replay.py extensions/time-travel-ethics/runs/live --compare` | "All policies side by side. Torin, what does it tell us?" **HANDOFF** |

## Fallbacks, in order

1. **Command fails or output differs.** Stop typing. Say "here's the recorded run"
   and replay `runs/kubecon` (pre-generated) with the same commands.
2. **Terminal or laptop can't be shown.** Return to the slides: slide 10's
   animated console shows the recorded lines, and appendix A2 has the recorded numbers.
   Say explicitly that it's a recording.
3. **Out of time.** Skip the live part entirely; describe slide 10's console in 30 s.

Never debug on stage. Never claim the recording is live.

## What the demo does not show

No real model, provider or local inference; no Kubernetes rollout; no telemetry
collection. See `docs/agentic-ethics/VALIDATION.md` before answering questions about them.
