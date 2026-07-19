import socializer.llm.anthropic as mod
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings


def _settings():
    return Settings(
        llm=LLMSettings("anthropic", "", "claude-sonnet-5", "sk-ant"),
        limits=LimitSettings(40, 15, 3, 7),
        timing=TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8),
        data_dir="data", telegram_api_id=1, telegram_api_hash="h",
        control_bot_token="t", owner_user_id=1,
    )


async def test_complete_uses_system_param_and_returns_text(monkeypatch):
    captured = {}

    class FakeBlock:
        text = "ответ"
    class FakeResp:
        content = [FakeBlock()]
    class FakeMessages:
        async def create(self, model, system, messages, max_tokens):
            captured.update(model=model, system=system, messages=messages, max_tokens=max_tokens)
            return FakeResp()
    class FakeClient:
        def __init__(self, api_key):
            captured["api_key"] = api_key
            self.messages = FakeMessages()

    monkeypatch.setattr(mod, "AsyncAnthropic", FakeClient)

    prov = mod.AnthropicProvider(_settings())
    out = await prov.complete("системная роль", [{"role": "user", "content": "привет"}])

    assert out == "ответ"
    assert captured["api_key"] == "sk-ant"
    assert captured["system"] == "системная роль"
    assert captured["messages"] == [{"role": "user", "content": "привет"}]
    assert captured["max_tokens"] == 1024
