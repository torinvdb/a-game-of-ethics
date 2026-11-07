import json
import re
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
TWO = "convict-catastrophe,hostage-holdout"

needs_node = pytest.mark.skipif(shutil.which("node") is None, reason="node not on PATH")


def option_count(messages) -> int:
    tail = messages[-1].text.rsplit("Options:\n", 1)[-1]
    return len(re.findall(r"^\d+\. ", tail, re.M))


def scripted(reply):
    """mockllm custom_outputs callable: reply(n_options, config) -> (content, stop_reason)."""
    from inspect_ai.model import ModelOutput, ModelUsage

    def fn(input, tools, tool_choice, config):
        content, stop = reply(option_count(input), config)
        out = ModelOutput.from_content(model="mockllm", content=content, stop_reason=stop)
        # Usage set explicitly so mockllm does not fetch a tiktoken encoding.
        out.usage = ModelUsage(input_tokens=10, output_tokens=5, total_tokens=15)
        return out

    return fn


@pytest.fixture
def repo() -> Path:
    return REPO


def pick(k):
    return lambda n, config: (json.dumps({"choice": min(k, n), "rationale": "test"}), "stop")


@pytest.fixture
def python() -> str:
    return sys.executable
