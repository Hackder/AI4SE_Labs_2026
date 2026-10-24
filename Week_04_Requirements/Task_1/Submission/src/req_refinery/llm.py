"""Structured LLM calls with one validation retry and full call records."""

import asyncio
import json
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

import openai
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


@dataclass
class LLMResponse:
    parsed: BaseModel | None
    raw_text: str
    usage: dict[str, int]
    parsing_error: str | None = None
    transport_retries: int = 0


class LLMClient(Protocol):
    async def ainvoke(
        self, model: str, messages: Sequence[BaseMessage], schema: type[BaseModel]
    ) -> LLMResponse: ...


@dataclass
class OpenAIClient:
    """Real client: ChatOpenAI with structured output, default endpoint."""

    timeout_s: float = 900.0
    max_concurrency: int = 8
    transport_attempts: int = 4
    backoff_s: tuple[float, ...] = (5.0, 15.0, 30.0)
    _models: dict[str, ChatOpenAI] = field(default_factory=dict[str, ChatOpenAI])
    _gate: asyncio.Semaphore | None = None

    def _semaphore(self) -> asyncio.Semaphore:
        if self._gate is None:
            self._gate = asyncio.Semaphore(self.max_concurrency)
        return self._gate

    def _chat(self, model: str) -> ChatOpenAI:
        if model not in self._models:
            self._models[model] = ChatOpenAI(
                model=model, timeout=self.timeout_s, streaming=True, stream_usage=True
            )
        return self._models[model]

    async def ainvoke(
        self, model: str, messages: Sequence[BaseMessage], schema: type[BaseModel]
    ) -> LLMResponse:
        runnable = self._chat(model).with_structured_output(schema, include_raw=True)
        retries = 0
        async with self._semaphore():
            while True:
                try:
                    out = await runnable.ainvoke(list(messages))
                    break
                except openai.APIConnectionError:
                    # dropped or timed-out connections (also mid-stream) are retried here;
                    # schema failures are handled by structured_call's single retry
                    if retries + 1 >= self.transport_attempts:
                        raise
                    await asyncio.sleep(self.backoff_s[min(retries, len(self.backoff_s) - 1)])
                    retries += 1
        if not isinstance(out, dict):
            return LLMResponse(parsed=out, raw_text="", usage={}, transport_retries=retries)
        raw: object = out.get("raw")
        parsed: object = out.get("parsed")
        error: object = out.get("parsing_error")
        raw_text = ""
        usage: dict[str, int] = {}
        if isinstance(raw, AIMessage):
            raw_text = raw.content if isinstance(raw.content, str) else str(raw.content)
            if raw.usage_metadata is not None:
                usage = {
                    "prompt": raw.usage_metadata["input_tokens"],
                    "completion": raw.usage_metadata["output_tokens"],
                    "total": raw.usage_metadata["total_tokens"],
                }
        return LLMResponse(
            parsed=parsed if isinstance(parsed, BaseModel) else None,
            raw_text=raw_text,
            usage=usage,
            parsing_error=None if error is None else str(error),
            transport_retries=retries,
        )


class LLMCallError(RuntimeError):
    """Raised after the retry also failed; carries the attempt records."""

    def __init__(self, message: str, records: list[dict[str, Any]]) -> None:
        super().__init__(message)
        self.records: list[dict[str, Any]] = records


def to_json(payload: object) -> str:
    return json.dumps(payload, indent=1, ensure_ascii=False)


async def structured_call[T: BaseModel](
    client: LLMClient,
    model: str,
    system: str,
    payload: dict[str, Any],
    schema: type[T],
    check: Callable[[T], None] | None = None,
    soft_check: Callable[[T], str | None] | None = None,
) -> tuple[T, list[dict[str, Any]]]:
    """Call the model; on schema or check failure retry once with the error appended.

    soft_check returns an error message or None; a soft failure is retried once like a
    hard one, but on the second attempt the response is returned anyway and the record
    is marked with soft_check_failed so the caller can repair it deterministically.
    Returns the parsed object and one call record per attempt for the trace.
    """
    messages: list[BaseMessage] = [
        SystemMessage(content=system),
        HumanMessage(content=to_json(payload)),
    ]
    records: list[dict[str, Any]] = []
    last_error = ""
    for attempt in (1, 2):
        t0 = time.perf_counter()
        record: dict[str, Any] = {
            "attempt": attempt,
            "model": model,
            "messages": [{"role": m.type, "content": m.content} for m in messages],
        }
        records.append(record)
        try:
            response = await client.ainvoke(model, messages, schema)
            record["raw_response"] = response.raw_text
            record["usage"] = response.usage
            record["transport_retries"] = response.transport_retries
            if response.parsing_error is not None:
                raise ValueError(response.parsing_error)
            parsed = response.parsed
            if not isinstance(parsed, schema):
                raise TypeError(f"response did not parse into {schema.__name__}")
            record["parsed"] = parsed.model_dump()
            if check is not None:
                check(parsed)
            if soft_check is not None and (problem := soft_check(parsed)) is not None:
                if attempt == 1:
                    raise ValueError(problem)
                record["soft_check_failed"] = problem
            record["duration_ms"] = int((time.perf_counter() - t0) * 1000)
            return parsed, records
        except Exception as exc:  # noqa: BLE001 - any failure triggers the one retry
            last_error = f"{type(exc).__name__}: {exc}"
            record["error"] = last_error
            record["duration_ms"] = int((time.perf_counter() - t0) * 1000)
            messages = [
                *messages,
                HumanMessage(
                    content=(
                        "Your previous response was rejected with this error:\n"
                        f"{last_error}\nRespond again, fixing the problem."
                    )
                ),
            ]
    raise LLMCallError(f"{schema.__name__} call to {model} failed twice: {last_error}", records)
