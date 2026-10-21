from solution import make_cached


def test_example():
    calls = []
    def slow_add(a, b):
        calls.append((a, b))
        return a + b
    add, stats = make_cached(slow_add)
    assert add(2, 3) == 5
    assert add(2, 3) == 5
    assert add(3, 2) == 5
    assert calls == [(2, 3), (3, 2)], f"func should run once per distinct argument tuple; it ran for {calls}."
    assert stats() == {"hits": 1, "misses": 2}


def test_falsy_results_are_cached():
    calls = []
    def zero(x):
        calls.append(x)
        return 0
    z, stats = make_cached(zero)
    z(1); z(1); z(1)
    assert calls == [1], (
        "A cached result of 0 was recomputed. Test `args in cache`, not the truthiness of the stored value.")
    assert stats() == {"hits": 2, "misses": 1}


def test_none_result_cached():
    calls = []
    def nothing():
        calls.append(1)
    n, _ = make_cached(nothing)
    assert n() is None and n() is None
    assert calls == [1]


def test_separate_caches():
    f1, s1 = make_cached(lambda x: x * 2)
    f2, s2 = make_cached(lambda x: x * 3)
    assert f1(5) == 10 and f2(5) == 15, "Each make_cached call needs its own cache."
    assert s1() == {"hits": 0, "misses": 1} and s2() == {"hits": 0, "misses": 1}


def test_stats_is_a_copy():
    f, stats = make_cached(abs)
    f(-1)
    snapshot = stats()
    snapshot["hits"] = 99
    assert stats() == {"hits": 0, "misses": 1}, "stats() must return a new dict each time."


def test_initial_stats():
    _, stats = make_cached(abs)
    assert stats() == {"hits": 0, "misses": 0}
