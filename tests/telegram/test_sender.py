import pytest
from socializer.config import TimingSettings
from socializer.telegram.sender import send_human, SendBlocked
from telethon.errors import FloodWaitError


def _t():
    return TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8)


class FakeClient:
    def __init__(self, raise_flood=False):
        self.sent = []
        self.typed = []
        self._raise = raise_flood
    def action(self, chat, kind):
        client = self
        class _Ctx:
            async def __aenter__(self_):
                client.typed.append((chat, kind)); return self_
            async def __aexit__(self_, *a): return False
        return _Ctx()
    async def send_message(self, chat, text):
        if self._raise:
            raise FloodWaitError(request=None, capture=42)
        self.sent.append((chat, text))


async def test_send_human_delays_types_then_sends():
    slept = []
    async def sleeper(s): slept.append(s)
    client = FakeClient()
    await send_human(client, 111, "привет", _t(), sleeper=sleeper, rng=lambda: 0.0)
    assert client.sent == [(111, "привет")]
    assert client.typed and client.typed[0][1] == "typing"
    assert slept                                        # at least the read delay happened


async def test_send_human_wraps_floodwait():
    async def sleeper(s): pass
    client = FakeClient(raise_flood=True)
    with pytest.raises(SendBlocked) as exc:
        await send_human(client, 111, "hi", _t(), sleeper=sleeper, rng=lambda: 0.0)
    assert exc.value.seconds == 42
