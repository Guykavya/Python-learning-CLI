import cProfile
import pstats

import solution
from solution import ways


def python_calls_in_solution(fn, *args):
    """Run fn under cProfile; return (result, total calls of Python functions defined in solution.py)."""
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        result = fn(*args)
    finally:
        profiler.disable()
    calls = sum(
        stat[1]
        for (filename, _line, _name), stat in pstats.Stats(profiler).stats.items()
        if filename == solution.__file__
    )
    return result, calls


def clear():
    if hasattr(solution.count, "cache_clear"):
        solution.count.cache_clear()


def test_small_examples():
    assert ways(4, [1, 2]) == 3, "4 = 1+1+1+1 = 1+1+2 = 2+2: three ways."
    assert ways(0, [5]) == 1, "Paying 0 has exactly one way: no coins."
    assert ways(3, [2]) == 0, "3 cannot be paid with only 2s."
    assert ways(5, []) == 0 and ways(0, []) == 1, "With no coins only the amount 0 can be paid (one way)."


def test_count_is_cached():
    assert hasattr(solution.count, "cache_info"), (
        "count has no cache_info(): decorate the recursive function count with @functools.cache or @lru_cache."
    )


def test_coins_as_list():
    assert ways(10, [1, 5, 10]) == 4, "ways must still accept a LIST of coins. Do not put @cache on ways itself (a list is unhashable)."


def test_different_coins_one_after_another():
    clear()
    assert ways(10, [1, 2]) == 6, "ways(10, [1, 2]) is 6."
    assert ways(10, [5]) == 1, (
        "After ways(10, [1, 2]), ways(10, [5]) must be 1. If the cache key does not include the coins "
        "(for example coins kept in a global), answers from the first coin list leak into the second."
    )
    assert ways(10, [3]) == 0, "ways(10, [3]) is 0."


def test_call_count_then_big_input():
    clear()
    result, calls = python_calls_in_solution(ways, 60, [1, 2, 5, 10, 20, 50])
    assert result == 793, f"ways(60, [1, 2, 5, 10, 20, 50]) is 793, got {result}."
    assert calls <= 1281, (
        f"Your functions in solution.py were called {calls:,} times for ways(60, ...); the uncached version needs 74,809 "
        "and a cached one about 500. Cache count with @functools.cache so each (amount, coins, i) is computed once."
    )
    # only reached when caching works, so a slow version never gets here
    assert ways(200, [1, 2, 5, 10, 20, 50, 100, 200]) == 73682, "ways(200, UK coins) is 73682."
    assert ways(500, [1, 2, 5, 10, 20, 50, 100, 200]) == 6295434, "ways(500, UK coins) is 6295434."


def test_second_call_is_free():
    clear()
    ways(60, [1, 2, 5, 10, 20, 50])
    _, calls = python_calls_in_solution(ways, 60, [1, 2, 5, 10, 20, 50])
    assert calls <= 2, (
        f"Asking the same question again ran {calls} Python calls. With the cache, it is one call of ways and a "
        "cache hit for count."
    )
