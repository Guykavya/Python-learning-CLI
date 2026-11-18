import random

from solution import can_attend_all


def brute(meetings):
    """Check every pair with the half-open overlap test."""
    for i in range(len(meetings)):
        for j in range(i + 1, len(meetings)):
            a, b = meetings[i], meetings[j]
            if a[0] < b[1] and b[0] < a[1]:
                return False
    return True


def test_chapter_examples():
    assert can_attend_all([(0, 30), (5, 10), (15, 20)]) is False, (
        "(0,30) overlaps both other meetings. Sort by start and compare each meeting's end with the next start.")
    assert can_attend_all([(7, 10), (2, 4)]) is True, (
        "(2,4) then (7,10) do not overlap. The input is unsorted: sort before comparing neighbours.")


def test_touching_is_fine():
    assert can_attend_all([(1, 5), (5, 8)]) is True, (
        "Touching meetings (end 5, start 5) can both be attended: a clash is end > next start, not end >= next start.")
    assert can_attend_all([(5, 8), (1, 5), (8, 9)]) is True, "Three meetings touching end to start: True."


def test_clash_not_between_input_neighbours():
    assert can_attend_all([(1, 3), (10, 12), (2, 4)]) is False, (
        "(1,3) and (2,4) overlap, but they are not next to each other in the input. Sort first.")


def test_small_cases():
    assert can_attend_all([]) is True, "No meetings: nothing can clash."
    assert can_attend_all([(3, 4)]) is True, "One meeting can always be attended."
    assert can_attend_all([(1, 4), (1, 4)]) is False, "Two copies of the same meeting clash."
    assert can_attend_all([[4, 6], [1, 2], [5, 7]]) is False, "Meetings given as lists: (4,6) and (5,7) clash."


def test_input_not_changed():
    data = [(7, 10), (2, 4)]
    can_attend_all(data)
    assert data == [(7, 10), (2, 4)], "Do not sort the caller's list in place; use sorted(...)."


def test_random_against_all_pairs():
    rng = random.Random(9)
    for _ in range(800):
        n = rng.randint(0, 7)
        meetings = []
        for _ in range(n):
            s = rng.randint(0, 25)
            meetings.append((s, s + rng.randint(1, 5)))
        expected = brute(meetings)
        got = can_attend_all(list(meetings))
        assert got is expected, (
            f"meetings={meetings}: expected {expected}, got {got}. Sort by start; a clash is "
            "end > next start (touching is fine). Return True or False.")


def test_large_input_is_fast():
    meetings = [(2 * i, 2 * i + 2) for i in range(100_000)]
    assert can_attend_all(meetings) is True, "100,000 touching meetings: True. Sort once, then one pass."
    meetings.append((5, 6))
    assert can_attend_all(meetings) is False, "Adding (5,6) inside (4,6) makes a clash."
