"""End-to-end Inspect runs against the real scenarios (Node + inkjs required)."""

import json
import math
import os
import subprocess
from pathlib import Path

import anyio
import pytest
from inspect_ai import eval as inspect_eval
from inspect_ai.log import read_eval_log
from inspect_ai.model import get_model

from agoe import agoe
from agoe.export import export
from agoe.ink import InkStory

from conftest import TWO, needs_node, pick, scripted

pytestmark = needs_node


def run(tmp_path, reply, epochs=1, **task_args):
    model = get_model("mockllm/model", custom_outputs=scripted(reply))
    task_args.setdefault("scenarios", TWO)
    [log] = inspect_eval(agoe(**task_args), model=model, epochs=epochs, log_dir=str(tmp_path / "logs"), display="none")
    return log


def scores(log):
    return [(s.id, s.epoch, s.scores["agoe_scorer"]) for s in log.samples]


async def replay(repo: Path, path: str, original_indices):
    async with InkStory(repo, repo / path) as story:
        for i in original_indices:
            cur = await story.cont()
            assert cur["choices"], "story ended before replay finished"
            await story.choose(i)
        cur = await story.cont()
        assert not cur["choices"]
        return await story.variables()


def test_mockllm_two_scenarios_complete_and_replay(tmp_path, repo):
    seen_schemas = []

    def reply(n, config):
        seen_schemas.append(config.response_schema)
        return pick(1)(n, config)

    log = run(tmp_path, reply, epochs=2)
    assert log.status == "success"
    assert len(log.samples) == 4
    # structured output requested with an enum of the presented positions
    rs = seen_schemas[0]
    assert rs is not None and rs.json_schema.properties["choice"].enum[0] == 1
    assert _metric(log, "completed", "mean") == 1.0
    for sid, epoch, sc in scores(log):
        v = sc.value
        assert v["completed"] == 1.0
        md = sc.metadata
        assert math.isclose(v["average"], md["ink_average"])
        assert md["verdict"] == md["ink_verdict"]  # tier from manifest thresholds equals the Ink text
        assert all(d["presented_index"] == 0 for d in md["decisions"])
        # replaying the recorded original indices reproduces the axes
        sample_meta = next(s.metadata for s in log.samples if s.id == sid)
        variables = anyio.run(replay, repo, sample_meta["path"], [d["original_index"] for d in md["decisions"]])
        assert {a: variables[a] for a in md["axes"]} == md["axes"]
    # epochs reshuffle: same position-1 answer maps to different original options
    orders = {(sid, ep): [tuple(d["order"]) for d in sc.metadata["decisions"]] for sid, ep, sc in scores(log)}
    assert orders[("convict-catastrophe", 1)] != orders[("convict-catastrophe", 2)]


def test_no_shuffle_is_deterministic(tmp_path):
    log = run(tmp_path, pick(1), epochs=2, shuffle_options=False)
    paths = {}
    for sid, ep, sc in scores(log):
        paths.setdefault(sid, set()).add(tuple(d["original_index"] for d in sc.metadata["decisions"]))
        assert all(d["order"] == list(range(d["n_options"])) for d in sc.metadata["decisions"])
    assert all(len(p) == 1 for p in paths.values())


def test_invalid_json_is_execution_failure(tmp_path):
    log = run(tmp_path, lambda n, c: ("I pick the second one.", "stop"))
    assert log.status == "success"
    for _, _, sc in scores(log):
        assert sc.value["completed"] == 0.0
        assert math.isnan(sc.value["average"])
        assert sc.metadata["failure_class"] == "schema_invalid"
        assert sc.metadata["at_decision"] == 0
    assert _metric(log, "completed", "mean") == 0.0
    # every score key is NaN for failed runs, so the average metric has no scored samples
    avg = next(x for x in log.results.scores if x.name == "average")
    assert avg.scored_samples == 0 and avg.unscored_samples == 2


def test_refusal_and_truncation(tmp_path):
    log = run(tmp_path, lambda n, c: ("", "content_filter"), scenarios="hostage-holdout")
    assert scores(log)[0][2].metadata["failure_class"] == "refusal"
    log = run(tmp_path, lambda n, c: ('{"choice": 1, "rat', "max_tokens"), scenarios="hostage-holdout")
    assert scores(log)[0][2].metadata["failure_class"] == "truncated"


def test_decision_cap(tmp_path):
    log = run(tmp_path, pick(1), scenarios="hostage-holdout", max_decisions=1)
    sc = scores(log)[0][2]
    assert sc.metadata["failure_class"] == "max_decisions"
    assert len(sc.metadata["decisions"]) == 1


def test_mixed_results_metrics(tmp_path):
    """Failures count toward completion rate but not the score mean."""
    good = run(tmp_path, pick(1), scenarios="hostage-holdout")
    good_avg = scores(good)[0][2].value["average"]

    model = get_model(
        "mockllm/model",
        custom_outputs=lambda input, t, tc, c: scripted(
            (lambda n, cfg: ("nope", "stop")) if "Kyln" in input[-1].text else pick(1)
        )(input, t, tc, c),
    )
    [log] = inspect_eval(agoe(scenarios=TWO), model=model, log_dir=str(tmp_path / "logs2"), display="none")
    by = {sid: sc for sid, _, sc in scores(log)}
    assert by["convict-catastrophe"].value["completed"] == 0.0
    assert by["hostage-holdout"].value["completed"] == 1.0
    assert math.isclose(_metric(log, "average", "mean"), good_avg)
    assert math.isclose(_metric(log, "completed", "mean"), 0.5)


def _metric(log, key, name):
    for s in log.results.scores:
        if s.name == key:
            return s.metrics[name].value
    raise KeyError((key, name, [s.name for s in log.results.scores]))


def test_cli_eval_log_dump_and_export(tmp_path, repo):
    """Real `inspect eval agoe/agoe` through the entry point, then log dump, export and analyze.py."""
    import shutil
    import sys
    candidates = [Path(sys.executable).parent / "inspect", Path(os.environ.get("VIRTUAL_ENV", "")) / "bin" / "inspect"]
    inspect_bin = next((str(c) for c in candidates if c.exists()), shutil.which("inspect"))
    if not inspect_bin:
        pytest.skip("inspect CLI not found next to this interpreter or on PATH")
    env = {**os.environ, "AGOE_ROOT": str(repo)}
    logs = tmp_path / "logs"
    r = subprocess.run(
        [inspect_bin, "eval", "agoe/agoe", "--model", "agoe_policy/first", "-T", f"scenarios={TWO}",
         "--epochs", "2", "--log-dir", str(logs), "--display", "none"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, r.stderr[-3000:]
    [log_file] = list(logs.glob("*.eval"))
    dump = json.loads(subprocess.run([inspect_bin, "log", "dump", str(log_file)], capture_output=True, text=True, check=True).stdout)
    assert dump["status"] == "success"
    assert dump["eval"]["task"] in ("agoe/agoe", "agoe")
    assert len(dump["samples"]) == 4
    assert all(s["scores"]["agoe_scorer"]["value"]["completed"] == 1.0 for s in dump["samples"])

    out = tmp_path / "ledger"
    counts = export(str(log_file), out)
    assert counts == {"results": 4, "errors": 0}
    assert export(str(log_file), out) == {"results": 0, "errors": 0}  # idempotent
    rows = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]
    assert {r["key"] for r in rows} == {f"first|{s}|deployment|{k}" for s in TWO.split(",") for k in (0, 1)}
    analyze = subprocess.run(
        [os.sys.executable, str(repo / "benchmark" / "run" / "analyze.py"), str(out), "--boot", "200"],
        capture_output=True, text=True, timeout=300,
    )
    assert analyze.returncode == 0, analyze.stderr[-3000:]
    summary = json.loads((out / "analysis" / "summary.json").read_text())
    assert summary["n_completed"] == 4


def test_inspect_limit_is_execution_failure(tmp_path):
    model = get_model("mockllm/model", custom_outputs=scripted(pick(1)))
    [log] = inspect_eval(agoe(scenarios="hostage-holdout"), model=model, message_limit=4,
                         log_dir=str(tmp_path / "logs"), display="none")
    sc = scores(log)[0][2]
    assert log.samples[0].limit is not None
    assert sc.value["completed"] == 0.0 and sc.metadata["failure_class"] == "limit_exceeded"
