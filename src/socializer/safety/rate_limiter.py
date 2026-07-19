from __future__ import annotations
from datetime import date
import json
import os
from socializer.config import LimitSettings


def days_between(a_iso: str, b_iso: str) -> int:
    a = date.fromisoformat(a_iso)
    b = date.fromisoformat(b_iso)
    return abs((b - a).days)


class RateLimiter:
    def __init__(self, data_dir: str, limits: LimitSettings, install_iso: str):
        os.makedirs(data_dir, exist_ok=True)
        self._path = os.path.join(data_dir, "rate_state.json")
        self._limits = limits
        self._install = install_iso

    def _load(self) -> dict:
        if not os.path.exists(self._path):
            return {"day": "", "total": 0, "new": 0, "per_contact": {}, "cooldown": 0}
        with open(self._path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, state: dict) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def _rollover(self, state: dict, today: str) -> dict:
        if state.get("day") != today:
            cooldown = state.get("cooldown", 0)
            state = {"day": today, "total": 0, "new": 0, "per_contact": {}, "cooldown": cooldown}
        return state

    def _caps(self, today: str, install_date: str) -> tuple[int, int, int]:
        total = self._limits.max_messages_per_day
        per = self._limits.max_per_contact_per_day
        new = self._limits.max_new_contacts_per_day
        if days_between(install_date, today) < self._limits.warmup_days:
            total, per, new = total // 2, per // 2, new // 2
        return total, per, new

    def allow_message(self, contact_slug: str, is_new_contact: bool,
                      today: str, install_date: str) -> bool:
        state = self._rollover(self._load(), today)
        self._save(state)
        total_cap, per_cap, new_cap = self._caps(today, install_date)
        if state["total"] >= total_cap:
            return False
        if state["per_contact"].get(contact_slug, 0) >= per_cap:
            return False
        if is_new_contact and state["new"] >= new_cap:
            return False
        return True

    def record_message(self, contact_slug: str, is_new_contact: bool, today: str) -> None:
        state = self._rollover(self._load(), today)
        state["total"] += 1
        state["per_contact"][contact_slug] = state["per_contact"].get(contact_slug, 0) + 1
        if is_new_contact:
            state["new"] += 1
        self._save(state)

    def set_cooldown(self, until_epoch: int) -> None:
        state = self._load()
        state["cooldown"] = until_epoch
        self._save(state)

    def in_cooldown(self, now_epoch: int) -> bool:
        return now_epoch < self._load().get("cooldown", 0)
