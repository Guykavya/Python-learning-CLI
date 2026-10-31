import pytest

from solution import Recorder


def test_calls_are_recorded_in_order():
    @Recorder
    def add(a, b=0):
        return a + b

    assert add(1, 2) == 3 and add(5, b=1) == 6, "The decorated function must still return its result."
    assert add.calls == [((1, 2), {}, "ok", 3), ((5,), {"b": 1}, "ok", 6)], (
        "Record each call as the tuple (args, kwargs, 'ok', result): args is a tuple, kwargs a dict."
    )


def test_exceptions_are_recorded_and_reraised():
    @Recorder
    def div(a, b):
        return a / b

    with pytest.raises(ZeroDivisionError):
        div(1, 0)
    assert len(div.calls) == 1, "A call that raises must still be recorded."
    args, kwargs, status, err = div.calls[0]
    assert (args, kwargs, status) == ((1, 0), {}, "error"), "Failed calls are recorded with the status 'error'."
    assert isinstance(err, ZeroDivisionError), "For an error, the last item is the exception object."


def test_last_result_skips_errors():
    @Recorder
    def half(n):
        if n % 2:
            raise ValueError("odd")
        return n // 2

    with pytest.raises(LookupError):
        half.last_result
    half(8)
    with pytest.raises(ValueError):
        half(3)
    assert half.last_result == 4, "last_result is the result of the most recent SUCCESSFUL call (skip 'error' entries)."
    half(10)
    assert half.last_result == 5, "A newer successful call replaces it."


def test_last_result_is_a_property():
    assert isinstance(Recorder.__dict__["last_result"], property), "Make last_result a @property, so it is read as half.last_result without ()."


def test_clear():
    @Recorder
    def f(x):
        return x

    f(1)
    f(2)
    f.clear()
    assert f.calls == [], "clear() empties the list of calls."
    f(3)
    assert f.calls == [((3,), {}, "ok", 3)], "Recording continues after clear()."


def test_metadata_is_copied_like_functools_wraps():
    @Recorder
    def documented(x):
        """Return x."""
        return x

    assert documented.__name__ == "documented", "Use functools.update_wrapper(self, func) in __init__ so __name__ is kept."
    assert documented.__doc__ == "Return x.", "update_wrapper also copies the docstring."
    assert documented.__wrapped__(7) == 7, "update_wrapper stores the original function as __wrapped__."


def test_each_decorated_function_has_its_own_state():
    @Recorder
    def a():
        return 1

    @Recorder
    def b():
        return 2

    a()
    a()
    b()
    assert len(a.calls) == 2 and len(b.calls) == 1, "calls must be created in __init__ (per object), not shared in the class body."


def test_repr():
    @Recorder
    def f():
        return 0

    f()
    f()
    assert repr(f) == "<Recorder f: 2 call(s)>", "repr is <Recorder NAME: N call(s)>."
