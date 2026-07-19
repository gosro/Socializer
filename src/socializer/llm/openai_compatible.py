from __future__ import annotations
from openai import AsyncOpenAI
from socializer.config import Settings
from socializer.llm.base import LLMProvider, Message, register_provider


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, settings: Settings):
        self._model = settings.llm.model
        self._client = AsyncOpenAI(
            base_url=settings.llm.base_url,
            api_key=settings.llm.api_key,
        )

    async def complete(self, system: str, messages: list[Message]) -> str:
        full = [{"role": "system", "content": system}, *messages]
        resp = await self._client.chat.completions.create(
            model=self._model, messages=full,
        )
        return resp.choices[0].message.content


register_provider("openai_compatible", OpenAICompatibleProvider)
