from __future__ import annotations
from typing import Awaitable, Callable
from socializer.contacts import slug
from socializer.telegram.listener import IncomingMessage
from socializer.brain.responder import generate_reply
from socializer.brain.safety_gate import classify_incoming, mentions_unknown_fact
from socializer.approval.queue import ApprovalQueue, new_request, DRAFT, MISSING_FACT
from socializer.telegram.sender import send_human, SendBlocked

_MAX_RECENT = 10


class Orchestrator:
    def __init__(self, *, provider, data_dir, settings, rate, kill, control_bot,
                 queue: ApprovalQueue, client,
                 sleeper: Callable[[float], Awaitable[None]],
                 rng: Callable[[], float],
                 now: Callable[[], tuple], install_iso: str):
        self.provider = provider
        self.data_dir = data_dir
        self.settings = settings
        self.rate = rate
        self.kill = kill
        self.control_bot = control_bot
        self.queue = queue
        self.client = client
        self.sleeper = sleeper
        self.rng = rng
        self.now = now
        self.install_iso = install_iso
        self.recent: dict[int, list[tuple[str, str]]] = {}

    def _push(self, chat_id: int, role: str, text: str) -> None:
        buf = self.recent.setdefault(chat_id, [])
        buf.append((role, text))
        del buf[:-_MAX_RECENT]

    async def _enqueue(self, kind, contact, chat_id, context, candidate, ts, rh):
        req = new_request(kind, slug(contact), chat_id, context, candidate, ts, rh)
        await self.control_bot.notify(req)

    async def handle(self, msg: IncomingMessage) -> str:
        today, epoch, hour, ts, rh = self.now()
        self._push(msg.chat_id, "them", msg.text)

        if self.kill.is_engaged():
            return "killed"
        if self.kill.is_paused():
            return "paused"

        gate = classify_incoming(msg.text)
        if gate.needs_approval:
            await self._enqueue(gate.kind, msg.contact, msg.chat_id, msg.text, "", ts, rh)
            return f"approval:{gate.kind}"

        reply = await generate_reply(self.provider, self.data_dir, msg.contact,
                                     self.recent[msg.chat_id])
        if mentions_unknown_fact(reply):
            await self._enqueue(MISSING_FACT, msg.contact, msg.chat_id, msg.text, reply, ts, rh)
            return "approval:missing_fact"

        if not self.rate.allow_message(slug(msg.contact), False, today, self.install_iso):
            return "rate_limited"

        if msg.contact.mode == "draft":
            await self._enqueue(DRAFT, msg.contact, msg.chat_id, msg.text, reply, ts, rh)
            return "draft"

        try:
            await send_human(self.client, msg.chat_id, reply, self.settings.timing,
                             sleeper=self.sleeper, rng=self.rng)
        except SendBlocked as e:
            self.rate.set_cooldown(epoch + e.seconds)
            return "rate_limited"
        self.rate.record_message(slug(msg.contact), False, today)
        self._push(msg.chat_id, "me", reply)
        return "sent"
