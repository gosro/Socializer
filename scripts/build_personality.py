from __future__ import annotations
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from socializer.config import load_settings
from socializer.telegram.client import build_user_client
from socializer.llm.base import build_provider
from socializer.memory.personality_builder import generate_personality
from socializer.memory.personality import personality_path

SAMPLES_PER_CHAT = 200


def parse_selection(raw: str, count: int) -> list[int]:
    out: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part.isdigit():
            continue
        idx = int(part) - 1
        if 0 <= idx < count and idx not in out:
            out.append(idx)
    return out


async def collect_own_messages(client, chat, limit: int) -> list[str]:
    texts: list[str] = []
    async for msg in client.iter_messages(chat, from_user="me"):
        text = getattr(msg, "text", None)
        if text:
            texts.append(text)
        if len(texts) >= limit:
            break
    return texts


async def main() -> None:
    settings = load_settings()
    client = build_user_client(settings)
    await client.start()

    dialogs = []
    print("\nТвои диалоги:")
    async for dialog in client.iter_dialogs():
        if not dialog.is_user:
            continue
        dialogs.append(dialog)
        print(f"  [{len(dialogs)}] {dialog.name}")

    raw = input("\nИз каких чатов взять твой стиль? (номера через запятую): ")
    picked = parse_selection(raw, len(dialogs))
    if not picked:
        print("Ничего не выбрано. Выход.")
        return

    samples: list[str] = []
    for i in picked:
        samples.extend(await collect_own_messages(client, dialogs[i].entity, SAMPLES_PER_CHAT))
    print(f"Собрано {len(samples)} твоих сообщений. Генерирую personality.md ...")

    provider = build_provider(settings)
    await generate_personality(provider, samples, settings.data_dir)
    print(f"Готово: {personality_path(settings.data_dir)}")


if __name__ == "__main__":
    asyncio.run(main())
