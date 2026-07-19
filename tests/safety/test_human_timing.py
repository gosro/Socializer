from socializer.config import TimingSettings
from socializer.safety.human_timing import (
    is_night, seconds_until_morning, read_delay, typing_seconds, maybe_long_delay)


def _t():
    return TimingSettings(min_read_delay_seconds=30, max_read_delay_seconds=900,
                          typing_seconds_per_10_chars=1.0, long_delay_probability=0.10,
                          long_delay_min_seconds=3600, long_delay_max_seconds=10800,
                          night_start_hour=0, night_end_hour=8)


def test_is_night_default_window():
    assert is_night(3, _t()) is True
    assert is_night(0, _t()) is True
    assert is_night(8, _t()) is False       # end exclusive
    assert is_night(14, _t()) is False


def test_seconds_until_morning():
    assert seconds_until_morning(6, _t()) == 2 * 3600   # 6 -> 8


def test_read_delay_interpolates():
    assert read_delay(_t(), 0.0) == 30
    assert read_delay(_t(), 1.0) == 900
    assert read_delay(_t(), 0.5) == 465


def test_typing_seconds_scales_with_length():
    assert typing_seconds("1234567890", _t()) == 1.0     # 10 chars -> 1s
    assert typing_seconds("12345", _t()) == 0.5


def test_maybe_long_delay_gated_by_roll():
    assert maybe_long_delay(_t(), roll=0.5, rand=0.0) == 0        # above prob
    assert maybe_long_delay(_t(), roll=0.05, rand=0.0) == 3600    # fires, min
    assert maybe_long_delay(_t(), roll=0.05, rand=1.0) == 10800   # fires, max
