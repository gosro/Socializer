from socializer.clock import real_now, install_date


def test_real_now_shape():
    today, epoch, hour, ts, rh = real_now()
    assert len(today) == 10 and today[4] == "-"       # YYYY-MM-DD
    assert isinstance(epoch, int) and epoch > 0
    assert 0 <= hour <= 23
    assert "T" in ts
    assert len(rh) >= 4


def test_install_date_persists(tmp_path):
    d1 = install_date(str(tmp_path))
    d2 = install_date(str(tmp_path))
    assert d1 == d2                                     # stable across calls
    assert len(d1) == 10
