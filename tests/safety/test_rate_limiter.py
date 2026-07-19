from socializer.config import LimitSettings
from socializer.safety.rate_limiter import RateLimiter, days_between


def _limits():
    return LimitSettings(max_messages_per_day=4, max_per_contact_per_day=2,
                         max_new_contacts_per_day=1, warmup_days=7)


def test_days_between():
    assert days_between("2026-07-19", "2026-07-19") == 0
    assert days_between("2026-07-19", "2026-07-26") == 7


def test_per_contact_cap(tmp_path):
    rl = RateLimiter(str(tmp_path), _limits(), install_iso="2026-01-01")
    d = "2026-07-19"
    assert rl.allow_message("masha", False, d, "2026-01-01")
    rl.record_message("masha", False, d)
    rl.record_message("masha", False, d)                 # now 2 == cap
    assert rl.allow_message("masha", False, d, "2026-01-01") is False   # per-contact hit
    assert rl.allow_message("dima", False, d, "2026-01-01") is True     # other contact ok


def test_daily_total_cap_and_reset(tmp_path):
    rl = RateLimiter(str(tmp_path), _limits(), install_iso="2026-01-01")
    d = "2026-07-19"
    for slug in ["a", "b", "c", "d"]:
        assert rl.allow_message(slug, False, d, "2026-01-01")
        rl.record_message(slug, False, d)
    assert rl.allow_message("e", False, d, "2026-01-01") is False       # 4 == total cap
    # next day resets
    assert rl.allow_message("e", False, "2026-07-20", "2026-01-01") is True


def test_warmup_halves_caps(tmp_path):
    rl = RateLimiter(str(tmp_path), _limits(), install_iso="2026-07-19")
    d = "2026-07-19"                                       # day 0, within warmup
    # total cap halved 4 -> 2
    rl.record_message("a", False, d)
    rl.record_message("b", False, d)
    assert rl.allow_message("c", False, d, "2026-07-19") is False


def test_new_contact_cap(tmp_path):
    rl = RateLimiter(str(tmp_path), _limits(), install_iso="2026-01-01")
    d = "2026-07-19"
    assert rl.allow_message("new1", True, d, "2026-01-01")
    rl.record_message("new1", True, d)                    # 1 == new-contact cap
    assert rl.allow_message("new2", True, d, "2026-01-01") is False
