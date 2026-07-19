from socializer.safety.kill_switch import KillSwitch


def test_engage_release(tmp_path):
    k = KillSwitch(str(tmp_path))
    assert not k.is_engaged()
    k.engage()
    assert k.is_engaged()
    k.release()
    assert not k.is_engaged()


def test_pause_resume_independent_of_kill(tmp_path):
    k = KillSwitch(str(tmp_path))
    k.pause()
    assert k.is_paused()
    assert not k.is_engaged()
    k.resume()
    assert not k.is_paused()
