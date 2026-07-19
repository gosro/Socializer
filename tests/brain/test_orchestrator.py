from socializer.contacts import Contact
from socializer.telegram.listener import IncomingMessage
from socializer.brain.orchestrator import Orchestrator
from socializer.llm.base import LLMProvider
from socializer.config import Settings, LLMSettings, LimitSettings, TimingSettings
from socializer.safety.rate_limiter import RateLimiter
from socializer.safety.kill_switch import KillSwitch


def _settings(tmp_path):
    return Settings(
        llm=LLMSettings("openai_compatible", "u", "m", "k"),
        limits=LimitSettings(40, 15, 3, 7),
        timing=TimingSettings(30, 900, 1.0, 0.1, 3600, 10800, 0, 8),
        data_dir=str(tmp_path), telegram_api_id=1, telegram_api_hash="h",
        control_bot_token="t", owner_user_id=9)


class _Prov(LLMProvider):
    def __init__(self, text="оо привет)"): self._text = text
    async def complete(self, system, messages): return self._text


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


def _now():
    return ("2026-07-19", 1_000_000, 14, "2026-07-19T14:00:00", "r1")


async def _noop_sleeper(s): pass


def _orch(tmp_path, provider=None, contact_mode="auto"):
    s = _settings(tmp_path)
    from socializer.approval.queue import ApprovalQueue
    o = Orchestrator(
        provider=provider or _Prov(), data_dir=str(tmp_path), settings=s,
        rate=RateLimiter(str(tmp_path), s.limits, "2026-01-01"),
        kill=KillSwitch(str(tmp_path)), control_bot=_FakeBot(),
        queue=ApprovalQueue(str(tmp_path)), client=_FakeClient(),
        sleeper=_noop_sleeper, rng=lambda: 0.0, now=_now, install_iso="2026-01-01")
    return o


def _msg(mode="auto", text="как дела"):
    c = Contact(telegram="@masha", name="Маша", mode=mode,
                relationship="friend", tone="тёплый", goal="общение")
    return IncomingMessage(contact=c, text=text, chat_id=111)


async def test_auto_sends(tmp_path):
    o = _orch(tmp_path)
    assert await o.handle(_msg("auto")) == "sent"
    assert o.client.sent == [(111, "оо привет)")]


async def test_draft_queues_not_sends(tmp_path):
    o = _orch(tmp_path)
    assert await o.handle(_msg("draft")) == "draft"
    assert o.client.sent == []
    assert len(o.control_bot.notified) == 1


async def test_invitation_forces_approval(tmp_path):
    o = _orch(tmp_path)
    assert await o.handle(_msg("auto", "давай встретимся в субботу")) == "approval:invitation"
    assert o.client.sent == []


async def test_kill_switch_blocks(tmp_path):
    o = _orch(tmp_path)
    o.kill.engage()
    assert await o.handle(_msg("auto")) == "killed"
    assert o.client.sent == []


async def test_missing_fact_escalates(tmp_path):
    o = _orch(tmp_path, provider=_Prov("хм честно не помню"))
    assert await o.handle(_msg("auto", "помнишь как звали моего кота?")) == "approval:missing_fact"
    assert o.client.sent == []
