"""Trace records, per-node timing wrapper and state snapshots."""

import json
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, TextIO

from pydantic import BaseModel

from req_refinery.llm import LLMCallError, LLMClient
from req_refinery.state import TraceRecord


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def to_plain(value: object) -> object:
    """Convert Pydantic models nested in containers into JSON-ready data."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {str(k): to_plain(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [to_plain(v) for v in value]
    return value


class TraceWriter:
    """Appends trace records to trace.jsonl, flushing after every record."""

    def __init__(self, path: Path) -> None:
        self._fh: TextIO = path.open("a", encoding="utf-8")

    def write(self, record: TraceRecord) -> None:
        _ = self._fh.write(record.model_dump_json() + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


@dataclass
class Deps:
    llm: LLMClient
    tracer: TraceWriter
    models: dict[str, str] = field(default_factory=dict[str, str])


@dataclass
class NodeResult:
    update: dict[str, Any]
    payload: dict[str, Any]
    round: int


type NodeImpl[S] = Callable[[S, Deps], Awaitable[NodeResult]]


class NodeFn[S](Protocol):
    """A LangGraph node callable; the parameter must be named ``state``."""

    def __call__(self, state: S) -> Awaitable[dict[str, Any]]: ...


def traced[S](name: str, impl: NodeImpl[S], deps: Deps) -> NodeFn[S]:
    """Wrap a node so every execution appends one TraceRecord, even on failure."""

    async def run(state: S) -> dict[str, Any]:
        started = now_iso()
        t0 = time.perf_counter()
        try:
            result = await impl(state, deps)
        except Exception as exc:
            payload: dict[str, Any] = {"error": f"{type(exc).__name__}: {exc}"}
            if isinstance(exc, LLMCallError):
                payload["llm_calls"] = exc.records
            deps.tracer.write(
                TraceRecord(
                    node=name,
                    round=-1,
                    started_at=started,
                    ended_at=now_iso(),
                    duration_ms=int((time.perf_counter() - t0) * 1000),
                    payload=payload,
                )
            )
            raise
        record = TraceRecord(
            node=name,
            round=result.round,
            started_at=started,
            ended_at=now_iso(),
            duration_ms=int((time.perf_counter() - t0) * 1000),
            payload=_jsonable(result.payload),
        )
        deps.tracer.write(record)
        return {**result.update, "trace": [record]}

    return run


def _jsonable(payload: dict[str, Any]) -> dict[str, Any]:
    plain = to_plain(payload)
    assert isinstance(plain, dict)
    return json.loads(json.dumps(plain, default=str))


def write_snapshot(state_dir: Path, index: int, label: str, state: Mapping[str, Any]) -> None:
    """Save the full state (minus the trace, which lives in trace.jsonl)."""
    data = {k: to_plain(v) for k, v in state.items() if k != "trace"}
    data["trace_records"] = len(state.get("trace", []))
    path = state_dir / f"{index:02d}_{label}.json"
    _ = path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
