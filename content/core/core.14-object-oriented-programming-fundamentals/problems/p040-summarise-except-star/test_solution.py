import pytest

from solution import run_all, summarise


def good():
    return 1


def two():
    return 2


def bad_int():
    return int("x")


def bad_key():
    return {}["missing"]


def bad_index():
    return [][0]


def bad_decode():
    return b"\xff".decode("utf-8")


def test_all_good_returns_results():
    assert run_all([("a", good), ("b", two)]) == {"a": 1, "b": 2}, "No failures: return {name: result}."
    assert run_all([]) == {}, "No tasks: an empty dict."


def test_failures_raise_group():
    with pytest.raises(ExceptionGroup) as info:
        run_all([("a", good), ("b", bad_int), ("c", bad_key)])
    eg = info.value
    assert eg.message == "2 of 3 tasks failed", "The group message is '{failed} of {total} tasks failed'."
    kinds = [type(e) for e in eg.exceptions]
    assert kinds == [ValueError, KeyError], "Put the real exceptions in the group, in task order."


def test_every_task_runs():
    ran = []

    def mark(name, fail):
        def task():
            ran.append(name)
            if fail:
                raise RuntimeError(name)
            return name
        return task

    tasks = [("a", mark("a", True)), ("b", mark("b", False)), ("c", mark("c", True))]
    with pytest.raises(ExceptionGroup):
        run_all(tasks)
    assert ran == ["a", "b", "c"], "A failing task must not stop the others: catch each failure and go on."


def test_notes_name_the_task():
    with pytest.raises(ExceptionGroup) as info:
        run_all([("import", bad_int), ("mail", good), ("report", bad_index)])
    notes = [getattr(e, "__notes__", []) for e in info.value.exceptions]
    assert notes == [["task: import"], ["task: report"]], "Add a note 'task: <name>' to each failed task's exception with add_note."


def test_run_all_does_not_catch_keyboard_interrupt():
    def stop():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        run_all([("a", good), ("b", stop)])


def test_summarise_mixed():
    tasks = [("a", good), ("b", bad_int), ("c", bad_key), ("d", bad_index), ("e", bad_int)]
    assert summarise(tasks) == {"ok": 1, "value_errors": 2, "key_errors": 1, "other_errors": 1}, (
        "Count each kind with its own except* clause; IndexError is not a KeyError, so it is 'other'."
    )


def test_summarise_all_good():
    assert summarise([("a", good), ("b", two)]) == {"ok": 2, "value_errors": 0, "key_errors": 0, "other_errors": 0}, (
        "No failures: everything is ok and run_all raises nothing."
    )
    assert summarise([]) == {"ok": 0, "value_errors": 0, "key_errors": 0, "other_errors": 0}, "No tasks at all."


def test_summarise_subclasses():
    tasks = [("d", bad_decode), ("i", bad_index), ("z", lambda: 1 / 0)]
    assert summarise(tasks) == {"ok": 0, "value_errors": 1, "key_errors": 0, "other_errors": 2}, (
        "UnicodeDecodeError is a ValueError subclass; IndexError and ZeroDivisionError are others."
    )


def test_summarise_only_others():
    def custom():
        raise RuntimeError("boom")

    assert summarise([("x", custom), ("y", good)]) == {"ok": 1, "value_errors": 0, "key_errors": 0, "other_errors": 1}, (
        "Unknown kinds must not escape summarise: catch the rest with except* Exception."
    )
