from socializer.contacts import load_contacts, ContactBook, slug, Contact

YAML = """
contacts:
  - telegram: "@masha"
    name: "Маша"
    mode: "auto"
    relationship: "romantic"
    tone: "тёплый"
    goal: "встреча"
    notes: "дизайнер"
    reengage_after_days: 3
  - telegram: "777"
    name: "Дима"
    mode: "draft"
    relationship: "friend"
    tone: "по-братски"
    goal: "не терять контакт"
"""


def test_loads_contacts_with_defaults(tmp_path):
    p = tmp_path / "contacts.yaml"
    p.write_text(YAML)
    contacts = load_contacts(str(p))
    assert len(contacts) == 2
    masha = contacts[0]
    assert masha.mode == "auto"
    assert masha.reengage_after_days == 3
    dima = contacts[1]
    assert dima.notes == ""                 # default
    assert dima.reengage_after_days == 0    # default


def test_slug_is_filesystem_safe():
    assert slug(Contact(telegram="@Masha", name="", mode="draft",
                        relationship="", tone="", goal="")) == "masha"


def test_match_by_username_and_id(tmp_path):
    p = tmp_path / "contacts.yaml"
    p.write_text(YAML)
    book = ContactBook(load_contacts(str(p)))
    assert book.match(111, "masha").name == "Маша"     # by username, no @
    assert book.match(777, None).name == "Дима"         # by numeric id
    assert book.match(222, "stranger") is None
