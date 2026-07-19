from socializer.contacts import Contact
from socializer.brain.responder import generate_reply
from socializer.llm.base import LLMProvider
from socializer.memory.personality import write_personality
from socializer.memory.conversation_memory import write_memory


class _CapProvider(LLMProvider):
    def __init__(self): self.system = None; self.messages = None
    async def complete(self, system, messages):
        self.system = system; self.messages = messages
        return "  оо привет) как сама  "


def _c():
    return Contact(telegram="@masha", name="Маша", mode="draft",
                   relationship="romantic", tone="тёплый", goal="встреча")


async def test_generate_reply_uses_files_and_strips(tmp_path):
    write_personality(str(tmp_path), "коротко, эмодзи 😄")
    write_memory(str(tmp_path), _c(), "любит кофе")
    prov = _CapProvider()
    out = await generate_reply(prov, str(tmp_path), _c(),
                               recent=[("them", "привет")])
    assert out == "оо привет) как сама"                 # stripped
    assert "коротко" in prov.system                     # personality reached prompt
    assert "любит кофе" in prov.system                  # memory reached prompt
    assert prov.messages[-1]["content"] == "привет"     # last interlocutor turn
