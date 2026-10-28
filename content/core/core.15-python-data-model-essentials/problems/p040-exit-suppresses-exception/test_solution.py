import pytest

from solution import Expect, Ignore


def test_ignore_swallows_listed_exception():
    with Ignore(KeyError) as ig:
        {}["missing"]
    assert ig.caught is True, "Ignore(KeyError) must catch the KeyError: return True from __exit__."
    assert isinstance(ig.exception, KeyError), "The caught exception object is stored in .exception."


def test_ignore_without_exception():
    with Ignore(KeyError) as ig:
        pass
    assert ig.caught is False and ig.exception is None, "No exception: caught is False and exception is None."


def test_ignore_code_after_the_failing_line_is_skipped():
    steps = []
    with Ignore(ValueError):
        steps.append("before")
        int("x")
        steps.append("after")
    steps.append("outside")
    assert steps == ["before", "outside"], "The block stops at the exception; the program continues after the `with`."


def test_ignore_other_exceptions_propagate():
    with pytest.raises(ZeroDivisionError):
        with Ignore(KeyError, ValueError):
            1 / 0


def test_ignore_several_types_and_subclasses():
    with Ignore(KeyError, ValueError) as ig:
        int("x")
    assert ig.caught, "Any of the listed types is caught."
    with Ignore(LookupError) as ig:
        [][0]
    assert ig.caught, "issubclass(exc_type, types) also catches subclasses: IndexError is a LookupError."
    with Ignore(Exception) as ig:
        raise OSError("disk")
    assert ig.exception.args == ("disk",), "The stored exception is the very object that was raised."


def test_ignore_can_be_reused_and_resets():
    ig = Ignore(ValueError)
    with ig:
        int("x")
    assert ig.caught is True, "First use catches."
    with ig:
        pass
    assert ig.caught is False, "A new `with` resets the state: set exception = None in __enter__."


def test_expect_passes_when_exception_raised():
    with Expect(ValueError) as ex:
        int("x")
    assert isinstance(ex.exception, ValueError), "Expect stores the exception it saw in .exception."
    with Expect(LookupError):
        {}["x"]


def test_expect_fails_when_nothing_raised():
    with pytest.raises(AssertionError) as info:
        with Expect(ValueError):
            pass
    assert "ValueError" in str(info.value), "The AssertionError message should name the expected exception class."


def test_expect_does_not_hide_the_wrong_exception():
    with pytest.raises(KeyError):
        with Expect(ValueError):
            {}["x"]


def test_exit_returns_a_real_bool_for_the_swallow_decision():
    ig = Ignore(ValueError)
    ig.__enter__()
    assert ig.__exit__(ValueError, ValueError("x"), None) is True, "Return True (not None) when swallowing."
    assert not ig.__exit__(KeyError, KeyError("x"), None), "Return a false value for exceptions that are not listed."
    assert not ig.__exit__(None, None, None), "No exception at all: return a false value."
