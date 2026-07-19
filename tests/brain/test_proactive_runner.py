from socializer.contacts import Contact, ContactBook
from socializer.brain.proactive_runner import ProactiveRunner
from socializer.llm.base import LLMProvider
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings
from socializer.safety.rate_limiter import RateLimiter
from socializer.safety.kill_switch import KillSwitch
from socializer.approval.queue import ApprovalQueue


class _Prov(LLMProvider):
    async def complete(self, system, messages): return "оо привет)"


class _FakeBot:
    def __init__(self): self.notified = []
    async def notify(self, req): self.notified.append(req)


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


def _runner(tmp_path, hour=14, book=None):
    s = _settings(tmp_path)
    def now(): return ("2026-07-19", 1_000_000, hour, "2026-07-19T14:00:00", "r1")
    return ProactiveRunner(
        provider=_Prov(), data_dir=str(tmp_path), settings=s,
        rate=RateLimiter(str(tmp_path), s.limits, "2026-01-01"),
        kill=KillSwitch(str(tmp_path)), control_bot=_FakeBot(),
        queue=ApprovalQueue(str(tmp_path)), client=_FakeClient(),
        book=book or ContactBook([Contact("@masha", "Маша", "auto", "friend",
                                          "тёплый", "контакт", reengage_after_days=3)]),
        sleeper=_noop, rng=lambda: 0.0, now=now, install_iso="2026-01-01",
        chat_id_for=lambda contact: 111)


async def test_sends_reengagement_for_due_auto(tmp_path):
    r = _runner(tmp_path)
    out = await r.run_once({"masha": 5})              # 5 >= 3 -> due
    assert out == ["sent:masha"]
    assert r.client.sent == [(111, "оо привет)")]


async def test_not_due_is_skipped(tmp_path):
    r = _runner(tmp_path)
    assert await r.run_once({"masha": 1}) == []       # not stale
    assert r.client.sent == []


async def test_night_skips(tmp_path):
    r = _runner(tmp_path, hour=3)
    assert await r.run_once({"masha": 5}) == ["night"]
    assert r.client.sent == []


async def test_draft_contact_queues(tmp_path):
    book = ContactBook([Contact("@masha", "Маша", "draft", "friend",
                                "тёплый", "контакт", reengage_after_days=3)])
    r = _runner(tmp_path, book=book)
    assert await r.run_once({"masha": 5}) == ["draft:masha"]
    assert r.client.sent == []
    assert len(r.control_bot.notified) == 1
