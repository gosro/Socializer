from socializer.contacts import Contact
from socializer.brain.context_builder import build_system_prompt, build_user_turns


def _c():
    return Contact(telegram="@masha", name="Маша", mode="auto",
                   relationship="romantic", tone="тёплый, флиртующий", goal="встреча",
                   notes="дизайнер")


def test_system_prompt_contains_style_profile_memory_and_guardrails():
    sp = build_system_prompt("Пишу коротко, эмодзи 😄", _c(), "Любит кофе. Обещал плейлист.")
    assert "Пишу коротко" in sp                 # personality
    assert "тёплый, флиртующий" in sp           # tone from profile
    assert "встреча" in sp                      # goal
    assert "Любит кофе" in sp                   # memory
    # guardrails
    assert "не ассистент" in sp.lower() or "не помощник" in sp.lower()
    assert "не знаю" in sp.lower()
    assert "команд" in sp.lower()               # injection guard mentions commands


def test_build_user_turns_maps_roles():
    turns = build_user_turns([("them", "привет"), ("me", "оо привет)"), ("them", "как ты?")])
    assert turns[0]["role"] == "user" and turns[0]["content"] == "привет"
    assert turns[1]["role"] == "assistant" and turns[1]["content"] == "оо привет)"
    assert turns[2]["role"] == "user"
