import pytest

from solution import memoize


def test_caches_results():
    calls = []

    @memoize()
    def area(w, h=1):
        calls.append((w, h))
        return w * h

    assert area(2, h=3) == 6
    assert area(2, h=3) == 6, "A repeated call returns the stored result."
    assert calls == [(2, 3)], "The second call with the same arguments must not run the body."
    assert len(area.cache) == 1, "Store the cache dict as wrapper.cache."


def test_keyword_order_is_normalised():
    calls = []

    @memoize()
    def box(a=0, b=0):
        calls.append(1)
        return a - b

    assert box(a=1, b=2) == -1
    assert box(b=2, a=1) == -1
    assert len(calls) == 1, "Sort the keyword items so a=1, b=2 and b=2, a=1 give the same key."


def test_positional_and_keyword_are_different_keys():
    calls = []

    @memoize()
    def area(w, h=1):
        calls.append(1)
        return w * h

    area(2, 3)
    area(2, h=3)
    assert len(calls) == 2, "The default key is (args, sorted kwargs): (2, 3) and (2,) + h=3 are different keys."


def test_none_is_cached():
    calls = []

    @memoize()
    def find(x):
        calls.append(x)
        return None

    assert find(1) is None
    assert find(1) is None
    assert calls == [1], "None is a real result. Check `if k in cache`, not `if cache.get(k)`."


def test_exceptions_not_cached():
    attempts = []

    @memoize()
    def risky(x):
        attempts.append(x)
        if len(attempts) == 1:
            raise ValueError("first time fails")
        return x * 10

    with pytest.raises(ValueError):
        risky(4)
    assert risky(4) == 40, "A failed call must not store anything: the next call runs the body again."
    assert risky(4) == 40
    assert len(attempts) == 2


def test_custom_key_for_lists():
    calls = []

    @memoize(key=lambda xs: tuple(xs))
    def total(xs):
        calls.append(1)
        return sum(xs)

    assert total([1, 2]) == 3, "With a key function, the cache key is key(*args, **kwargs), so a list is fine."
    assert total([1, 2]) == 3
    assert len(calls) == 1, "Equal lists give equal tuple keys: the second call is a hit."
    assert (1, 2) in total.cache, "The cache key must be exactly what the key function returned."


def test_custom_key_case_insensitive():
    calls = []

    @memoize(key=str.lower)
    def lookup(name):
        calls.append(name)
        return name.title()

    assert lookup("Ann") == "Ann"
    assert lookup("ANN") == "Ann", "key=str.lower makes 'Ann' and 'ANN' the same entry, so the first result is returned."
    assert calls == ["Ann"]


def test_unhashable_default_key():
    @memoize()
    def total(xs):
        return sum(xs)

    with pytest.raises(TypeError):
        total([1, 2])


def test_cache_clear_and_separate_caches():
    m = memoize()
    calls = []

    @m
    def double(x):
        calls.append("d")
        return x * 2

    @m
    def triple(x):
        calls.append("t")
        return x * 3

    assert double(5) == 10
    assert triple(5) == 15, "Each function needs its own cache: create the dict in decorator(), not in memoize()."
    double.cache_clear()
    assert double.cache == {}, "cache_clear() empties the cache."
    assert double(5) == 10
    assert calls == ["d", "t", "d"], "After cache_clear() the body runs again."
    assert len(triple.cache) == 1, "Clearing double's cache must not clear triple's."


def test_metadata():
    @memoize()
    def f(x):
        """Doc."""
        return x

    assert f.__name__ == "f" and f.__doc__ == "Doc.", "Use functools.wraps."
