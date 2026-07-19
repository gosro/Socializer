from __future__ import annotations
from dataclasses import dataclass
from typing import Awaitable, Callable
from telethon import events
from socializer.contacts import Contact, ContactBook


@dataclass(frozen=True)
class IncomingMessage:
    contact: Contact
    text: str
    chat_id: int


def resolve_incoming(book: ContactBook, sender_id: int, username: str | None,
                     text: str, chat_id: int) -> IncomingMessage | None:
    contact = book.match(sender_id, username)
    if contact is None:
        return None
    return IncomingMessage(contact=contact, text=text, chat_id=chat_id)


def register_listener(client, book: ContactBook,
                      on_message: Callable[[IncomingMessage], Awaitable[None]]) -> None:
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def _handler(event):
        sender = await event.get_sender()
        username = getattr(sender, "username", None)
        msg = resolve_incoming(book, event.sender_id, username,
                               event.raw_text, event.chat_id)
        if msg is not None:
            await on_message(msg)
