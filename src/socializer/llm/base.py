from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable
from socializer.config import Settings

Message = dict  # {"role": str, "content": str}


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system: str, messages: list[Message]) -> str:
        ...


_REGISTRY: dict[str, Callable[[Settings], LLMProvider]] = {}


def register_provider(name: str, factory: Callable[[Settings], LLMProvider]) -> None:
    _REGISTRY[name] = factory


def build_provider(settings: Settings) -> LLMProvider:
    # Import adapters so they self-register (import side effect).
    from socializer.llm import openai_compatible as _oc  # noqa: F401
    from socializer.llm import anthropic as _an  # noqa: F401
    name = settings.llm.provider
    if name not in _REGISTRY:
        raise ValueError(f"Unknown LLM provider: {name!r}. Registered: {list(_REGISTRY)}")
    return _REGISTRY[name](settings)
