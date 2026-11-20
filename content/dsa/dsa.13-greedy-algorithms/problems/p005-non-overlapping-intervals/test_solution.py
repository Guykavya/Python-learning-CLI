import random

from solution import min_removals


def brute(intervals):
    """Fewest removals = n - largest non-overlapping subset (every subset tried)."""
    n = len(intervals)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(intervals[i] for i in range(n) if mask >> i & 1)
        if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return n - best


def test_chapter_examples():
    assert min_removals([(1, 2), (2, 3), (3, 4), (1, 3)]) == 1, (
        "(1,3) overlaps (1,2) and (2,3); removing it alone leaves a valid calendar: 1 removal.")
    assert min_removals([(1, 2), (1, 2), (1, 2)]) == 2, "Three copies of one interval: keep one, remove two."
    assert min_removals([(1, 2), (2, 3)]) == 0, (
        "Touching intervals do not overlap: (1,2) and (2,3) both stay. Use `start >= last_end`.")


def test_remove_the_one_that_ends_later():
    assert min_removals([(1, 100), (11, 22), (1, 11), (2, 12)]) == 2, (
        "Keep (1,11) and (11,22), remove 2. If you got 3, you probably keep the interval that STARTS first "
        "(1,100); sort by END time instead.")
    assert min_removals([(0, 10), (1, 2), (3, 4), (5, 6)]) == 1, (
        "Remove only the long (0,10). When two intervals clash, drop the one that ends later.")


def test_edge_cases():
    assert min_removals([]) == 0, "No intervals: nothing to remove."
    assert min_removals([(5, 7)]) == 0, "One interval never overlaps anything."
    assert min_removals([[3, 4], [1, 3], [2, 4]]) == 1, "Unsorted input given as lists: remove (2,4)."


def test_input_not_changed():
    data = [(3, 4), (1, 3), (2, 4)]
    copy = list(data)
    min_removals(data)
    assert data == copy, "Do not sort the caller's list in place; use sorted(...)."


def test_random_against_brute_force():
    rng = random.Random(5)
    for _ in range(500):
        n = rng.randint(0, 9)
        intervals = []
        for _ in range(n):
            s = rng.randint(-5, 10)
            intervals.append((s, s + rng.randint(1, 6)))
        expected = brute(intervals)
        got = min_removals(list(intervals))
        assert got == expected, (
            f"intervals={intervals}: the fewest removals is {expected}, you returned {got}. Keep the most "
            "intervals with the earliest-finish sweep, then return n - kept.")


def test_large_input_is_fast():
    intervals = [(i, i + 2) for i in range(100_000)]
    assert min_removals(intervals) == 50_000, (
        "100,000 intervals (i, i+2): keep every second one, remove 50,000. One sort and one pass are enough.")
