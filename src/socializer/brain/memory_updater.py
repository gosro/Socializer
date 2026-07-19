from __future__ import annotations
from socializer.contacts import Contact
from socializer.llm.base import LLMProvider
from socializer.memory.conversation_memory import read_memory, write_memory

_SYSTEM = "Ты ведёшь краткие заметки о собеседнике. Отвечай только на русском."

_INSTRUCTION = """Обнови краткую сводку о собеседнике (файл памяти). НЕ храни дословную
переписку — только факты, договорённости, о чём говорили (с датой) и какой тон заходит.

Текущая сводка:
<<<
{existing}
>>>

Свежий обмен сообщениями (сегодня {today}):
<<<
{recent}
>>>

Верни ПОЛНУЮ обновлённую сводку в формате:
# <Имя>
## Кто это
## Важное / договорённости
## О чём общались (последнее)
## Тон, который заходит"""


def _fmt_recent(recent: list[tuple[str, str]]) -> str:
    label = {"me": "я", "them": "он/она"}
    return "\n".join(f"{label.get(r, r)}: {t}" for r, t in recent)


def build_update_prompt(existing: str, recent: list[tuple[str, str]], today_iso: str) -> str:
    return _INSTRUCTION.format(existing=existing or "(пусто)",
                               recent=_fmt_recent(recent), today=today_iso)


async def update_memory(provider: LLMProvider, data_dir: str, contact: Contact,
                        recent: list[tuple[str, str]], today_iso: str) -> str:
    existing = read_memory(data_dir, contact)
    prompt = build_update_prompt(existing, recent, today_iso)
    result = await provider.complete(_SYSTEM, [{"role": "user", "content": prompt}])
    write_memory(data_dir, contact, result)
    return result
