import pytest
from socializer.config import load_settings, ConfigError


def _write(tmp_path, env_body, yaml_body):
    env = tmp_path / ".env"
    env.write_text(env_body)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml_body)
    return str(cfg), str(env)


VALID_YAML = """
llm:
  provider: openai_compatible
  base_url: "https://openrouter.ai/api/v1"
  model: "deepseek/deepseek-chat"
  api_key_env: OPENROUTER_API_KEY
limits:
  max_messages_per_day: 40
  max_per_contact_per_day: 15
  max_new_contacts_per_day: 3
  warmup_days: 7
timing:
  min_read_delay_seconds: 30
  max_read_delay_seconds: 900
  typing_seconds_per_10_chars: 1.0
  long_delay_probability: 0.10
  long_delay_min_seconds: 3600
  long_delay_max_seconds: 10800
  night_start_hour: 0
  night_end_hour: 8
paths:
  data_dir: "data"
"""

VALID_ENV = """
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=abchash
CONTROL_BOT_TOKEN=bottoken
OWNER_USER_ID=999
OPENROUTER_API_KEY=sk-or-xxx
"""


def test_loads_valid_settings(tmp_path):
    cfg, env = _write(tmp_path, VALID_ENV, VALID_YAML)
    s = load_settings(cfg, env)
    assert s.telegram_api_id == 12345
    assert s.owner_user_id == 999
    assert s.llm.model == "deepseek/deepseek-chat"
    assert s.llm.api_key == "sk-or-xxx"
    assert s.limits.max_messages_per_day == 40
    assert s.timing.night_end_hour == 8
    assert s.data_dir == "data"


def test_missing_secret_raises_with_name(tmp_path):
    broken_env = "TELEGRAM_API_ID=1\n"  # everything else missing
    cfg, env = _write(tmp_path, broken_env, VALID_YAML)
    with pytest.raises(ConfigError) as exc:
        load_settings(cfg, env)
    msg = str(exc.value)
    assert "TELEGRAM_API_HASH" in msg
    assert "OWNER_USER_ID" in msg
    assert "OPENROUTER_API_KEY" in msg
