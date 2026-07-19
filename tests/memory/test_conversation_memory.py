from socializer.contacts import Contact
from socializer.memory.conversation_memory import read_memory, write_memory


def _c():
    return Contact(telegram="@masha", name="Маша", mode="auto",
                   relationship="romantic", tone="тёплый", goal="встреча")


def test_read_missing_returns_empty(tmp_path):
    assert read_memory(str(tmp_path), _c()) == ""


def test_write_then_read(tmp_path):
    write_memory(str(tmp_path), _c(), "# Маша\nлюбит кофе")
    assert read_memory(str(tmp_path), _c()) == "# Маша\nлюбит кофе"
