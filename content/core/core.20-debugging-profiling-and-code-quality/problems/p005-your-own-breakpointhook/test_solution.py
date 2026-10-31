import sys

import pytest

from solution import install_recorder, uninstall


def _not_installed(*args, **kwargs):
    raise AssertionError(
        "breakpoint() reached a hook the test put there as a guard: install_recorder() did not "
        "set sys.breakpointhook to your recorder."
    )


@pytest.fixture(autouse=True)
def guard_hook():
    """Never let a real debugger start, and always put the original hook back afterwards."""
    saved = sys.breakpointhook
    sys.breakpointhook = _not_installed
    yield
    sys.breakpointhook = saved


def average(xs):
    total = sum(xs)
    breakpoint()
    total = total / len(xs)
    breakpoint()
    return total


def test_records_function_and_locals():
    records = install_recorder()
    result = average([2, 4, 9])
    assert result == 5.0, "The recorder must not change what the program computes."
    assert len(records) == 2, f"Two breakpoint() calls should give 2 records, got {len(records)}."
    assert records[0] == {"function": "average", "locals": {"xs": [2, 4, 9], "total": 15}}, (
        f"First record is wrong: {records[0]!r}. Use sys._getframe(1): frame 0 is the hook itself."
    )


def test_locals_are_a_snapshot():
    records = install_recorder()
    average([2, 4, 9])
    assert records[0]["locals"]["total"] == 15, (
        "The first record shows the LATER value of total. Store dict(frame.f_locals), a copy "
        "taken at the moment of the call, not f_locals itself."
    )
    assert records[1]["locals"]["total"] == 5.0, "The second record should see total == 5.0."
    assert type(records[0]["locals"]) is dict, "Store a plain dict copy of the locals."
    assert records[0]["locals"] is not records[1]["locals"], "Each record needs its own dict."


def test_same_list_keeps_growing():
    records = install_recorder()

    def step(n):
        breakpoint()

    step(1)
    step(2)
    step(3)
    assert [r["locals"]["n"] for r in records] == [1, 2, 3], (
        "install_recorder must return the SAME list the hook appends to, in call order."
    )
    assert all(r["function"] == "step" for r in records), "function should be the caller's name, 'step'."


def test_hook_accepts_arguments():
    records = install_recorder()

    def chatty():
        label = "here"
        breakpoint("ignored", depth=2)

    try:
        chatty()
    except TypeError as exc:
        pytest.fail(
            f"breakpoint('ignored', depth=2) crashed: {exc}. breakpoint(*args, **kwargs) passes its "
            "arguments to the hook. Define the hook with *args and **kwargs and ignore them."
        )
    assert records == [{"function": "chatty", "locals": {"label": "here"}}], (
        "breakpoint(*args, **kwargs) passes its arguments to the hook. Define the hook with "
        "*args and **kwargs and ignore them."
    )


def test_each_install_gives_a_fresh_list():
    first = install_recorder()

    def one():
        breakpoint()

    one()
    second = install_recorder()
    one()
    assert len(first) == 1 and len(second) == 1, (
        "Each install_recorder() call should start a NEW empty list and point the hook at it."
    )


def test_uninstall_restores_the_original_hook():
    install_recorder()
    uninstall()
    assert sys.breakpointhook is sys.__breakpointhook__, (
        "uninstall() must set sys.breakpointhook back to sys.__breakpointhook__."
    )
