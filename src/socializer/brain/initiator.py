from __future__ import annotations
from socializer.contacts import Contact, ContactBook, slug
from socializer.llm.base import LLMProvider
from socializer.brain.context_builder import build_system_prompt
from socializer.memory.personality import read_personality
from socializer.memory.conversation_memory import read_memory

_REENGAGE_INSTRUCTION = (
    "Напиши собеседнику ПЕРВЫМ, чтобы возобновить общение. Коротко и естественно, "
    "в своём стиле. Если в памяти есть незакрытая тема или повод — обопрись на неё. "
    "Не извиняйся формально, не пиши длинно. Одно сообщение.")


def is_stale(last_msg_days: int | None, contact: Contact) -> bool:
    if contact.reengage_after_days <= 0:
        return False
    if last_msg_days is None:
        return False
    return last_msg_days >= contact.reengage_after_days


def due_contacts(book: ContactBook, last_days_by_slug: dict[str, int | None]) -> list[Contact]:
    out = []
    for c in book.all():
        if is_stale(last_days_by_slug.get(slug(c)), c):
            out.append(c)
    return out


async def generate_reengagement(provider: LLMProvider, data_dir: str,
                                contact: Contact) -> str:
    personality = read_personality(data_dir)
    memory = read_memory(data_dir, contact)
    system = build_system_prompt(personality, contact, memory)
    result = await provider.complete(
        system, [{"role": "user", "content": _REENGAGE_INSTRUCTION}])
    return result.strip()
