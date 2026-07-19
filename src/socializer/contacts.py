from __future__ import annotations
from dataclasses import dataclass
import re
import yaml


@dataclass(frozen=True)
class Contact:
    telegram: str
    name: str
    mode: str
    relationship: str
    tone: str
    goal: str
    notes: str = ""
    reengage_after_days: int = 0


def slug(contact: Contact) -> str:
    raw = contact.telegram.lstrip("@").lower()
    return re.sub(r"[^a-z0-9]+", "_", raw).strip("_")


def load_contacts(path: str) -> list[Contact]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return [Contact(**item) for item in data.get("contacts", [])]


class ContactBook:
    def __init__(self, contacts: list[Contact]):
        self._contacts = contacts

    def all(self) -> list[Contact]:
        return list(self._contacts)

    def match(self, user_id: int, username: str | None) -> Contact | None:
        uname = (username or "").lstrip("@").lower()
        uid = str(user_id)
        for c in self._contacts:
            target = c.telegram.lstrip("@").lower()
            if target == uid or (uname and target == uname):
                return c
        return None
