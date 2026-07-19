import importlib.util, os

spec = importlib.util.spec_from_file_location(
    "build_personality", os.path.join("scripts", "build_personality.py"))
bp = importlib.util.module_from_spec(spec)


def _load():
    spec.loader.exec_module(bp)


def test_parse_selection_filters_range_and_garbage():
    _load()
    assert bp.parse_selection("1,3,5", count=4) == [0, 2]     # 5 out of range (1..4) dropped
    assert bp.parse_selection(" 2 , x, 2 ", count=3) == [1]   # garbage + dedup


class _FakeMsg:
    def __init__(self, text): self.text = text


class _FakeClient:
    def __init__(self, msgs): self._msgs = msgs
    def iter_messages(self, chat, from_user=None):
        async def gen():
            for m in self._msgs:
                yield m
        return gen()


async def test_collect_own_messages_skips_empty():
    _load()
    client = _FakeClient([_FakeMsg("привет"), _FakeMsg(""), _FakeMsg(None), _FakeMsg("го")])
    out = await bp.collect_own_messages(client, chat=123, limit=10)
    assert out == ["привет", "го"]
