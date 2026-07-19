from socializer.control_bot.commands import handle_command, is_owner
from socializer.safety.kill_switch import KillSwitch


def test_non_owner_ignored(tmp_path):
    k = KillSwitch(str(tmp_path))
    assert handle_command("/status", sender_id=5, owner_id=9, kill=k,
                          status_provider=lambda: "S") is None


def test_status_returns_provider_text(tmp_path):
    k = KillSwitch(str(tmp_path))
    out = handle_command("/status", 9, 9, k, status_provider=lambda: "всё ок")
    assert out == "всё ок"


def test_kill_engages_and_pause_resume(tmp_path):
    k = KillSwitch(str(tmp_path))
    handle_command("/kill", 9, 9, k, lambda: "")
    assert k.is_engaged()
    handle_command("/pause", 9, 9, k, lambda: "")
    assert k.is_paused()
    handle_command("/resume", 9, 9, k, lambda: "")
    assert not k.is_paused()
