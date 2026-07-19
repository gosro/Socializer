from __future__ import annotations
import asyncio
from datetime import date
from socializer.config import load_settings
from socializer.clock import real_now, install_date
from socializer.contacts import load_contacts, ContactBook, slug
from socializer.llm.base import build_provider
from socializer.telegram.client import build_user_client
from socializer.telegram.listener import register_listener
from socializer.control_bot.bot import build_bot_client, ControlBot
from socializer.approval.queue import ApprovalQueue
from socializer.safety.kill_switch import KillSwitch
from socializer.safety.rate_limiter import RateLimiter
from socializer.brain.orchestrator import Orchestrator
from socializer.brain.proactive_runner import ProactiveRunner
from socializer.brain.decision_handler import DecisionHandler

PROACTIVE_INTERVAL_SECONDS = 3 * 3600
CONTACTS_PATH = "data/contacts.yaml"


async def _last_days_by_slug(user_client, book: ContactBook) -> dict:
    out: dict[str, int | None] = {}
    today = date.today()
    for contact in book.all():
        try:
            entity = await user_client.get_entity(contact.telegram)
        except Exception:
            out[slug(contact)] = None
            continue
        last = None
        async for msg in user_client.iter_messages(entity, limit=1):
            last = (today - msg.date.date()).days
        out[slug(contact)] = last
    return out


async def main() -> None:
    settings = load_settings()
    installed = install_date(settings.data_dir)
    provider = build_provider(settings)
    book = ContactBook(load_contacts(CONTACTS_PATH))
    queue = ApprovalQueue(settings.data_dir)
    kill = KillSwitch(settings.data_dir)
    rate = RateLimiter(settings.data_dir, settings.limits, installed)

    user_client = build_user_client(settings)
    bot_client = build_bot_client(settings)

    async def sleeper(s: float) -> None:
        await asyncio.sleep(s)

    import random
    rng = random.random

    orchestrator = Orchestrator(
        provider=provider, data_dir=settings.data_dir, settings=settings,
        rate=rate, kill=kill, control_bot=None, queue=queue, client=user_client,
        sleeper=sleeper, rng=rng, now=real_now, install_iso=installed)

    decision_handler = DecisionHandler(
        queue=queue, client=user_client, settings=settings, rate=rate,
        sleeper=sleeper, rng=rng, now=real_now, install_iso=installed)

    def status() -> str:
        pend = queue.pending()
        return (f"Контактов: {len(book.all())}. Ожидают апрува: {len(pend)}. "
                f"Kill: {kill.is_engaged()}, пауза: {kill.is_paused()}.")

    control = ControlBot(client=bot_client, queue=queue, kill=kill,
                         owner_id=settings.owner_user_id,
                         on_decision=decision_handler.apply, status_provider=status)
    orchestrator.control_bot = control        # wire back-reference
    control.register()

    register_listener(user_client, book, orchestrator.handle)

    proactive = ProactiveRunner(
        provider=provider, data_dir=settings.data_dir, settings=settings,
        rate=rate, kill=kill, control_bot=control, queue=queue, client=user_client,
        book=book, sleeper=sleeper, rng=rng, now=real_now, install_iso=installed,
        chat_id_for=lambda c: c.telegram)

    async def proactive_loop() -> None:
        while True:
            await asyncio.sleep(PROACTIVE_INTERVAL_SECONDS)
            if kill.is_engaged() or kill.is_paused():
                continue
            last = await _last_days_by_slug(user_client, book)
            await proactive.run_once(last)

    await user_client.start()
    await bot_client.start(bot_token=settings.control_bot_token)
    print("Socializer запущен. Управляющий бот активен.")
    asyncio.create_task(proactive_loop())
    await asyncio.gather(
        user_client.run_until_disconnected(),
        bot_client.run_until_disconnected(),
    )


if __name__ == "__main__":
    asyncio.run(main())
