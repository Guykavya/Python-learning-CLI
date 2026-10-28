import pytest

from solution import debug


def test_without_parentheses(capsys):
    @debug
    def add(a, b):
        return a + b

    assert add(2, 3) == 5, "@debug without parentheses: debug receives the function and must return the wrapper."
    assert capsys.readouterr().out == "DEBUG: add(2, 3) -> 5\n", "Default prefix DEBUG, and print when log is None."


def test_empty_parentheses(capsys):
    @debug()
    def neg(x):
        return -x

    assert neg(4) == -4, "@debug() with no arguments must return a decorator."
    assert capsys.readouterr().out == "DEBUG: neg(4) -> -4\n"


def test_with_options():
    lines = []

    @debug(prefix="TRACE", log=lines)
    def greet(name, punct="!"):
        return "hi " + name + punct

    assert greet("ann", punct="?") == "hi ann?"
    assert greet("bo") == "hi bo!"
    assert lines == [
        "TRACE: greet('ann', punct='?') -> 'hi ann?'",
        "TRACE: greet('bo') -> 'hi bo!'",
    ], "Use repr for arguments and the result; keywords as key=repr(value); only the arguments actually passed."


def test_returns_a_decorator_not_a_wrapper():
    lines = []
    deco = debug(log=lines)
    assert callable(deco), "debug(log=...) must return a decorator."

    def square(x):
        return x * x

    wrapped = deco(square)
    assert lines == [], "Applying the decorator must not call the function or log anything."
    assert wrapped(3) == 9
    assert lines == ["DEBUG: square(3) -> 9"]


def test_same_options_reused():
    lines = []
    deco = debug(prefix="P", log=lines)

    @deco
    def one():
        return 1

    @deco
    def two():
        return 2

    one()
    two()
    assert lines == ["P: one() -> 1", "P: two() -> 2"], "One decorator can be applied to many functions; use each function's own name."


def test_exception_is_recorded_and_raised():
    lines = []

    @debug(log=lines)
    def div(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        div(1, 0)
    assert lines == ["DEBUG: div(1, 0) raised ZeroDivisionError"], "Record 'raised <ExceptionName>' and re-raise."


def test_positional_string_is_an_error():
    with pytest.raises(TypeError) as info:
        debug("TRACE")
    assert "prefix" in str(info.value), "A string in place of the function: raise TypeError and tell the user to write prefix=..."


def test_metadata():
    @debug
    def f(x):
        """Doc."""
        return x

    assert f.__name__ == "f" and f.__doc__ == "Doc.", "Use functools.wraps in both ways of using debug."

    @debug(log=[])
    def g():
        """Gee."""

    assert g.__name__ == "g" and g.__doc__ == "Gee."
