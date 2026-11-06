# E2 run notes (2026-11-06)

Free OpenRouter models, $0 spend. Prompts, scenarios, settings and `benchmark/run/analyze.py`
are unchanged from E1 except where the config says otherwise (temperature 1.0, JSON requested in
the prompt, `openai_max_tokens` 4000). The full model entries and every exclusion are in
[models.lock.json](models.lock.json).

## Model selection

Rule: the largest open-weights instruction or reasoning `:free` model per developer, at most four.

| Model | Role | Smoke | Pilot (held-out, 2 reps) |
| --- | --- | --- | --- |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | primary | 2/2 (one malformed response, retried) | 12/12, 0 failed attempts |
| `xingchen-agi/xing4.0-29b-a4b:free` | exploratory | 2/2 after 3 failed attempts | 11/12; 5 of 16 attempts failed (31%) |
| `google/gemma-4-31b-it:free` | dropped before smoke passed | 0/2 | not run |
| `google/gemma-4-26b-a4b-it:free` | replacement, dropped before smoke passed | 0/2 | not run |

Both Gemma endpoints sit on the same Google AI Studio shared pool and returned
`429 upstream_provider_shared_pool` on every attempt during the day. Xing4.0's failure rate is
over the 10% go threshold, so it is reported with that rate and kept out of the primary comparison.
`dots-3-note-preview` (280B) was excluded at selection: no Hugging Face weights to verify, and a
preview ID can change behind the name.

## Execution

* Concurrency 1. `ETHI_MAX_RETRIES=10` raised in-request retries for 429s (transport only).
* The free daily quota is 1,000 requests per key; the full stage needs about 1,000 per model, so it
  resumes across days with the same command.
* Removing the Gemma entries changed the config hash recorded in `run.json` between invocations.
  The Nemotron and Xing settings did not change.
* The key's credit limit was $50, not the $0 the plan called for. Usage stayed at $0; only `:free`
  IDs are in the config.

## Results

Pending the full stage.
