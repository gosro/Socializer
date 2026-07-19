from socializer.contacts import Contact, ContactBook, slug
from socializer.brain.initiator import is_stale, due_contacts, generate_reengagement
from socializer.llm.base import LLMProvider


def _c(name="@masha", days=3, mode="auto"):
    return Contact(telegram=name, name=name.strip("@"), mode=mode,
                   relationship="friend", tone="тёплый", goal="не терять контакт",
                   reengage_after_days=days)


def test_is_stale_rules():
    assert is_stale(5, _c(days=3)) is True
    assert is_stale(2, _c(days=3)) is False
    assert is_stale(None, _c(days=3)) is False        # never messaged -> not a re-engage target
    assert is_stale(100, _c(days=0)) is False          # disabled (0)


def test_due_contacts_filters():
    book = ContactBook([_c("@a", 3), _c("@b", 7), _c("@c", 0)])
    last = {"a": 5, "b": 2, "c": 999}
    due = due_contacts(book, last)
    assert [x.name for x in due] == ["a"]              # a stale; b not yet; c disabled


class _Prov(LLMProvider):
    async def complete(self, system, messages):
        return "  оо привет) сто лет не общались, как ты?  "


async def test_generate_reengagement_strips(tmp_path):
    out = await generate_reengagement(_Prov(), str(tmp_path), _c())
    assert out == "оо привет) сто лет не общались, как ты?"
