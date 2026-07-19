from socializer.approval.queue import ApprovalQueue, new_request, INVITATION, DRAFT


def _req(rid="a1", kind=INVITATION, candidate=""):
    return new_request(kind, "masha", 111, "Маша зовёт на выставку", candidate,
                       now_iso="2026-07-19T12:00:00", rand_hex=rid)


def test_add_get_pending_resolve_roundtrip(tmp_path):
    q = ApprovalQueue(str(tmp_path))
    r = _req()
    q.add(r)
    assert q.get(r.id).context == "Маша зовёт на выставку"
    assert [x.id for x in q.pending()] == [r.id]
    removed = q.resolve(r.id)
    assert removed.id == r.id
    assert q.pending() == []
    assert q.get(r.id) is None


def test_persists_across_instances(tmp_path):
    q1 = ApprovalQueue(str(tmp_path))
    q1.add(_req(rid="zz", kind=DRAFT, candidate="привет)"))
    q2 = ApprovalQueue(str(tmp_path))                 # fresh instance, same dir
    pend = q2.pending()
    assert len(pend) == 1
    assert pend[0].candidate == "привет)"
    assert pend[0].kind == DRAFT
