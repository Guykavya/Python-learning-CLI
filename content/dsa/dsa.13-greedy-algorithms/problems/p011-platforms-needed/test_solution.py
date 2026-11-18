import random

from solution import min_platforms


def brute(arrivals, departures):
    """O(n^2): at each arrival time, count the trains standing in the station (a <= t < d)."""
    best = 0
    for t in arrivals:
        here = sum(1 for a, d in zip(arrivals, departures) if a <= t < d)
        best = max(best, here)
    return best


def test_chapter_example():
    arrivals = [900, 940, 950, 1100, 1500, 1800]
    departures = [910, 1200, 1120, 1130, 1900, 2000]
    assert min_platforms(arrivals, departures) == 3, (
        "The chapter's timetable needs 3 platforms (peak at 1100). Sort arrivals and departures separately and "
        "walk through both in time order, counting trains in the station.")


def test_same_time_rule():
    assert min_platforms([900, 1000], [1000, 1100]) == 1, (
        "A train leaves at 1000 and another arrives at 1000: the departure goes first, so 1 platform is enough. "
        "When the times are equal, process the DEPARTURE first (arr[i] < dep[j] for an arrival, not <=).")
    assert min_platforms([100, 200, 300], [200, 300, 400]) == 1, "Each train arrives as the previous one leaves: 1."


def test_departures_not_sorted_like_arrivals():
    assert min_platforms([900, 905, 910], [1000, 920, 915]) == 3, (
        "All three trains are in the station at 910. The departures are not in the same order as the arrivals; "
        "sort the two lists separately.")
    assert min_platforms([1000, 900], [1100, 950]) == 1, (
        "Unsorted input: 900-950 and 1000-1100 never meet, so 1 platform. Did you sort the arrivals?")


def test_edge_cases():
    assert min_platforms([], []) == 0, "No trains: no platforms."
    assert min_platforms([500], [600]) == 1, "One train needs one platform."
    assert min_platforms([700, 700, 700], [800, 900, 750]) == 3, "Three trains arrive at the same minute: 3."


def test_input_not_changed():
    a, d = [950, 900], [1000, 910]
    min_platforms(a, d)
    assert a == [950, 900] and d == [1000, 910], "Do not sort the caller's lists in place; use sorted(...)."


def test_random_against_brute_force():
    rng = random.Random(11)
    for _ in range(800):
        n = rng.randint(0, 9)
        arrivals, departures = [], []
        for _ in range(n):
            a = rng.randint(0, 20)
            arrivals.append(a)
            departures.append(a + rng.randint(1, 6))
        expected = brute(arrivals, departures)
        got = min_platforms(list(arrivals), list(departures))
        assert got == expected, (
            f"arrivals={arrivals}, departures={departures}: expected {expected}, got {got}. On equal times "
            "process the departure first; the answer is the HIGHEST count seen, not the final count.")


def test_large_input_is_fast():
    arrivals = list(range(0, 300_000, 3))
    departures = [a + 7 for a in arrivals]
    assert min_platforms(arrivals, departures) == 3, (
        "100,000 trains, each staying 7 minutes, one every 3 minutes: 3 platforms. Use two sorts and one walk.")
