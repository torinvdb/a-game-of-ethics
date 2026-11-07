# E1 run notes (2026-11-06)

Deviations from DESIGN.md and execution events, recorded in run order. Prompts, scenarios,
settings and `benchmark/run/analyze.py` were not changed after the smoke stage. E1a pilot and
full ran with config sha256 `92e6f46d…6a0b`.

## Budget (before the smoke stage)

Stage caps were fitted to a $200 account limit: E1a full $160 to $120; E1b full 5 reps / $90 to
3 reps / $45; E1b pilot $10 to $14 (commits `c5691bf`, `585f648`). DESIGN.md §6 and §7 still show
the original caps.

## Go criteria

| Check | Result |
| --- | --- |
| Failure rate under 10% per model (pilot) | 0% for every model in E1a (156/156) and E1b (9/9) |
| E1a pilot cost × 15 within $120 | $1.89 × 15 = $28.28 |
| E1b pilot cost × 3 within $45 | $7.64 × 3 = $22.92 |

## Outcome

| Arm | Completed | Terminal failures | Cost |
| --- | --- | --- | ---: |
| E1a full | 2,335 / 2,340 | Haiku refusal 3, Opus refusal 1, Sonnet truncated 1 | $26.38 |
| E1b full | 45 / 45 (5 reps; 3 first, then extended within the $45 cap) | none | $37.89 |

## E1b execution failures and re-runs

The first E1b pilot invocation failed all 9 trajectories as `replay_crashed` before any API call:
`cluster.py` passed relative `--stories` / `--out` paths to a replay that runs with
`cwd=extensions/time-travel-ethics`. The pilot was re-run with absolute paths, one model at a time,
because the runner's budget cap did not stop submission (all jobs were queued while spend was $0).
Both bugs are fixed in `0905f35`.

52 E1b full trajectories ended as an execution failure (43 `bridge_timeout`, 9 `rate_limited`), an execution failure (the replay kills its
per-decision bridge process after a wall-clock limit). They were moved, not deleted, to
`runs/e1b-full-sleep-failures/` and re-run from month 1. Causes, in order:

| Batch | Failed | Cause | Fix |
| --- | ---: | --- | --- |
| first full run | 18 (Haiku 9, Sonnet 9) | macOS idle sleep; failures coincide with DarkWake events in `pmset -g log` | re-run under `caffeinate` |
| attempt 2 | 13 | sleep continued under `caffeinate -i` | `caffeinate -dimsu`, operator kept the machine awake |
| attempt 3 | 4 (Sonnet) | first attributed to the Anthropic client allowing 120 s × 5 attempts inside a 90 s decision budget; the same pattern recurred after that fix, so host overload (next row) is the likely cause | `8a3c766`: 40 s, 1 retry (kept as a correctness fix) |
| attempt 4 | 4 (Sonnet) | host overload (load average about 49 on 10 cores, heavy swapping from an unrelated process); the same decision answered in about 3 s when run directly | `a816a68`: 300 s decision budget for live runs |
| attempt 5 (reps 3-4) | 9 (Haiku 5, Sonnet 4) | `rate_limited`: E3 Inspect runs overlapped and briefly hit the account rate limit; the bridge had one retry | `20ae614`: 3 retries for the 300 s budget |

Re-running an execution failure from the start matches E1a's resume rule (failures are never
scored as choices). The final 45 trajectories mix transport settings (client timeouts, retries and the per-decision
wall-clock budget) across the fixes above. These affect retries and timeouts only, not requests.

## Spend

Anthropic total for E1, including failed attempts: $75.68 (E1a $28.26, E1b pilot $7.64,
E1b full kept $37.89, E1b failed attempts $1.89). Account total across E1, E3
and the demo on 2026-11-06: $82.67.

## Scenario text change after the runs

After E1a, E1b and E3 finished, the city's name was removed from `blackout-ledger.ink` for the
talk: "the megacity of Ashgrove Reach has been rebuilt" became "the megacity has been rebuilt",
and the closing line "Ashgrove Reach survived the cold front." became "The city survived the cold
front." Choices, scoring and every other line are unchanged. The manifest was re-frozen at 2.0.2.
`blackout-ledger` is held out, so under PROTOCOL.md section 4 results from the old and new text
are not strictly comparable. Every E1 and E3 result in this directory used the old text, and
`run.json` records its hash. These runs were not repeated.

