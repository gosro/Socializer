from __future__ import annotations
import os

_FALLBACK = "Пиши коротко, дружелюбно, неформально."


def personality_path(data_dir: str) -> str:
    return os.path.join(data_dir, "personality.md")


def read_personality(data_dir: str) -> str:
    path = personality_path(data_dir)
    if not os.path.exists(path):
        return _FALLBACK
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_personality(data_dir: str, content: str) -> None:
    os.makedirs(data_dir, exist_ok=True)
    with open(personality_path(data_dir), "w", encoding="utf-8") as f:
        f.write(content)
