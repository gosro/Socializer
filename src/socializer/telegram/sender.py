from __future__ import annotations
from typing import Awaitable, Callable
from telethon.errors import FloodWaitError
from socializer.config import TimingSettings
from socializer.safety.human_timing import read_delay, typing_seconds


class SendBlocked(Exception):
    def __init__(self, seconds: int):
        super().__init__(f"FloodWait {seconds}s")
        self.seconds = seconds


async def send_human(client, chat_id: int, text: str, timing: TimingSettings, *,
                     sleeper: Callable[[float], Awaitable[None]],
                     rng: Callable[[], float]) -> None:
    await sleeper(read_delay(timing, rng()))
    try:
        async with client.action(chat_id, "typing"):
            await sleeper(typing_seconds(text, timing))
            await client.send_message(chat_id, text)
    except FloodWaitError as e:
        raise SendBlocked(seconds=e.seconds)
