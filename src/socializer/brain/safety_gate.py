from __future__ import annotations
from dataclasses import dataclass
from socializer.approval.queue import INVITATION, SENSITIVE, SUSPECTED_BOT

_INVITATION = ("пойдём", "пойдем", "встрет", "свидан", "увидимся", "сходим",
               "погуляем", "приезжай", "давай встретимся", "давай сходим")
_SENSITIVE = ("деньги", "денег", "перевод", "займ", "кредит", "болезн", "врач",
              "умер", "интим", "секс", "ссор", "суд", "полиц")
_INJECTION = ("ты бот", "ты ии", "ты нейросеть", "system prompt", "игнорируй",
              "покажи промпт", "ты теперь", "веди себя как", "переведи", "напиши код",
              "реши уравнение")
_HEDGES = ("не помню", "не знаю, что тебе", "не уверен", "честно не помню")


@dataclass(frozen=True)
class GateResult:
    needs_approval: bool
    kind: str
    reason: str


def _contains(text: str, needles: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(n in low for n in needles)


def classify_incoming(text: str) -> GateResult:
    if _contains(text, _INJECTION):
        return GateResult(True, SUSPECTED_BOT, "возможная попытка вскрыть агента")
    if _contains(text, _INVITATION):
        return GateResult(True, INVITATION, "приглашение/встреча — нужно твоё решение")
    if _contains(text, _SENSITIVE):
        return GateResult(True, SENSITIVE, "чувствительная тема")
    return GateResult(False, "", "")


def mentions_unknown_fact(reply: str) -> bool:
    return _contains(reply, _HEDGES)
