"""Chat models: the OpenAI chat completions API and an offline fake."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from openai import OpenAI

# The models the assignment allows (same list as week 4); "fake" is the offline stand-in.
ALLOWED_MODELS = (
    "gpt-6-luna",
    "gpt-5.6-luna",
    "gpt-5.4-nano",
    "gpt-5-nano",
    "gpt-5-mini",
    "gpt-4.1-nano",
    "gpt-4o-mini",
)
FAKE_MODEL = "fake"
DEFAULT_CHAT_MODEL = "gpt-6-luna"


@dataclass(frozen=True)
class Completion:
    text: str
    usage: dict[str, int] = field(default_factory=dict[str, int])  # prompt, completion, total


class ChatModel(Protocol):
    @property
    def model(self) -> str: ...

    def complete(self, system: str, user: str) -> Completion: ...


class OpenAIChat:
    """One chat completion per call; no temperature, which reasoning models reject."""

    def __init__(self, model: str, timeout_s: float = 300.0) -> None:
        self._model = model
        self._client = OpenAI(timeout=timeout_s)

    @property
    def model(self) -> str:
        return self._model

    def complete(self, system: str, user: str) -> Completion:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        usage: dict[str, int] = {}
        if response.usage is not None:
            usage = {
                "prompt": response.usage.prompt_tokens,
                "completion": response.usage.completion_tokens,
                "total": response.usage.total_tokens,
            }
        return Completion(response.choices[0].message.content or "", usage)


class FakeChat:
    """Offline stand-in: answers with the stub from the prompt (the last ```python block),
    its body replaced by ``raise NotImplementedError``, wrapped in prose like a real reply."""

    @property
    def model(self) -> str:
        return FAKE_MODEL

    def complete(self, system: str, user: str) -> Completion:
        del system
        stub = re.findall(r"```python\n(.*?)```", user, re.DOTALL)[-1]
        code = re.sub(r"\bpass\s*$", 'raise NotImplementedError("fake LLM")\n', stub)
        return Completion(f"Here is the method:\n\n```python\n{code}```\n")


def make_chat(model: str) -> ChatModel:
    if model == FAKE_MODEL:
        return FakeChat()
    if model not in ALLOWED_MODELS:
        raise ValueError(f"model {model!r} is not allowed; choose from {', '.join(ALLOWED_MODELS)}")
    return OpenAIChat(model)
