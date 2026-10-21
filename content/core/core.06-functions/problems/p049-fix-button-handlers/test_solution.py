import inspect
from solution import make_handlers, make_adders


def test_handlers_each_remember_their_name():
    h = make_handlers(["Save", "Open", "Quit"])
    assert h["Save"]() == "Clicked Save", (
        "Every handler returns the LAST name: the lambdas share one loop variable (late binding). "
        "Give each handler its own scope with a factory function.")
    assert h["Open"]() == "Clicked Open"
    assert h["Quit"]() == "Clicked Quit"


def test_handlers_take_no_arguments():
    h = make_handlers(["Save"])
    params = inspect.signature(h["Save"]).parameters
    assert len(params) == 0, (
        "Handlers must take no arguments. The `name=name` default trick adds a parameter; use a factory instead.")


def test_adders():
    adders = make_adders(3)
    assert [add(10) for add in adders] == [10, 11, 12], "The adder at index i must add i, not the last i."


def test_adders_one_argument():
    adders = make_adders(2)
    assert len(inspect.signature(adders[1]).parameters) == 1, "Each adder takes exactly one argument, x."


def test_empty():
    assert make_handlers([]) == {}
    assert make_adders(0) == []
