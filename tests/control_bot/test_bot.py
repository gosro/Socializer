import socializer.control_bot.bot as mod


def test_to_inline_maps_rows(monkeypatch):
    made = []
    class FakeButton:
        @staticmethod
        def inline(label, data):
            made.append((label, data))
            return ("BTN", label, data)
    monkeypatch.setattr(mod, "Button", FakeButton)
    rows = mod.to_inline([[("Отправить", b"send:1"), ("Пропустить", b"skip:1")]])
    assert rows == [[("BTN", "Отправить", b"send:1"), ("BTN", "Пропустить", b"skip:1")]]


async def test_callback_enforces_owner_and_forwards_decision():
    forwarded = []

    async def on_decision(decision, rid):
        forwarded.append((decision, rid))

    cb = mod.ControlBot(client=None, queue=None, kill=None, owner_id=9,
                        on_decision=on_decision)

    class FakeEvent:
        def __init__(self, sender_id, data):
            self.sender_id = sender_id
            self.data = data
            self.answered = False
            self.edited = None
        async def answer(self, *a, **k): self.answered = True
        async def edit(self, text): self.edited = text

    # non-owner: ignored, no forward
    ev_bad = FakeEvent(1, b"send:abc")
    await cb._on_callback(ev_bad)
    assert forwarded == []

    # owner: acked + forwarded
    ev_ok = FakeEvent(9, b"send:abc")
    await cb._on_callback(ev_ok)
    assert ev_ok.answered is True
    assert forwarded == [("send", "abc")]
