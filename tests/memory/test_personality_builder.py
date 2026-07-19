from socializer.memory.personality_builder import build_personality_prompt, generate_personality
from socializer.memory.personality import read_personality
from socializer.llm.base import LLMProvider


def test_prompt_includes_samples_and_asks_for_markdown():
    prompt = build_personality_prompt(["оо привет)", "го завтра"])
    assert "оо привет)" in prompt
    assert "го завтра" in prompt
    assert "personality" in prompt.lower() or "стиль" in prompt.lower()


class _FakeProvider(LLMProvider):
    def __init__(self):
        self.calls = []
    async def complete(self, system, messages):
        self.calls.append((system, messages))
        return "# Мой стиль\nкороткие фразы, эмодзи 😄"


async def test_generate_writes_and_returns(tmp_path):
    prov = _FakeProvider()
    out = await generate_personality(prov, ["привет", "как ты"], str(tmp_path))
    assert "Мой стиль" in out
    assert read_personality(str(tmp_path)) == out       # persisted
    assert len(prov.calls) == 1
