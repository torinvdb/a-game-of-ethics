"""Offline baseline policies exposed as an Inspect model provider.

    inspect eval agoe/agoe --model agoe_policy/random
    inspect eval agoe/agoe --model agoe_policy/first

These answer the solver's JSON prompt without any network call. `random`
picks uniformly among the presented options (an empirical check of the
manifest's uniform-random chance level); `first` and `last` always pick the
first or last presented option; `invalid` always returns non-JSON (to
exercise the failure path).
"""

from __future__ import annotations

import json
import random
import re
from typing import Any

from inspect_ai.model import ChatMessage, GenerateConfig, ModelAPI, ModelOutput, modelapi
from inspect_ai.tool import ToolChoice, ToolInfo

POLICIES = ("random", "first", "last", "invalid")


def count_options(messages: list[ChatMessage]) -> int:
    last = messages[-1].text if messages else ""
    tail = last.rsplit("Options:\n", 1)[-1]
    return len(re.findall(r"^\d+\. ", tail, re.M))


@modelapi(name="agoe_policy")
class AgoePolicyAPI(ModelAPI):
    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        api_key: str | None = None,
        config: GenerateConfig = GenerateConfig(),
        seed: int | None = None,
        **model_args: Any,
    ) -> None:
        super().__init__(model_name, base_url, api_key, [], config)
        if model_name not in POLICIES:
            raise ValueError(f"unknown agoe_policy {model_name!r}; expected one of {POLICIES}")
        self.rng = random.Random(seed if seed is not None else config.seed)

    async def generate(
        self,
        input: list[ChatMessage],
        tools: list[ToolInfo],
        tool_choice: ToolChoice,
        config: GenerateConfig,
    ) -> ModelOutput:
        n = count_options(input)
        if self.model_name == "invalid" or n == 0:
            return ModelOutput.from_content(model=self.model_name, content="I would rather not pick a number.")
        if self.model_name == "first":
            choice = 1
        elif self.model_name == "last":
            choice = n
        else:
            choice = self.rng.randint(1, n)
        content = json.dumps({"choice": choice, "rationale": f"{self.model_name} policy"})
        return ModelOutput.from_content(model=self.model_name, content=content)
