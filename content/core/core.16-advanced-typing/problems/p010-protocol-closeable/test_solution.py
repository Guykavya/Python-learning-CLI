import io
import typing
from collections.abc import Iterable
from typing import get_args, get_origin, get_type_hints

import pytest

import solution
from solution import close_all, close_quietly


def test_closeable_is_a_protocol():
    c = getattr(solution, "Closeable", None)
    assert c is not None, "Define a class named Closeable."
    assert typing.is_protocol(c), "Closeable must inherit from Protocol: class Closeable(Protocol)."
    assert typing.get_protocol_members(c) == frozenset({"close"}), "Closeable has exactly one member: the method close."
    assert get_type_hints(c.close) == {"return": type(None)}, "close(self) -> None."


def test_function_hints():
    c = solution.Closeable
    h = get_type_hints(close_all)
    assert get_origin(h["items"]) is Iterable and get_args(h["items"]) == (c,), "close_all(items: Iterable[Closeable])."
    assert h["return"] is int, "close_all returns how many were closed: -> int."
    assert get_type_hints(close_quietly) == {"item": c, "return": bool}, "close_quietly(item: Closeable) -> bool."


class Conn:
    def __init__(self, log, name):
        self.log, self.name = log, name

    def close(self):
        self.log.append(self.name)


class Broken:
    def close(self):
        raise OSError("already gone")


def test_close_all_calls_in_order_and_counts():
    log = []
    assert close_all([Conn(log, "a"), Conn(log, "b"), Conn(log, "c")]) == 3, "Return the number of items closed."
    assert log == ["a", "b", "c"], "Close the items in the order given."
    assert close_all([]) == 0, "No items: 0."


def test_works_without_inheritance():
    f = io.StringIO("data")
    assert close_all([f]) == 1 and f.closed, "A StringIO has close() so it fits Closeable without inheriting from it."


def test_accepts_any_iterable():
    log = []
    assert close_all(Conn(log, c) for c in "xy") == 2 and log == ["x", "y"], "items may be a generator: iterate it once."


def test_close_all_does_not_hide_errors():
    log = []
    with pytest.raises(OSError):
        close_all([Conn(log, "a"), Broken(), Conn(log, "b")])
    assert log == ["a"], "close_all stops at the first error and lets it propagate; items after it are not closed."


def test_close_quietly():
    log = []
    assert close_quietly(Conn(log, "a")) is True and log == ["a"], "Success: close the item and return True."
    assert close_quietly(Broken()) is False, "close() raised: return False, do not let the exception out."


def test_close_quietly_only_swallows_exceptions():
    class Interrupt:
        def close(self):
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        close_quietly(Interrupt())
