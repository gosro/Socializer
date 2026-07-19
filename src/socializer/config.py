from __future__ import annotations
from dataclasses import dataclass
import os
import yaml
from dotenv import dotenv_values


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    base_url: str
    model: str
    api_key: str


@dataclass(frozen=True)
class LimitSettings:
    max_messages_per_day: int
    max_per_contact_per_day: int
    max_new_contacts_per_day: int
    warmup_days: int


@dataclass(frozen=True)
class TimingSettings:
    min_read_delay_seconds: int
    max_read_delay_seconds: int
    typing_seconds_per_10_chars: float
    long_delay_probability: float
    long_delay_min_seconds: int
    long_delay_max_seconds: int
    night_start_hour: int
    night_end_hour: int


@dataclass(frozen=True)
class Settings:
    llm: LLMSettings
    limits: LimitSettings
    timing: TimingSettings
    data_dir: str
    telegram_api_id: int
    telegram_api_hash: str
    control_bot_token: str
    owner_user_id: int


def _require(env: dict, name: str, missing: list) -> str:
    val = env.get(name)
    if not val:
        missing.append(name)
        return ""
    return val


def load_settings(config_path: str = "config.yaml", env_path: str = ".env") -> Settings:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Secrets: if a .env file exists it is authoritative (deterministic validation —
    # a key absent from the file counts as missing even if ambient in the process).
    # With no .env file, fall back to the process environment (exported-env deployments).
    if os.path.exists(env_path):
        env = {k: v for k, v in dotenv_values(env_path).items() if v is not None}
    else:
        env = dict(os.environ)

    missing: list[str] = []
    api_id = _require(env, "TELEGRAM_API_ID", missing)
    api_hash = _require(env, "TELEGRAM_API_HASH", missing)
    bot_token = _require(env, "CONTROL_BOT_TOKEN", missing)
    owner = _require(env, "OWNER_USER_ID", missing)

    llm_cfg = cfg["llm"]
    api_key = _require(env, llm_cfg["api_key_env"], missing)

    if missing:
        raise ConfigError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        llm=LLMSettings(
            provider=llm_cfg["provider"],
            base_url=llm_cfg["base_url"],
            model=llm_cfg["model"],
            api_key=api_key,
        ),
        limits=LimitSettings(**cfg["limits"]),
        timing=TimingSettings(**cfg["timing"]),
        data_dir=cfg["paths"]["data_dir"],
        telegram_api_id=int(api_id),
        telegram_api_hash=api_hash,
        control_bot_token=bot_token,
        owner_user_id=int(owner),
    )
