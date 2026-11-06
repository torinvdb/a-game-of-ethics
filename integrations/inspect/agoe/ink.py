"""Async client for ink_server.mjs (one Node subprocess per scenario run)."""

from __future__ import annotations

import json
import os
import shutil
from importlib.resources import files
from pathlib import Path
from typing import Any

import anyio
from anyio.abc import Process
from anyio.streams.buffered import BufferedByteReceiveStream

SERVER = Path(str(files("agoe").joinpath("ink_server.mjs")))
MAX_LINE = 64 * 1024 * 1024


class InkError(RuntimeError):
    """The Node bridge failed (missing node, compile error, crash, bad request)."""


def node_binary() -> str:
    node = os.environ.get("AGOE_NODE") or shutil.which("node")
    if not node:
        raise InkError("node not found on PATH (set AGOE_NODE to the node binary)")
    return node


class InkStory:
    """Drive one Ink story in a Node subprocess.

    Use as an async context manager::

        async with InkStory(repo_root, scenario_path) as story:
            step = await story.cont()
    """

    def __init__(self, repo_root: Path, scenario_path: Path, timeout: float = 120.0) -> None:
        self.repo_root = Path(repo_root)
        self.scenario_path = Path(scenario_path)
        self.timeout = timeout
        self.sha256: str | None = None
        self._proc: Process | None = None
        self._reader: BufferedByteReceiveStream | None = None

    async def __aenter__(self) -> "InkStory":
        self._proc = await anyio.open_process(
            [node_binary(), str(SERVER), str(self.repo_root)],
            cwd=str(self.repo_root),
        )
        assert self._proc.stdout is not None
        self._reader = BufferedByteReceiveStream(self._proc.stdout)
        res = await self._request({"cmd": "load", "path": str(self.scenario_path)})
        self.sha256 = res["sha256"]
        return self

    async def __aexit__(self, *exc: Any) -> None:
        proc = self._proc
        self._proc = None
        if proc is None:
            return
        with anyio.move_on_after(5):
            try:
                await self._request({"cmd": "quit"}, proc=proc)
            except Exception:
                pass
        if proc.returncode is None:
            proc.kill()
        with anyio.CancelScope(shield=True):
            await proc.aclose()

    async def _request(self, req: dict[str, Any], proc: Process | None = None) -> dict[str, Any]:
        proc = proc or self._proc
        if proc is None or proc.stdin is None or self._reader is None:
            raise InkError("ink server not running")
        try:
            with anyio.fail_after(self.timeout):
                await proc.stdin.send((json.dumps(req) + "\n").encode())
                line = await self._reader.receive_until(b"\n", MAX_LINE)
        except (anyio.EndOfStream, anyio.IncompleteRead, anyio.BrokenResourceError) as e:
            stderr = b""
            if proc.stderr is not None:
                with anyio.move_on_after(1):
                    try:
                        stderr = await proc.stderr.receive(65536)
                    except Exception:
                        pass
            raise InkError(f"ink server exited during {req.get('cmd')}: {stderr.decode(errors='replace')[-1000:]}") from e
        except TimeoutError as e:
            raise InkError(f"ink server timed out during {req.get('cmd')}") from e
        res = json.loads(line)
        if not res.get("ok"):
            raise InkError(f"{req.get('cmd')}: {res.get('error')}")
        return res

    async def cont(self) -> dict[str, Any]:
        """Continue maximally. Returns {text, choices, can_continue}."""
        return await self._request({"cmd": "continue"})

    async def choose(self, index: int) -> None:
        """Choose by ORIGINAL (unshuffled) choice index."""
        await self._request({"cmd": "choose", "index": index})

    async def variables(self) -> dict[str, Any]:
        return (await self._request({"cmd": "variables"}))["variables"]
