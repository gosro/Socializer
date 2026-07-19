from __future__ import annotations
import os
from telethon import TelegramClient
from socializer.config import Settings


def build_user_client(settings: Settings) -> TelegramClient:
    session_path = os.path.join(settings.data_dir, "user_session")
    return TelegramClient(session_path, settings.telegram_api_id, settings.telegram_api_hash)
