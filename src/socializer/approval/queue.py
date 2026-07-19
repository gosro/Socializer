from __future__ import annotations
from dataclasses import dataclass, asdict
import json
import os

INVITATION = "invitation"
SENSITIVE = "sensitive"
MISSING_FACT = "missing_fact"
SUSPECTED_BOT = "suspected_bot"
DRAFT = "draft"


@dataclass(frozen=True)
class ApprovalRequest:
    id: str
    kind: str
    contact_slug: str
    chat_id: int
    context: str
    candidate: str
    created_iso: str


def new_request(kind: str, contact_slug: str, chat_id: int, context: str,
                candidate: str, now_iso: str, rand_hex: str) -> ApprovalRequest:
    return ApprovalRequest(
        id=f"{now_iso.replace(':', '').replace('-', '')}_{rand_hex}",
        kind=kind, contact_slug=contact_slug, chat_id=chat_id,
        context=context, candidate=candidate, created_iso=now_iso,
    )


class ApprovalQueue:
    def __init__(self, data_dir: str):
        self._path = os.path.join(data_dir, "approvals.json")
        os.makedirs(data_dir, exist_ok=True)

    def _load(self) -> list[dict]:
        if not os.path.exists(self._path):
            return []
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, rows: list[dict]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)

    def add(self, request: ApprovalRequest) -> None:
        rows = self._load()
        rows.append(asdict(request))
        self._save(rows)

    def get(self, id: str) -> ApprovalRequest | None:
        for row in self._load():
            if row["id"] == id:
                return ApprovalRequest(**row)
        return None

    def pending(self) -> list[ApprovalRequest]:
        return [ApprovalRequest(**row) for row in self._load()]

    def resolve(self, id: str) -> ApprovalRequest | None:
        rows = self._load()
        kept, found = [], None
        for row in rows:
            if row["id"] == id and found is None:
                found = ApprovalRequest(**row)
            else:
                kept.append(row)
        if found is not None:
            self._save(kept)
        return found
