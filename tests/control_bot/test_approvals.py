from socializer.approval.queue import new_request, DRAFT, INVITATION
from socializer.control_bot.approvals import render_request, buttons_for, parse_callback


def _req(kind, candidate=""):
    return new_request(kind, "masha", 111, "Маша зовёт гулять", candidate,
                       "2026-07-19T12:00:00", "x1")


def test_render_draft_shows_candidate():
    txt = render_request(_req(DRAFT, "пойдём в субботу?"))
    assert "пойдём в субботу?" in txt


def test_buttons_for_draft_have_send_skip_edit():
    rows = buttons_for(_req(DRAFT, "ок"))
    labels = [label for row in rows for (label, _data) in row]
    datas = [data for row in rows for (_l, data) in row]
    assert any("тправ" in l for l in labels)          # Отправить
    assert any(d.startswith(b"send:") for d in datas)
    assert any(d.startswith(b"skip:") for d in datas)
    assert any(d.startswith(b"edit:") for d in datas)


def test_buttons_for_invitation_have_reply_own_ignore():
    datas = [d for row in buttons_for(_req(INVITATION)) for (_l, d) in row]
    assert any(d.startswith(b"reply:") for d in datas)
    assert any(d.startswith(b"own:") for d in datas)
    assert any(d.startswith(b"ignore:") for d in datas)


def test_parse_callback_splits_decision_and_id():
    assert parse_callback(b"send:20260719_x1") == ("send", "20260719_x1")
