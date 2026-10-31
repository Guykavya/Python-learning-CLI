import pytest

from solution import Note


def test_tags_are_cleaned():
    a = Note("Lists", tags=[" Python ", "python", "Basics"])
    assert a.tags == ["python", "basics"], "Clean tags with strip().lower(), drop duplicates, keep first order."


def test_notes_without_tags_do_not_share():
    a = Note("Lists")
    a.add_tag("python")
    b = Note("Shopping")
    assert b.tags == [], (
        "A new note already has another note's tag. The default `tags=[]` is ONE list made when `def` runs, "
        "shared by every call. Use tags=None and build a new list inside __init__."
    )
    b.add_tag("food")
    assert a.tags == ["python"], "Adding a tag to b must not change a."


def test_callers_list_is_not_changed():
    mine = ["exam", " EXAM "]
    c = Note("OOP", tags=mine)
    assert mine == ["exam", " EXAM "], "Cleaning the tags must not change the caller's list. Build a new list."
    c.add_tag("revise")
    assert mine == ["exam", " EXAM "], (
        "add_tag changed the caller's list: self.tags is the same list object. Make self.tags a new list."
    )
    mine.append("later")
    assert c.tags == ["exam", "revise"], "Changing the caller's list later must not change the note."


def test_two_notes_from_one_list():
    shared = ["a"]
    x = Note("x", tags=shared)
    y = Note("y", tags=shared)
    x.add_tag("b")
    assert y.tags == ["a"], "Two notes made from the same list must still have separate tag lists."


def test_tags_any_iterable():
    n = Note("t", tags=("Z", "y"))
    assert n.tags == ["z", "y"], "tags may be a tuple (any iterable); the note stores its own list."
    assert isinstance(n.tags, list), "Store the tags as a list, so add_tag can append."


def test_history_is_per_note():
    a = Note("A", "v1")
    b = Note("B", "w1")
    a.edit("v2")
    assert b.history == [], (
        "Editing one note changed another note's history. `history = []` in the class body is a class "
        "attribute: one list for all notes. Create self.history = [] in __init__."
    )
    assert a.history == ["v1"], "edit saves the old body in the note's own history."


def test_edit_and_undo():
    a = Note("A", "")
    a.edit("v2")
    a.edit("v3")
    a.undo_edit()
    assert (a.body, a.history) == ("v2", [""]), "undo_edit puts back the last saved body."
    a.undo_edit()
    assert a.body == "", "Undo again goes back to the first body."
    with pytest.raises(IndexError, match="nothing to undo"):
        a.undo_edit()


def test_undo_on_fresh_note():
    b = Note("B", "start")
    with pytest.raises(IndexError, match="nothing to undo"):
        b.undo_edit()


def test_add_and_remove_tag():
    n = Note("t")
    n.add_tag("  Py ")
    n.add_tag("py")
    assert n.tags == ["py"], "add_tag cleans the tag and ignores one that is already there."
    with pytest.raises(ValueError):
        n.add_tag("   ")
    n.remove_tag("PY")
    assert n.tags == [], "remove_tag cleans the tag before removing it."
    with pytest.raises(KeyError):
        n.remove_tag("py")


def test_no_shared_lists_on_the_class():
    assert "history" not in vars(Note) or not isinstance(vars(Note)["history"], list), (
        "Note still has a class-level history list. Remove it; each note creates its own."
    )
    a = Note("a")
    b = Note("b")
    assert a.tags is not b.tags, "Each note needs its own tags list object."
    assert a.history is not b.history, "Each note needs its own history list object."


def test_count_still_shared():
    before = Note.count
    Note("one")
    Note("two")
    assert Note.count == before + 2, "Note.count must still count every note created (keep Note.count += 1)."
    assert "count" not in vars(Note("three")), "count must stay a class attribute, not become an instance attribute."
