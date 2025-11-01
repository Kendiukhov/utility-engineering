"""LLM client abstractions for experiments."""

from __future__ import annotations

import abc
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

try:
    import openai
except Exception:  # pragma: no cover - optional dependency may be missing
    openai = None  # type: ignore


class LLMClient(abc.ABC):
    """Abstract base class for language model clients."""

    model: str

    @abc.abstractmethod
    async def generate(self, *, system: str, prompt: str, temperature: float, max_tokens: Optional[int]) -> str:
        """Return the model's response to the provided prompt."""


@dataclass
class MockLLMClient(LLMClient):
    """Deterministic mock for unit testing and offline experimentation."""

    model: str = "mock-model"
    scripted_responses: Dict[str, str] | None = None

    async def generate(
        self, *, system: str, prompt: str, temperature: float, max_tokens: Optional[int]
    ) -> str:
        key = f"{system}\n\n{prompt}"
        if self.scripted_responses and key in self.scripted_responses:
            return self.scripted_responses[key]
        return "[[no-scripted-response]]"


class OpenAIClient(LLMClient):  # pragma: no cover - requires external service
    """Wrapper around the OpenAI client."""

    def __init__(self, model: str, client: Any | None = None) -> None:
        self.model = model
        if client is not None:
            self._client = client
        else:
            if openai is None:
                raise RuntimeError("openai package is not available")
            self._client = openai.AsyncOpenAI()

    async def generate(
        self, *, system: str, prompt: str, temperature: float, max_tokens: Optional[int]
    ) -> str:
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""


async def gather_with_concurrency(
    n: int, coroutines: Iterable[asyncio.Future[str] | asyncio.Task[str] | Any]
) -> List[str]:
    """Run coroutines with limited concurrency."""

    semaphore = asyncio.Semaphore(n)
    results: List[str] = []

    async def run(coro: Any) -> str:
        async with semaphore:
            return await coro

    for coro in asyncio.as_completed([run(c) for c in coroutines]):
        results.append(await coro)
    return results
