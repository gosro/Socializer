import socializer.telegram.client as mod
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings


def _settings(tmp_path):
    return Settings(
        llm=LLMSettings("openai_compatible", "u", "m", "k"),
        limits=LimitSettings(40, 15, 3, 7),
        timing=TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8),
        data_dir=str(tmp_path),
        telegram_api_id=123,
        telegram_api_hash="hash",
        control_bot_token="t",
        owner_user_id=9,
    )


def test_build_user_client_uses_session_path_and_creds(tmp_path, monkeypatch):
    captured = {}

    class FakeClient:
        def __init__(self, session, api_id, api_hash):
            captured["session"] = session
            captured["api_id"] = api_id
            captured["api_hash"] = api_hash

    monkeypatch.setattr(mod, "TelegramClient", FakeClient)
    client = mod.build_user_client(_settings(tmp_path))
    assert isinstance(client, FakeClient)
    assert captured["session"].endswith("user_session")
    assert captured["api_id"] == 123
    assert captured["api_hash"] == "hash"
