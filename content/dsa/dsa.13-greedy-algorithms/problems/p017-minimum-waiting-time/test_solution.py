import random
from itertools import permutations

from solution import min_total_waiting


def total_waiting(order):
    wait = elapsed = 0
    for d in order:
        wait += elapsed
        elapsed += d
    return wait


def brute(durations):
    if not durations:
        return 0
    return min(total_waiting(p) for p in permutations(durations))


def test_chapter_examples():
    assert min_total_waiting([6, 8, 7, 3]) == 28, (
        "Best order 3, 6, 7, 8: waits 0 + 3 + 9 + 16 = 28. If you got 41 you used the given order; sort first. "
        "If you got 44, you sorted longest first.")
    assert min_total_waiting([2, 1, 3]) == 4, "Order 1, 2, 3: waits 0 + 1 + 3 = 4."


def test_waiting_not_finishing():
    assert min_total_waiting([1, 2]) == 1, (
        "Order 1, 2: the first job waits 0, the second waits 1. Total 1. If you got 4 you summed FINISH times "
        "(1 + 3): add `elapsed` to the total before adding the job's own duration.")


def test_edge_cases():
    assert min_total_waiting([]) == 0, "No jobs: total waiting 0."
    assert min_total_waiting([5]) == 0, "A single job starts at once and waits 0."
    assert min_total_waiting([0, 0, 4]) == 0, "Zero-length jobs go first; the 4-minute job then waits 0."
    assert min_total_waiting([3, 3, 3]) == 9, "Equal jobs: waits 0 + 3 + 6 = 9."


def test_input_not_changed():
    data = [6, 8, 7, 3]
    min_total_waiting(data)
    assert data == [6, 8, 7, 3], "Do not sort the caller's list in place; use sorted(...)."


def test_random_against_all_orders():
    rng = random.Random(17)
    for _ in range(300):
        n = rng.randint(0, 7)
        durations = [rng.randint(0, 20) for _ in range(n)]
        expected = brute(durations)
        got = min_total_waiting(list(durations))
        assert got == expected, (
            f"durations={durations}: the best total waiting time is {expected}, you returned {got}. Sort shortest "
            "first; each job waits for the sum of the jobs before it.")


def test_large_input_is_fast():
    durations = list(range(100_000, 0, -1))
    n = 100_000
    expected = sum((n - k) * k for k in range(1, n + 1))
    assert min_total_waiting(durations) == expected, (
        "100,000 jobs: sort once and keep a running total; summing the earlier jobs again for every job is O(n^2).")
