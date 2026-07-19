import pytest
import socializer.llm.openai_compatible as mod
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings


def _settings():
    return Settings(
        llm=LLMSettings("openai_compatible", "https://openrouter.ai/api/v1", "deepseek/deepseek-chat", "sk-x"),
        limits=LimitSettings(40, 15, 3, 7),
        timing=TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8),
        data_dir="data", telegram_api_id=1, telegram_api_hash="h",
        control_bot_token="t", owner_user_id=1,
    )


async def test_complete_sends_system_plus_messages_and_returns_content(monkeypatch):
    captured = {}

    class FakeMsg:
        content = "готовый ответ"
    class FakeChoice:
        message = FakeMsg()
    class FakeResp:
        choices = [FakeChoice()]

    class FakeCompletions:
        async def create(self, model, messages):
            captured["model"] = model
            captured["messages"] = messages
            return FakeResp()
    class FakeChat:
        completions = FakeCompletions()
    class FakeClient:
        def __init__(self, base_url, api_key):
            captured["base_url"] = base_url
            captured["api_key"] = api_key
            self.chat = FakeChat()

    monkeypatch.setattr(mod, "AsyncOpenAI", FakeClient)

    prov = mod.OpenAICompatibleProvider(_settings())
    out = await prov.complete("ты — это я", [{"role": "user", "content": "привет"}])

    assert out == "готовый ответ"
    assert captured["base_url"] == "https://openrouter.ai/api/v1"
    assert captured["api_key"] == "sk-x"
    assert captured["model"] == "deepseek/deepseek-chat"
    assert captured["messages"][0] == {"role": "system", "content": "ты — это я"}
    assert captured["messages"][1] == {"role": "user", "content": "привет"}
