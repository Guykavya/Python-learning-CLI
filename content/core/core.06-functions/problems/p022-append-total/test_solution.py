from solution import append_total


def test_changes_callers_list():
    marks = [10, 20, 30]
    append_total(marks)
    assert marks == [10, 20, 30, 60], (
        "The caller's list did not change. `numbers = numbers + [...]` only rebinds the local name; "
        "use a method that mutates the list, such as append.")


def test_returns_none():
    assert append_total([1, 2]) is None, "In-place functions return None, like list.sort()."


def test_same_object():
    marks = [5]
    before = id(marks)
    append_total(marks)
    assert id(marks) == before and marks == [5, 5]


def test_empty():
    empty = []
    append_total(empty)
    assert empty == [0], "The sum of an empty list is 0, so the list becomes [0]."


def test_twice():
    data = [1, 2]
    append_total(data)
    append_total(data)
    assert data == [1, 2, 3, 6], "Second call: the sum of [1, 2, 3] is 6."
