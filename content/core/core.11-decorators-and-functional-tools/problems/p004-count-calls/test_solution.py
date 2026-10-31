import pytest

from solution import count_calls, square


def test_square_counts():
    start = square.calls
    assert square(3) == 9, "The wrapper must return the result of square. Did you forget `return func(...)`?"
    assert square(4) == 16, "square(4) is 16."
    assert square.calls == start + 2, "Two calls must add 2 to square.calls."


def test_starts_at_zero():
    @count_calls
    def hello():
        return "hi"

    assert hello.calls == 0, "Set wrapper.calls = 0 in the decorator, before returning the wrapper. Decorating is not a call."
    hello()
    assert hello.calls == 1, "One call: calls must be 1."


def test_arguments_pass_through():
    @count_calls
    def describe(name, age=0, *, city="?"):
        return f"{name}/{age}/{city}"

    assert describe("ann", 30, city="Pune") == "ann/30/Pune", "Pass both *args and **kwargs on to func."
    assert describe("bo") == "bo/0/?", "Defaults of func must still work through the wrapper."
    assert describe.calls == 2, "Both calls must be counted."


def test_separate_counters():
    @count_calls
    def a():
        return 1

    @count_calls
    def b():
        return 2

    a()
    a()
    b()
    assert (a.calls, b.calls) == (2, 1), "Each decorated function needs its own counter. Store it on its own wrapper, not in a global."


def test_counts_failing_call():
    @count_calls
    def boom():
        raise ValueError("bad")

    with pytest.raises(ValueError):
        boom()
    assert boom.calls == 1, "Count the call before calling func, so a call that raises is counted too."
