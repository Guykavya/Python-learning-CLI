import pytest

from solution import UndoableList


def test_composition_not_inheritance():
    u = UndoableList()
    assert not isinstance(u, list), "UndoableList must wrap a list, not inherit from list."
    for name in ("sort", "insert", "extend", "remove", "reverse"):
        assert not hasattr(u, name), f"UndoableList should not offer {name}(): that change could not be undone."


def test_start_items_copied():
    start = ["milk", "eggs"]
    u = UndoableList(start)
    u.append("tea")
    assert start == ["milk", "eggs"], "Keep your own copy of the starting items."
    assert UndoableList(range(3)).to_list() == [0, 1, 2], "items can be any iterable."
    assert UndoableList().size() == 0, "No items: an empty list."


def test_lists_do_not_share():
    a, b = UndoableList(), UndoableList()
    a.append(1)
    assert b.size() == 0, "Two UndoableLists must not share items. Avoid items=[] as a default."


def test_reading():
    u = UndoableList(["a", "b", "c"])
    assert u.get(0) == "a" and u.get(-1) == "c", "get works with negative indexes too."
    assert u.size() == 3
    out = u.to_list()
    out.append("x")
    assert u.size() == 3, "to_list must return a new list."
    with pytest.raises(IndexError):
        u.get(3)


def test_basic_changes():
    u = UndoableList(["milk", "eggs"])
    u.append("tea")
    u.set(0, "oat milk")
    assert u.pop(1) == "eggs", "pop(index) returns the removed item."
    assert u.to_list() == ["oat milk", "tea"]
    assert u.pop() == "tea", "pop() removes the last item by default."


def test_undo_example():
    u = UndoableList(["milk", "eggs"])
    u.append("tea")
    u.set(0, "oat milk")
    u.pop(1)
    u.undo()
    assert u.to_list() == ["oat milk", "eggs", "tea"], "Undoing pop(1) puts 'eggs' back at index 1, not at the end."
    u.undo()
    assert u.to_list() == ["milk", "eggs", "tea"], "Undoing set(0, ...) puts the old value back."
    u.undo()
    assert u.to_list() == ["milk", "eggs"], "Undoing append removes the last item."
    with pytest.raises(IndexError, match="nothing to undo"):
        u.undo()


def test_undo_with_negative_indexes():
    u = UndoableList([1, 2, 3, 4])
    assert u.pop(-3) == 2, "pop(-3) removes the third item from the end."
    u.set(-1, 40)
    assert u.to_list() == [1, 3, 40]
    u.undo()
    assert u.to_list() == [1, 3, 4], "Undo set(-1, ...): remember the REAL index, not -1."
    u.undo()
    assert u.to_list() == [1, 2, 3, 4], (
        "Undo pop(-3) must put 2 back at index 1. Remember the real index; inserting at -3 puts it in the wrong place."
    )


def test_clear_and_undo():
    u = UndoableList(["a", "b"])
    u.clear()
    assert u.to_list() == [], "clear removes everything."
    u.undo()
    assert u.to_list() == ["a", "b"], "Undo clear brings every item back."


def test_redo():
    u = UndoableList(["milk", "eggs"])
    u.append("tea")
    u.set(0, "oat milk")
    u.pop(1)
    u.undo()
    u.undo()
    u.redo()
    assert u.to_list() == ["oat milk", "eggs", "tea"], "redo does the set(0, 'oat milk') again."
    u.redo()
    assert u.to_list() == ["oat milk", "tea"], "redo does the pop(1) again."
    with pytest.raises(IndexError, match="nothing to redo"):
        u.redo()
    u.undo()
    assert u.to_list() == ["oat milk", "eggs", "tea"], "A redone change can be undone again."


def test_new_change_clears_redo():
    u = UndoableList(["milk", "eggs"])
    u.pop()
    u.undo()
    u.append("rice")
    try:
        u.redo()
    except IndexError:
        pass
    else:
        pytest.fail("redo() still worked after a new change. Every new change must empty the redo stack.")
    assert u.to_list() == ["milk", "eggs", "rice"], "After a new change, the old undone change is gone for good."


def test_redo_clear_and_append():
    u = UndoableList([1, 2])
    u.clear()
    u.append(9)
    u.undo()
    u.undo()
    assert u.to_list() == [1, 2]
    u.redo()
    u.redo()
    assert u.to_list() == [9], "redo clear, then redo append(9)."


def test_failed_changes_are_not_recorded():
    u = UndoableList()
    with pytest.raises(IndexError):
        u.pop()
    with pytest.raises(IndexError):
        u.set(0, "x")
    with pytest.raises(IndexError, match="nothing to undo"):
        u.undo()
    u.append("a")
    with pytest.raises(IndexError):
        u.pop(5)
    with pytest.raises(IndexError):
        u.set(-2, "x")
    u.undo()
    assert u.to_list() == [], "Only the append was recorded; failed pop/set must not add undo steps."


def test_nothing_to_redo_at_start():
    with pytest.raises(IndexError, match="nothing to redo"):
        UndoableList([1]).redo()
