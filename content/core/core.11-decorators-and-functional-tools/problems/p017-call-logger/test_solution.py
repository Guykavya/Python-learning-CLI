import pytest

from solution import logged


def test_positional_call():
    log = []

    @logged(log)
    def add(a, b):
        return a + b

    assert add(2, 3) == 5, "The wrapper must return the function's result, not the log line."
    assert log == ["add(2, 3) -> 5"], "Format: name(args) -> result, args joined by ', '."


def test_strings_use_repr():
    log = []

    @logged(log)
    def greet(name, loud=False):
        text = "hi " + name
        return text.upper() if loud else text

    greet("Ann", loud=True)
    assert log == ["greet('Ann', loud=True) -> 'HI ANN'"], "Use repr() for every value (strings get quotes) and key=repr(value) for keywords."


def test_no_arguments_and_none_result():
    log = []

    @logged(log)
    def ping():
        return None

    ping()
    assert log == ["ping() -> None"], "No arguments gives empty brackets; a None result is shown as None."


def test_keyword_order_kept():
    log = []

    @logged(log)
    def box(*, w, h):
        return w * h

    box(h=2, w=5)
    assert log == ["box(h=2, w=5) -> 10"], "Show keyword arguments in the order the caller gave them. Do not sort them."


def test_error_logged_and_reraised():
    log = []

    @logged(log)
    def div(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        div(1, 0)
    assert log == ["div(1, 0) raised ZeroDivisionError"], "On an error, log 'name(args) raised ErrorType' and then re-raise with a bare `raise`."


def test_many_calls_append():
    log = ["start"]

    @logged(log)
    def neg(x):
        return -x

    neg(1)
    neg(-2)
    assert log == ["start", "neg(1) -> -1", "neg(-2) -> 2"], "Append to the given list. Do not replace it or clear it."


def test_metadata():
    @logged([])
    def neg(x):
        """Negate."""
        return -x

    assert neg.__name__ == "neg" and neg.__doc__ == "Negate.", "Use @wraps(func) on the wrapper."
