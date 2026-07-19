from socializer.contacts import Contact
from socializer.brain.memory_updater import build_update_prompt, update_memory
from socializer.memory.conversation_memory import read_memory, write_memory
from socializer.llm.base import LLMProvider


def _c():
    return Contact(telegram="@masha", name="Маша", mode="draft",
                   relationship="romantic", tone="тёплый", goal="встреча")


def test_update_prompt_includes_existing_and_date():
    p = build_update_prompt("любит кофе", [("them", "сдала защиту")], "2026-07-19")
    assert "любит кофе" in p
    assert "2026-07-19" in p


class _Prov(LLMProvider):
    async def complete(self, system, messages):
        return "# Маша\nлюбит кофе\nсдала защиту 2026-07-19"


async def test_update_memory_writes(tmp_path):
    write_memory(str(tmp_path), _c(), "любит кофе")
    out = await update_memory(_Prov(), str(tmp_path), _c(),
                              [("them", "сдала защиту")], "2026-07-19")
    assert "сдала защиту" in out
    assert read_memory(str(tmp_path), _c()) == out
