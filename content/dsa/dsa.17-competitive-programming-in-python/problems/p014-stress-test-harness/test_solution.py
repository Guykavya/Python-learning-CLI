from solution import stress


def kadane_bug(a):
    best = cur = 0
    for x in a:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


def kadane_ok(a):
    best = cur = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


def brute(a):
    n = len(a)
    return max(sum(a[i:j]) for i in range(n) for j in range(i + 1, n + 1))


def gen(rng):
    return ([rng.randint(-5, 5) for _ in range(rng.randint(1, 5))],)


def test_finds_the_planted_bug():
    res = stress(kadane_bug, brute, gen)
    assert res is not None, "The buggy Kadane fails on lists of negative numbers; 1000 trials must find one."
    case, a, b = res
    assert a == kadane_bug(*case) and b == brute(*case) and a != b, (
        "Return (case, fast_result, brute_result) where the two results really differ on that case.")
    assert all(x < 0 for x in case[0]) or max(case[0]) <= 0, "A failing case must have no positive element."


def test_correct_solution_returns_none():
    assert stress(kadane_ok, brute, gen, trials=300) is None, "No difference exists: return None."


def test_same_seed_same_case_and_different_trials_count():
    r1 = stress(kadane_bug, brute, gen, seed=7)
    r2 = stress(kadane_bug, brute, gen, seed=7)
    assert r1 == r2, "The same seed must give the same sequence of cases: create Random(seed) once, outside the loop."


def test_inputs_are_copied():
    def weighted(a):
        return sum(i * x for i, x in enumerate(a))

    def fast_mutating(a):
        r = weighted(a)
        a.reverse()          # changes the argument in place
        return r

    def g(rng):
        return ([rng.randint(0, 9) for _ in range(rng.randint(2, 6))],)

    assert stress(fast_mutating, weighted, g, trials=200) is None, (
        "fast reverses its argument in place. Give each function its own copy.deepcopy(case).")

    # the returned case is the original one, not the mutated one
    def fast_wrong_and_mutating(a):
        a.append(99)
        return 0

    res = stress(fast_wrong_and_mutating, lambda a: 1, g, trials=5)
    assert res is not None and 99 not in res[0][0], "Return the original case, not the copy that fast changed."


def test_stops_at_first_difference_and_counts_trials():
    calls = []

    def counting_gen(rng):
        calls.append(1)
        return (rng.randint(0, 3),)

    assert stress(lambda x: x, lambda x: x, counting_gen, trials=40) is None
    assert len(calls) == 40, f"gen must be called once per trial: expected 40 calls, got {len(calls)}."
    calls.clear()
    res = stress(lambda x: 0, lambda x: x, counting_gen, trials=40)
    assert res is not None and len(calls) < 40, "Stop at the first difference: do not keep generating cases."


def test_exceptions_are_results():
    def fast(a):
        return a[0]            # IndexError on the empty list

    def brute_ok(a):
        return a[0] if a else None

    def g(rng):
        return ([rng.randint(1, 5) for _ in range(rng.randint(0, 3))],)

    res = stress(fast, brute_ok, g, trials=200)
    assert res is not None, "fast raises IndexError on an empty list while brute returns None: that is a difference."
    case, a, b = res
    assert case[0] == [] and isinstance(a, IndexError) and b is None, (
        "Return the exception object as the result of the function that raised.")
    both = stress(fast, fast, g, trials=100)
    assert both is None, "Two exceptions of the same type count as equal."
