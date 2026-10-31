import inspect
from functools import wraps

import pytest

from solution import log_arguments


def test_names_and_defaults():
    log = []

    @log_arguments(log)
    def send(user, text, urgent=False):
        return f"sent to {user}"

    assert send(1, "hi") == "sent to 1", "Return the function's result."
    send(2, text="yo", urgent=True)
    assert log == [
        "send(user=1, text='hi', urgent=False)",
        "send(user=2, text='yo', urgent=True)",
    ], "Name every parameter in signature order and fill in defaults with apply_defaults()."


def test_keyword_order_does_not_matter():
    log = []

    @log_arguments(log)
    def box(w, h, d=1):
        return w * h * d

    box(h=3, w=2)
    assert log == ["box(w=2, h=3, d=1)"], "Use bound.arguments: it lists parameters in signature order, not in the order the caller wrote them."


def test_star_args():
    log = []

    @log_arguments(log)
    def total(first, *rest):
        return first + sum(rest)

    assert total(1, 2, 3) == 6
    assert log == ["total(first=1, rest=(2, 3))"], "A *args parameter is bound as a tuple."


def test_bad_call_is_not_logged():
    log = []
    called = []

    @log_arguments(log)
    def pair(a, b):
        called.append(True)

    with pytest.raises(TypeError):
        pair(1)
    with pytest.raises(TypeError):
        pair(1, 2, c=3)
    assert log == [], "Bind first: a call that does not fit raises TypeError before anything is logged."
    assert called == [], "A call that does not fit must not reach the function."


def test_signature_is_kept():
    @log_arguments([])
    def send(user, text, urgent=False):
        """Send a message."""

    assert str(inspect.signature(send)) == "(user, text, urgent=False)", (
        "Use functools.wraps: it sets __wrapped__, which inspect.signature follows."
    )
    assert send.__name__ == "send" and send.__doc__ == "Send a message."


def shout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper


def test_on_top_of_another_decorator():
    log = []

    @log_arguments(log)
    @shout
    def greet(name, punct="!"):
        return f"hi {name}{punct}"

    assert greet("ann") == "HI ANN!", "Call the function you were given (the shout wrapper), so its effect is kept."
    assert log == ["greet(name='ann', punct='!')"], (
        "inspect.signature(func) follows __wrapped__ through shout's wrapper to the real parameters. "
        "Did you build the signature from the wrapper's own (*args, **kwargs)?"
    )
