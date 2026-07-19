from __future__ import annotations
import os
from typing import Awaitable, Callable
from telethon import TelegramClient, events, Button
from socializer.config import Settings
from socializer.approval.queue import ApprovalQueue, ApprovalRequest
from socializer.control_bot.approvals import render_request, buttons_for, parse_callback
from socializer.control_bot.commands import handle_command
from socializer.safety.kill_switch import KillSwitch


def build_bot_client(settings: Settings) -> TelegramClient:
    session_path = os.path.join(settings.data_dir, "bot_session")
    return TelegramClient(session_path, settings.telegram_api_id, settings.telegram_api_hash)


def to_inline(rows):
    return [[Button.inline(label, data) for (label, data) in row] for row in rows]


class ControlBot:
    def __init__(self, client, queue: ApprovalQueue | None, kill: KillSwitch | None,
                 owner_id: int, on_decision: Callable[[str, str], Awaitable[None]],
                 status_provider: Callable[[], str] = lambda: "ok"):
        self.client = client
        self.queue = queue
        self.kill = kill
        self.owner_id = owner_id
        self.on_decision = on_decision
        self.status_provider = status_provider

    async def notify(self, req: ApprovalRequest) -> None:
        self.queue.add(req)
        await self.client.send_message(
            self.owner_id, render_request(req), buttons=to_inline(buttons_for(req)))

    async def _on_callback(self, event) -> None:
        if event.sender_id != self.owner_id:
            return
        decision, rid = parse_callback(event.data)
        await event.answer()
        await event.edit(f"Принято: {decision}")
        await self.on_decision(decision, rid)

    async def _on_command(self, event) -> None:
        reply = handle_command(event.raw_text, event.sender_id, self.owner_id,
                               self.kill, self.status_provider)
        if reply is not None:
            await event.respond(reply)

    def register(self) -> None:
        self.client.add_event_handler(
            self._on_command, events.NewMessage(pattern=r"^/"))
        self.client.add_event_handler(
            self._on_callback, events.CallbackQuery())
