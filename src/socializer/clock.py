from __future__ import annotations
from datetime import datetime
import os
import secrets


def real_now() -> tuple[str, int, int, str, str]:
    dt = datetime.now()
    return (dt.date().isoformat(), int(dt.timestamp()), dt.hour,
            dt.isoformat(timespec="seconds"), secrets.token_hex(3))


def install_date(data_dir: str) -> str:
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "INSTALLED")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    today = datetime.now().date().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        f.write(today)
    return today
