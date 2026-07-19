from __future__ import annotations
from socializer.config import TimingSettings


def is_night(hour: int, timing: TimingSettings) -> bool:
    return timing.night_start_hour <= hour < timing.night_end_hour


def seconds_until_morning(hour: int, timing: TimingSettings) -> int:
    hours_left = timing.night_end_hour - hour
    if hours_left <= 0:
        hours_left += 24
    return hours_left * 3600


def read_delay(timing: TimingSettings, rand: float) -> int:
    span = timing.max_read_delay_seconds - timing.min_read_delay_seconds
    return int(timing.min_read_delay_seconds + rand * span)


def typing_seconds(text: str, timing: TimingSettings) -> float:
    return len(text) / 10.0 * timing.typing_seconds_per_10_chars


def maybe_long_delay(timing: TimingSettings, roll: float, rand: float) -> int:
    if roll < timing.long_delay_probability:
        span = timing.long_delay_max_seconds - timing.long_delay_min_seconds
        return int(timing.long_delay_min_seconds + rand * span)
    return 0
