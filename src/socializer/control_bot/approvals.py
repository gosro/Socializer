from __future__ import annotations
from socializer.approval.queue import ApprovalRequest, DRAFT


def render_request(req: ApprovalRequest) -> str:
    if req.kind == DRAFT:
        return (f"✍️ Черновик для {req.contact_slug}:\n\n{req.candidate}\n\n"
                f"(контекст: {req.context})")
    return (f"🔴 Нужно твоё решение ({req.kind}) — {req.contact_slug}:\n\n"
            f"{req.context}\n\nКак ответить?")


def buttons_for(req: ApprovalRequest) -> list[list[tuple[str, bytes]]]:
    rid = req.id.encode()
    if req.kind == DRAFT:
        return [[("✅ Отправить", b"send:" + rid),
                 ("✏️ Править", b"edit:" + rid),
                 ("⏭ Пропустить", b"skip:" + rid)]]
    return [[("✅ Ответить так", b"reply:" + rid),
             ("✏️ Написать своё", b"own:" + rid),
             ("🚫 Игнорировать", b"ignore:" + rid)]]


def parse_callback(data: bytes) -> tuple[str, str]:
    decision, _, rid = data.decode().partition(":")
    return decision, rid
