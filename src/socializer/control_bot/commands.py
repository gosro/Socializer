from __future__ import annotations
from typing import Callable
from socializer.safety.kill_switch import KillSwitch


def is_owner(sender_id: int, owner_id: int) -> bool:
    return sender_id == owner_id


def handle_command(text: str, sender_id: int, owner_id: int, kill: KillSwitch,
                   status_provider: Callable[[], str]) -> str | None:
    if not is_owner(sender_id, owner_id):
        return None
    cmd = text.strip().split()[0].lower() if text.strip() else ""
    if cmd == "/status":
        return status_provider()
    if cmd == "/kill":
        kill.engage()
        return "🛑 Kill switch включён. Вся отправка остановлена."
    if cmd == "/pause":
        kill.pause()
        return "⏸ Агент на паузе."
    if cmd == "/resume":
        kill.resume()
        return "▶️ Агент снова активен."
    if cmd == "/pending":
        return status_provider()   # status text includes pending count; kept simple
    if cmd == "/contacts":
        return status_provider()
    return "Команды: /status /pause /resume /kill /pending /contacts"
