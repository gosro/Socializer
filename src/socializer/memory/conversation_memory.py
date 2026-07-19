from __future__ import annotations
import os
from socializer.contacts import Contact, slug


def memory_path(data_dir: str, contact: Contact) -> str:
    return os.path.join(data_dir, "memory", f"{slug(contact)}.md")


def read_memory(data_dir: str, contact: Contact) -> str:
    path = memory_path(data_dir, contact)
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_memory(data_dir: str, contact: Contact, content: str) -> None:
    path = memory_path(data_dir, contact)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
