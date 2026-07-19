from __future__ import annotations
from typing import Awaitable, Callable
from socializer.approval.queue import ApprovalQueue
from socializer.telegram.sender import send_human, SendBlocked

_SEND = {"send", "reply"}
_SKIP = {"skip", "ignore"}
_EDIT = {"edit", "own"}


class DecisionHandler:
    def __init__(self, *, queue: ApprovalQueue, client, settings, rate,
                 sleeper: Callable[[float], Awaitable[None]],
                 rng: Callable[[], float], now: Callable[[], tuple], install_iso: str):
        self.queue = queue
        self.client = client
        self.settings = settings
        self.rate = rate
        self.sleeper = sleeper
        self.rng = rng
        self.now = now
        self.install_iso = install_iso

    async def apply(self, decision: str, request_id: str) -> str:
        req = self.queue.get(request_id)
        if req is None:
            return "noop"
        if decision in _EDIT:
            return "await_text"          # bot will collect replacement text (manual path in MVP)
        self.queue.resolve(request_id)
        if decision in _SKIP:
            return "skipped"
        if decision in _SEND:
            today, epoch, _hour, _ts, _rh = self.now()
            try:
                await send_human(self.client, req.chat_id, req.candidate,
                                 self.settings.timing, sleeper=self.sleeper, rng=self.rng)
            except SendBlocked as e:
                self.rate.set_cooldown(epoch + e.seconds)
                return "rate_limited"
            self.rate.record_message(req.contact_slug, False, today)
            return "sent"
        return "noop"
