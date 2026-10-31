import pytest

from solution import memoize


def test_caches_results():
    calls = []

    @memoize
    def square(n):
        calls.append(n)
        return n * n

    assert square(4) == 16, "Return the function's result."
    assert square(4) == 16, "The second call must return the same result."
    assert calls == [4], "The second square(4) must come from the cache, not call the function again."
    assert square(5) == 25 and calls == [4, 5], "New arguments are a new key: call the function."
    assert len(square.cache) == 2, "wrapper.cache must be the dict that holds the results (2 keys now)."


def test_keyword_order_does_not_matter():
    calls = []

    @memoize
    def area(*, width, height):
        calls.append(1)
        return width * height

    assert area(width=2, height=3) == 6, "Pass keyword arguments through to func."
    assert area(height=3, width=2) == 6, "Same call with keywords in another order."
    assert len(calls) == 1, "Sort the kwargs items in the key: tuple(sorted(kwargs.items())), so order does not matter."


def test_kwargs_are_part_of_key():
    @memoize
    def greet(name, punct="!"):
        return name + punct

    assert greet("Ann") == "Ann!", "Default argument."
    assert greet("Ann", punct="?") == "Ann?", "Different keyword value means a different key. Did you leave kwargs out of the key?"


def test_none_result_is_cached():
    calls = []

    @memoize
    def nothing(x):
        calls.append(x)
        return None

    nothing(1)
    nothing(1)
    assert calls == [1], "A stored None is still a hit. Test `key in cache`, not `cache.get(key)`, which cannot tell None from missing."


def test_errors_not_cached():
    attempts = []

    @memoize
    def flaky(x):
        attempts.append(x)
        if len(attempts) == 1:
            raise ValueError("first try fails")
        return x * 10

    with pytest.raises(ValueError):
        flaky(3)
    assert flaky(3) == 30, "A call that raised must not be stored. The next call must try again."
    assert len(attempts) == 2, "The function should run exactly twice."


def test_recursive_fib():
    calls = []

    @memoize
    def fib(n):
        calls.append(n)
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(25) == 75025, "fib(25) must be correct."
    assert len(calls) == 26, "Each n from 0 to 25 should be computed once (26 calls). The recursive calls must go through the cache."


def test_separate_caches_and_metadata():
    @memoize
    def a(x):
        """Doc of a."""
        return "a"

    @memoize
    def b(x):
        return "b"

    assert (a(1), b(1)) == ("a", "b"), "Each decorated function needs its own cache. Create the dict inside memoize."
    assert a.__name__ == "a" and a.__doc__ == "Doc of a.", "Use @wraps(func) on the wrapper."
