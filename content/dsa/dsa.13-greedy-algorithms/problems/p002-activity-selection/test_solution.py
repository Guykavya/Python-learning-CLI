import random

from solution import max_activities


def brute(intervals):
    """Try every subset (small inputs only)."""
    n = len(intervals)
    best = 0
    for mask in range(1 << n):
        chosen = sorted(intervals[i] for i in range(n) if mask >> i & 1)
        if all(chosen[i][1] <= chosen[i + 1][0] for i in range(len(chosen) - 1)):
            best = max(best, len(chosen))
    return best


def test_chapter_example():
    events = [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9), (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]
    assert max_activities(events) == 4, (
        "The chapter's eleven events give 4: (1,4), (5,7), (8,11), (12,16). Sort by END time, then take each "
        "event whose start is >= the end of the last one taken.")


def test_touching_is_allowed():
    assert max_activities([(0, 3), (3, 6), (6, 9)]) == 3, (
        "Touching events do not overlap: (0,3) and (3,6) can both be held. Use `start >= last_end`, not `>`.")
    assert max_activities([(5, 7), (1, 5), (7, 7)]) == 3, (
        "(1,5), (5,7) and the empty event (7,7) all fit end to start. Compare with `>=`.")


def test_wrong_rules_are_caught():
    assert max_activities([(0, 10), (1, 2), (3, 4), (5, 6)]) == 3, (
        "Got fewer than 3: are you sorting by START? The long event (0,10) starts first but blocks three short ones.")
    assert max_activities([(0, 5), (4, 7), (6, 10)]) == 2, (
        "Got 1: are you sorting by LENGTH? The short event (4,7) overlaps both others; (0,5) and (6,10) fit together.")


def test_unsorted_and_edge_cases():
    assert max_activities([]) == 0, "No requests: 0 events."
    assert max_activities([(2, 3)]) == 1, "One request: 1 event."
    assert max_activities([(1, 2), (1, 2), (1, 2)]) == 1, "Three copies of the same event: only one can be held."
    assert max_activities([[6, 9], [0, 3], [3, 6]]) == 3, (
        "The input is not sorted, and pairs may be lists. Sort a copy by end time first.")


def test_input_not_changed():
    data = [(5, 9), (1, 4), (3, 5)]
    copy = list(data)
    max_activities(data)
    assert data == copy, "Do not sort the caller's list in place: use sorted(...), which returns a new list."


def test_random_against_brute_force():
    rng = random.Random(2)
    for _ in range(500):
        n = rng.randint(0, 9)
        intervals = []
        for _ in range(n):
            s = rng.randint(0, 12)
            intervals.append((s, s + rng.randint(1, 5)))
        expected = brute(intervals)
        got = max_activities(list(intervals))
        assert got == expected, (
            f"intervals={intervals}: the best is {expected} events, you returned {got}. Sort by end time, take an "
            "event when start >= last_end (touching is fine), and count every event you take.")


def test_large_input_is_fast():
    n = 100_000
    intervals = [(i, i + 2) for i in range(n)]
    assert max_activities(intervals) == n // 2, (
        "100,000 events (i, i+2): every second one fits, so 50,000. If this is slow, avoid nested loops: "
        "one sort and one pass are enough.")
