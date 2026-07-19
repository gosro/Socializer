import pytest
from socializer.llm.base import LLMProvider, build_provider, register_provider
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings


def _settings(provider):
    return Settings(
        llm=LLMSettings(provider, "url", "model", "key"),
        limits=LimitSettings(40, 15, 3, 7),
        timing=TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8),
        data_dir="data", telegram_api_id=1, telegram_api_hash="h",
        control_bot_token="t", owner_user_id=1,
    )


def test_build_unknown_provider_raises():
    with pytest.raises(ValueError):
        build_provider(_settings("nope"))


def test_registered_provider_is_built():
    class Fake(LLMProvider):
        def __init__(self, settings):
            self.settings = settings
        async def complete(self, system, messages):
            return "ok"

    register_provider("fake", Fake)
    prov = build_provider(_settings("fake"))
    assert isinstance(prov, Fake)
    assert prov.settings.llm.model == "model"
