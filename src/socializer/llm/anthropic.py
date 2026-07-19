from __future__ import annotations
from anthropic import AsyncAnthropic
from socializer.config import Settings
from socializer.llm.base import LLMProvider, Message, register_provider


class AnthropicProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self._model = settings.llm.model
        self._client = AsyncAnthropic(api_key=settings.llm.api_key)

    async def complete(self, system: str, messages: list[Message]) -> str:
        resp = await self._client.messages.create(
            model=self._model, system=system, messages=messages, max_tokens=1024,
        )
        return resp.content[0].text


register_provider("anthropic", AnthropicProvider)
