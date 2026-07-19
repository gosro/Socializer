from __future__ import annotations
from typing import Awaitable, Callable
from socializer.contacts import ContactBook, slug
from socializer.brain.initiator import due_contacts, generate_reengagement
from socializer.approval.queue import ApprovalQueue, new_request, DRAFT
from socializer.telegram.sender import send_human, SendBlocked
from socializer.safety.human_timing import is_night


class ProactiveRunner:
    def __init__(self, *, provider, data_dir, settings, rate, kill, control_bot,
                 queue: ApprovalQueue, client, book: ContactBook,
                 sleeper: Callable[[float], Awaitable[None]],
                 rng: Callable[[], float], now: Callable[[], tuple],
                 install_iso: str, chat_id_for: Callable):
        self.provider = provider
        self.data_dir = data_dir
        self.settings = settings
        self.rate = rate
        self.kill = kill
        self.control_bot = control_bot
        self.queue = queue
        self.client = client
        self.book = book
        self.sleeper = sleeper
        self.rng = rng
        self.now = now
        self.install_iso = install_iso
        self.chat_id_for = chat_id_for

    async def run_once(self, last_days_by_slug: dict) -> list[str]:
        today, epoch, hour, ts, rh = self.now()
        results: list[str] = []
        for contact in due_contacts(self.book, last_days_by_slug):
            if self.kill.is_engaged():
                results.append("killed"); continue
            if self.kill.is_paused():
                results.append("paused"); continue
            if is_night(hour, self.settings.timing):
                results.append("night"); continue
            if not self.rate.allow_message(slug(contact), False, today, self.install_iso):
                results.append("rate_limited"); continue

            text = await generate_reengagement(self.provider, self.data_dir, contact)
            chat_id = self.chat_id_for(contact)

            if contact.mode == "draft":
                req = new_request(DRAFT, slug(contact), chat_id,
                                  "проактив: возобновить диалог", text, ts, rh)
                await self.control_bot.notify(req)
                results.append(f"draft:{slug(contact)}")
                continue

            try:
                await send_human(self.client, chat_id, text, self.settings.timing,
                                 sleeper=self.sleeper, rng=self.rng)
            except SendBlocked as e:
                self.rate.set_cooldown(epoch + e.seconds)
                results.append("rate_limited"); continue
            self.rate.record_message(slug(contact), False, today)
            results.append(f"sent:{slug(contact)}")
        return results
