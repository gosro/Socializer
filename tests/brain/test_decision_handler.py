from socializer.brain.decision_handler import DecisionHandler
from socializer.approval.queue import ApprovalQueue, new_request, DRAFT, INVITATION
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings
from socializer.safety.rate_limiter import RateLimiter


class _FakeClient:
    def __init__(self): self.sent = []
    def action(self, chat, kind):
        class _C:
            async def __aenter__(s): return s
            async def __aexit__(s, *a): return False
        return _C()
    async def send_message(self, chat, text): self.sent.append((chat, text))


async def _noop(s): pass


def _settings(tmp_path):
    return Settings(llm=LLMSettings("openai_compatible", "u", "m", "k"),
                    limits=LimitSettings(40, 15, 3, 7),
                    timing=TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8),
                    data_dir=str(tmp_path), telegram_api_id=1, telegram_api_hash="h",
                    control_bot_token="t", owner_user_id=9)


def _handler(tmp_path, queue):
    s = _settings(tmp_path)
    def now(): return ("2026-07-19", 1_000_000, 14, "2026-07-19T14:00:00", "r1")
    return DecisionHandler(queue=queue, client=_FakeClient(), settings=s,
                           rate=RateLimiter(str(tmp_path), s.limits, "2026-01-01"),
                           sleeper=_noop, rng=lambda: 0.0, now=now, install_iso="2026-01-01")


async def test_send_dispatches_candidate(tmp_path):
    q = ApprovalQueue(str(tmp_path))
    req = new_request(DRAFT, "masha", 111, "ctx", "оо привет)", "2026-07-19T12:00:00", "x1")
    q.add(req)
    h = _handler(tmp_path, q)
    assert await h.apply("send", req.id) == "sent"
    assert h.client.sent == [(111, "оо привет)")]
    assert q.get(req.id) is None                          # consumed


async def test_skip_discards(tmp_path):
    q = ApprovalQueue(str(tmp_path))
    req = new_request(INVITATION, "masha", 111, "ctx", "", "2026-07-19T12:00:00", "x2")
    q.add(req)
    h = _handler(tmp_path, q)
    assert await h.apply("ignore", req.id) == "skipped"
    assert h.client.sent == []
    assert q.get(req.id) is None


async def test_edit_signals_await_text(tmp_path):
    q = ApprovalQueue(str(tmp_path))
    req = new_request(DRAFT, "masha", 111, "ctx", "черновик", "2026-07-19T12:00:00", "x3")
    q.add(req)
    h = _handler(tmp_path, q)
    assert await h.apply("edit", req.id) == "await_text"


async def test_missing_request_noop(tmp_path):
    h = _handler(tmp_path, ApprovalQueue(str(tmp_path)))
    assert await h.apply("send", "nope") == "noop"
