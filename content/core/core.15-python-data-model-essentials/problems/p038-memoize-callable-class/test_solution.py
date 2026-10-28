import pytest

from solution import Memoize


def test_second_call_uses_the_cache():
    calls = []

    @Memoize
    def square(n):
        calls.append(n)
        return n * n

    assert square(4) == 16 and square(4) == 16, "Memoize returns the same result."
    assert calls == [4], "The wrapped function must run only once for the same arguments."
    assert (square.hits, square.misses) == (1, 1), "First call = miss, second call = hit."


def test_different_arguments_are_different_entries():
    @Memoize
    def add(a, b=0):
        return a + b

    assert add(1, 2) == 3 and add(2, 1) == 3 and add(1, b=2) == 3, "Three different calls, same value."
    assert add.misses == 3, "(1, 2), (2, 1) and (1, b=2) are different keys: positional vs keyword matter, order matters."
    assert len(add.cache) == 3, "Each distinct call is cached once."


def test_keyword_order_does_not_matter():
    @Memoize
    def f(**kw):
        return sum(kw.values())

    f(a=1, b=2)
    f(b=2, a=1)
    assert (f.hits, f.misses) == (1, 1), "f(a=1, b=2) and f(b=2, a=1) are the same call: sort the keyword items when you build the key."


def test_results_that_are_none_or_falsy_are_cached():
    calls = []

    @Memoize
    def zero(x):
        calls.append(x)
        return 0 if x else None

    zero(0); zero(0); zero(1); zero(1)
    assert calls == [0, 1], "A cached result of None or 0 is still a cache hit: test `key in cache`, not `if cache.get(key)`."


def test_exceptions_are_not_cached():
    state = {"n": 0}

    @Memoize
    def flaky(x):
        state["n"] += 1
        if state["n"] == 1:
            raise ValueError("first time")
        return x

    with pytest.raises(ValueError):
        flaky(1)
    assert flaky(1) == 1, "A call that raised must not be stored: the next call runs the function again."
    assert flaky.misses == 2 and len(flaky.cache) == 1, "Both calls were misses; only the success is cached."


def test_unhashable_arguments_fall_back_to_calling_directly():
    calls = []

    @Memoize
    def total(items):
        calls.append(1)
        return sum(items)

    assert total([1, 2]) == 3 and total([1, 2]) == 3, "A list argument cannot be a dict key, but the call must still work."
    assert len(calls) == 2 and total.uncached == 2, "Unhashable arguments: call the function every time and count it in `uncached`."
    assert (total.hits, total.misses, len(total.cache)) == (0, 0, 0), "Uncached calls are neither hits nor misses and add nothing to the cache."
    assert total((1, 2)) == 3 and total((1, 2)) == 3 and total.hits == 1, "Tuples are hashable and do get cached."


def test_recursive_fib_is_fast():
    @Memoize
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    assert fib(25) == 75025, "Correct value required."
    assert fib.misses == 26, "With the cache, fib(0..25) is each computed once: 26 misses. Inside fib, the name `fib` is the Memoize object, so recursive calls use the cache."
    assert fib.hits == 23, "Every fib(n-2) for n from 3 to 25 is a hit (23 hits); fib(n-1) is always the first computation of that value."


def test_cache_clear():
    @Memoize
    def f(x):
        return x

    f(1); f(1)
    f.cache_clear()
    assert (f.hits, f.misses, f.uncached, len(f.cache)) == (0, 0, 0, 0), "cache_clear() empties the cache and resets all three counters."
    f(1)
    assert f.misses == 1, "After clearing, the same call is a miss again."


def test_metadata_and_independence():
    @Memoize
    def one(x):
        """One."""
        return x

    @Memoize
    def two(x):
        return x

    one(1)
    assert one.__name__ == "one" and one.__doc__ == "One.", "Copy name and docstring with functools.update_wrapper(self, func)."
    assert len(two.cache) == 0, "Each Memoize object has its own cache."
