from socializer.memory.personality import read_personality, write_personality


def test_read_missing_returns_fallback(tmp_path):
    text = read_personality(str(tmp_path))
    assert "коротко" in text.lower()


def test_write_then_read_roundtrip(tmp_path):
    write_personality(str(tmp_path), "# Мой стиль\nкороткие фразы")
    assert read_personality(str(tmp_path)) == "# Мой стиль\nкороткие фразы"
