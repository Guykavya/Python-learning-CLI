import pytest

from solution import deprecated


def test_warns_once_into_list():
    log = []

    @deprecated("use area_v2", log)
    def area(w, h):
        return w * h

    assert log == [], "Decorating must not warn yet: warn on the first CALL."
    assert area(2, 3) == 6, "The old function must still work and return its result."
    assert area(4, h=5) == 20, "Pass keyword arguments through too."
    assert log == ["area is deprecated: use area_v2"], "Warn exactly once, with the text '<name> is deprecated: <message>'."


def test_prints_when_no_log(capsys):
    @deprecated("call new_total")
    def total(xs):
        return sum(xs)

    assert total([1, 2]) == 3
    assert total([5]) == 5
    out = capsys.readouterr().out
    assert out == "total is deprecated: call new_total\n", "With log=None, print the warning once (and only once)."


def test_each_function_warns_on_its_own():
    log = []
    old = deprecated("old API", log)

    @old
    def a():
        return "a"

    @old
    def b():
        return "b"

    a()
    a()
    b()
    b()
    assert log == ["a is deprecated: old API", "b is deprecated: old API"], (
        "Each decorated function needs its own 'warned' flag. If the flag lives in deprecated() "
        "instead of decorator(), b never warns."
    )


def test_warns_even_if_first_call_raises():
    log = []

    @deprecated("gone soon", log)
    def divide(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
    assert log == ["divide is deprecated: gone soon"], "Record the warning BEFORE calling the function."
    assert divide(6, 3) == 2
    assert len(log) == 1, "The first call happened (even though it raised), so do not warn again."


def test_metadata():
    @deprecated("x", [])
    def helper():
        """Help."""

    assert helper.__name__ == "helper" and helper.__doc__ == "Help.", "Use functools.wraps."
