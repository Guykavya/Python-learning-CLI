import pytest

from solution import Task


def names(tasks):
    return [(t.priority, t.name) for t in tasks]


def test_lt_by_priority():
    assert Task(1, "x") < Task(2, "a"), "A smaller priority number sorts first, whatever the name."
    assert not (Task(2, "a") < Task(1, "x")), "Task(2, ...) is not less than Task(1, ...)."


def test_ties_use_name():
    assert Task(2, "a") < Task(2, "b"), "On equal priority compare names: 'a' < 'b'."
    assert not (Task(2, "b") < Task(2, "a")), "'b' is not less than 'a'."
    assert not (Task(2, "a") < Task(2, "a")), "An equal task is not less than itself."


def test_sorted():
    ts = [Task(2, "b"), Task(1, "z"), Task(2, "a"), Task(0, "q")]
    assert names(sorted(ts)) == [(0, "q"), (1, "z"), (2, "a"), (2, "b")], "sorted() should order by (priority, name)."


def test_sort_in_place_and_reverse():
    ts = [Task(1, "a"), Task(3, "c"), Task(2, "b")]
    ts.sort(reverse=True)
    assert names(ts) == [(3, "c"), (2, "b"), (1, "a")], "reverse=True gives the largest first."


def test_min_max():
    ts = [Task(2, "b"), Task(1, "z"), Task(2, "a")]
    assert (min(ts).priority, min(ts).name) == (1, "z"), "min() uses <."
    assert (max(ts).priority, max(ts).name) == (2, "b"), "max() uses < as well; ties go by name."


def test_gt_is_reflected():
    assert Task(2, "a") > Task(1, "z"), "You only defined __lt__, but a > b works because Python tries b < a."


def test_foreign_types_raise_typeerror():
    with pytest.raises(TypeError):
        Task(1, "a") < 5
    assert Task(1, "a").__lt__(5) is NotImplemented, "Return NotImplemented (not False) for non-Task values."
