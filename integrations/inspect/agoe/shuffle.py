"""Seeded option permutation, bit-for-bit identical to benchmark/run/run.mjs.

run.mjs seeds mulberry32 with the first 8 hex digits of
sha256(f"{experiment_id}|{model}|{scenario}|{framing}|{rep}") and draws a
Fisher-Yates permutation per decision point from one stream per run.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable

M32 = 0xFFFFFFFF


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def cell_seed(experiment_id: str, model: str, scenario: str, framing: str, rep: int) -> str:
    return sha256_hex(f"{experiment_id}|{model}|{scenario}|{framing}|{rep}")


def _imul(a: int, b: int) -> int:
    return (a * b) & M32


def mulberry32(seed_hex: str) -> Callable[[], float]:
    state = int(seed_hex[:8], 16) & M32

    def rand() -> float:
        nonlocal state
        state = (state + 0x6D2B79F5) & M32
        t = state
        t = _imul(t ^ (t >> 15), t | 1)
        t ^= (t + _imul(t ^ (t >> 7), t | 61)) & M32
        return ((t ^ (t >> 14)) & M32) / 4294967296

    return rand


def permutation(n: int, rand: Callable[[], float]) -> list[int]:
    """order[k] = original index shown at presented position k."""
    p = list(range(n))
    for i in range(n - 1, 0, -1):
        j = int(rand() * (i + 1))
        p[i], p[j] = p[j], p[i]
    return p
