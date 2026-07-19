from socializer.contacts import ContactBook, Contact
from socializer.telegram.listener import resolve_incoming, IncomingMessage


def _book():
    return ContactBook([Contact(telegram="@masha", name="Маша", mode="auto",
                                relationship="romantic", tone="тёплый", goal="встреча")])


def test_resolve_returns_message_for_whitelisted():
    msg = resolve_incoming(_book(), sender_id=111, username="masha", text="привет", chat_id=111)
    assert isinstance(msg, IncomingMessage)
    assert msg.contact.name == "Маша"
    assert msg.text == "привет"
    assert msg.chat_id == 111


def test_resolve_returns_none_for_stranger():
    assert resolve_incoming(_book(), sender_id=222, username="bob", text="hi", chat_id=222) is None
