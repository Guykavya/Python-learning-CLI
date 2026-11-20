import random

from solution import assign_cookies


def brute(greed, sizes):
    """Try every way to give the children cookies (each child: no cookie, or any unused cookie that is big enough)."""
    best = 0

    def go(i, used, happy):
        nonlocal best
        if i == len(greed):
            best = max(best, happy)
            return
        go(i + 1, used, happy)
        for j in range(len(sizes)):
            if j not in used and sizes[j] >= greed[i]:
                go(i + 1, used | {j}, happy + 1)

    go(0, frozenset(), 0)
    return best


def test_chapter_examples():
    assert assign_cookies([1, 2, 3], [1, 1]) == 1, "Only greed 1 can be satisfied: both cookies have size 1."
    assert assign_cookies([1, 2], [1, 2, 3]) == 2, "Both children can be happy."
    assert assign_cookies([10, 9, 8, 7], [5, 6, 7, 8]) == 2, (
        "Expected 2: cookies 7 and 8 satisfy greed 7 and 8. The lists are not sorted: sort BOTH before the pass.")


def test_equal_size_is_enough():
    assert assign_cookies([2], [2]) == 1, "A cookie of size equal to the greed makes the child happy: use >=, not >."


def test_empty_lists():
    assert assign_cookies([], [1, 2]) == 0, "No children: 0."
    assert assign_cookies([1, 2], []) == 0, "No cookies: 0."


def test_big_cookie_not_wasted():
    assert assign_cookies([1, 5], [10, 1]) == 2, (
        "Give the size-1 cookie to the greed-1 child and the size-10 cookie to the greed-5 child. "
        "Giving the biggest cookie to the least greedy child wastes it.")


def test_each_cookie_used_once():
    assert assign_cookies([1, 1, 1], [5]) == 1, "One cookie can make only one child happy."
    assert assign_cookies([3], [1, 1, 1, 1]) == 0, "Small cookies cannot be combined: a child gets one cookie."


def test_inputs_not_changed():
    g, s = [3, 1, 2], [2, 1]
    assign_cookies(g, s)
    assert g == [3, 1, 2] and s == [2, 1], "Do not sort the caller's lists in place; use sorted(...)."


def test_random_against_brute_force():
    rng = random.Random(21)
    for _ in range(400):
        greed = [rng.randint(1, 6) for _ in range(rng.randint(0, 5))]
        sizes = [rng.randint(1, 6) for _ in range(rng.randint(0, 5))]
        want = brute(greed, sizes)
        got = assign_cookies(list(greed), list(sizes))
        assert got == want, (
            f"greed={greed}, sizes={sizes}: expected {want} happy children (every assignment tried), got {got}. "
            "Sort both lists; give each cookie, smallest first, to the least greedy child still unhappy.")


def test_large_input():
    rng = random.Random(2121)
    greed = [rng.randint(1, 10**9) for _ in range(3 * 10**4)]
    sizes = [rng.randint(1, 10**9) for _ in range(3 * 10**4)]
    g, s = sorted(greed), sorted(sizes)
    child = 0
    for c in s:
        if child < len(g) and c >= g[child]:
            child += 1
    assert assign_cookies(greed, sizes) == child, "30,000 children and cookies: wrong count (or too slow)."
