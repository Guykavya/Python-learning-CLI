import random
import time

from solution import top_k_each_day


def original(events, k):
    """The slow version from the problem, used as the yardstick."""
    result = {}
    for day, score in events:
        scores = sorted([s for d, s in events if d == day], reverse=True)
        result[day] = scores[:k]
    return result


EXAMPLE = [("mon", 5), ("tue", 7), ("mon", 9), ("mon", 1), ("tue", 7), ("mon", 9)]


def test_example():
    assert top_k_each_day(EXAMPLE, 2) == {"mon": [9, 9], "tue": [7, 7]}, "Top 2 per day, highest first, equal scores both kept."


def test_k_zero_and_large():
    assert top_k_each_day(EXAMPLE, 0) == {"mon": [], "tue": []}, "k = 0 keeps every day with an empty list."
    assert top_k_each_day(EXAMPLE, 10) == {"mon": [9, 9, 5, 1], "tue": [7, 7]}, "If a day has fewer than k scores, return all of them, sorted high to low."


def test_empty():
    assert top_k_each_day([], 3) == {}, "No events gives an empty dict."


def test_day_order_is_first_seen():
    got = top_k_each_day([("b", 1), ("a", 2), ("b", 3), ("c", 0)], 1)
    assert list(got) == ["b", "a", "c"], f"Days must be in the order they first appear, got {list(got)}. Do not sort the days."


def test_input_not_changed():
    events = list(EXAMPLE)
    top_k_each_day(events, 2)
    assert events == EXAMPLE, "Do not sort or change the events list itself."


def test_matches_original_on_random_input():
    rng = random.Random(7)
    events = [(rng.choice("abcdefg"), rng.randint(-50, 50)) for _ in range(300)]
    for k in (0, 1, 3, 100):
        assert top_k_each_day(events, k) == original(events, k), f"Different result from the original for k={k}."


def best_of(fn, events, k, times=5):
    best = float("inf")
    for _ in range(times):
        start = time.perf_counter()
        fn(events, k)
        best = min(best, time.perf_counter() - start)
    return best


def check_speed(events, k, what):
    start = time.perf_counter()
    expected = original(events, k)          # the slow yardstick runs once (about 0.1 to 0.3 s)
    slow = time.perf_counter() - start
    assert top_k_each_day(events, k) == expected, "Wrong result on the big input; fix correctness first."
    fast = best_of(top_k_each_day, events, k)
    ratio = slow / max(fast, 1e-9)
    assert ratio >= 5, (
        f"{what}: your version is only {ratio:.1f}x faster than the original (needs 5x; a one-pass grouping is "
        "hundreds of times faster). Look for work repeated per event: scanning all events again, or calling "
        "sorted() inside the loop over events."
    )


def test_speed_many_days():
    rng = random.Random(20)
    events = [(f"2025-01-{rng.randint(1, 20):02d}", rng.randint(0, 10_000)) for _ in range(2000)]
    check_speed(events, 5, "2000 events over 20 days")


def test_speed_one_busy_day():
    rng = random.Random(21)
    events = [("2025-01-01", rng.randint(0, 10_000)) for _ in range(1500)]
    check_speed(events, 5, "1500 events on one busy day (sorting the day's growing list for every event)")
