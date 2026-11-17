import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import min_rooms

HERE = Path(__file__).parent


def brute(intervals):
    """The largest number of meetings that are on at the moment one of them starts (a meeting is on from start up to, not including, end)."""
    best = 0
    for start, _ in intervals:
        best = max(best, sum(1 for s, e in intervals if s <= start < e))
    return best


def test_the_examples():
    assert min_rooms([(0, 30), (5, 10), (15, 20)]) == 2, "(0, 30) runs all the time; (5, 10) and (15, 20) share the second room."
    assert min_rooms([(7, 10), (2, 4)]) == 1, "the input is not sorted: sort by start time first."
    assert min_rooms([]) == 0, "no meetings: no rooms."


def test_touching_meetings_do_not_overlap():
    assert min_rooms([(1, 5), (5, 9)]) == 1, "a meeting that ends at 5 and one that starts at 5 can share a room: use <=, not <."
    assert min_rooms([(1, 3), (3, 5), (5, 7), (7, 9)]) == 1, "a chain of touching meetings needs one room."
    assert min_rooms([(0, 5), (5, 10), (5, 10)]) == 2, "two meetings start at 5 when the first ends: two rooms."


def test_identical_and_nested_meetings():
    assert min_rooms([(1, 4)] * 5) == 5, "five identical meetings overlap each other: five rooms."
    assert min_rooms([(0, 100), (10, 90), (20, 80), (30, 70)]) == 4, "nested meetings all overlap."


def test_one_meeting():
    assert min_rooms([(3, 4)]) == 1, "one meeting needs one room."


def test_meetings_given_as_lists():
    assert min_rooms([[0, 30], [5, 10], [15, 20]]) == 2, "meetings can be lists [start, end] too."


def test_the_input_is_not_changed():
    meetings = [(7, 10), (2, 4), (3, 9)]
    min_rooms(meetings)
    assert meetings == [(7, 10), (2, 4), (3, 9)], "your function changed the order of the caller's list (list.sort()?). Use sorted()."


def test_a_room_is_reused_in_the_order_of_ending():
    # Several rooms are busy at different times: the count must follow the real overlap, not the order of the input.
    assert min_rooms([(0, 10), (1, 3), (4, 8), (9, 12)]) == 2, "rooms: A (0-10), B (1-3 then 4-8 then 9-12): two rooms."
    assert min_rooms([(0, 10), (1, 5), (2, 6), (6, 7)]) == 3, "at time 2 three meetings are on: three rooms."


@pytest.mark.parametrize("seed", range(80))
def test_random_schedules(seed):
    rng = random.Random(seed)
    meetings = []
    for _ in range(rng.randint(0, 14)):
        s = rng.randint(0, 20)
        meetings.append((s, s + rng.randint(1, 8)))
    want = brute(meetings)
    got = min_rooms(list(meetings))
    assert got == want, (
        f"meetings = {meetings}: {want} rooms are needed, you returned {got}. "
        "Sort by start, keep the end times of busy rooms in a min-heap, reuse the room with the smallest end time when it is <= the new start.")


BIG = """
import random
from solution import min_rooms

def sweep(iv):
    events = sorted([(s, 1) for s, e in iv] + [(e, -1) for s, e in iv])
    now = best = 0
    for _, d in events:
        now += d
        best = max(best, now)
    return best

rng = random.Random(6)
cases = []
random_case = []
for _ in range(100000):
    s = rng.randint(0, 10**9 - 1)
    random_case.append((s, min(10**9, s + rng.randint(1, 3 * 10**6))))
cases.append(random_case)
cases.append([(i, 200000 + i) for i in range(100000)])          # every meeting overlaps every other
cases.append([(2 * i, 2 * i + 1) for i in range(100000)])       # no two meetings overlap
cases.append([(i, i + 1) for i in range(100000)])               # all touching: one room
rng.shuffle(cases[1]); rng.shuffle(cases[2])
print(" ".join("OK" if min_rooms(c) == sweep(c) else "WRONG" for c in cases))
"""


def test_one_hundred_thousand_meetings_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "100,000 meetings did not finish in 10 seconds. Checking every room (or every other meeting) for every "
            "meeting costs O(n^2) when many meetings overlap. Keep the end times in a min-heap: one heap operation per meeting.")
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    assert r.stdout.split() == ["OK"] * 4, (
        f"big cases (random, all overlapping, none overlapping, all touching) gave {r.stdout.strip()!r}; every case must be OK.")
