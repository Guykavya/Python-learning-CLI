import random
import statistics
import subprocess
import sys
from pathlib import Path

import pytest

from solution import MedianFinder

HERE = Path(__file__).parent


def feed(values):
    mf = MedianFinder()
    for v in values:
        mf.add(v)
    return mf


def test_the_example():
    mf = MedianFinder()
    got = []
    for x in (5, 2, 8, 1, 9, 3):
        mf.add(x)
        got.append(mf.median())
    assert got == [5, 3.5, 5, 3.5, 5, 4.0], (
        f"after 5, 2, 8, 1, 9, 3 the medians should be [5, 3.5, 5, 3.5, 5, 4.0], got {got}. "
        "Odd count: the top of the lower half. Even count: the average of the two tops.")


def test_one_number_is_its_own_median():
    for x in (7, -3, 0, 2.5):
        mf = feed([x])
        assert mf.median() == x, f"the only number is {x!r}, so the median is {x!r}, got {mf.median()!r}."


def test_empty_raises_value_error():
    mf = MedianFinder()
    with pytest.raises(ValueError):
        mf.median()


def test_odd_count_gives_the_number_itself():
    mf = feed([4])
    assert mf.median() == 4 and not isinstance(mf.median(), float), (
        "for an odd count return the middle number itself (4), not a float like 4.0.")


def test_even_count_gives_the_average_of_the_two_middle_numbers():
    assert feed([1, 2]).median() == 1.5, "median of 1, 2 is (1 + 2) / 2 = 1.5."
    assert feed([1, 4]).median() == 2.5, "median of 1, 4 is 2.5."
    assert feed([-3, 4]).median() == 0.5, "median of -3, 4 is 0.5 (negative numbers belong in the lower half)."
    assert feed([10, 2, 2, 10]).median() == 6, "median of 2, 2, 10, 10 is (2 + 10) / 2 = 6."


def test_all_equal_numbers():
    mf = feed([5] * 7)
    assert mf.median() == 5, "seven fives have median 5."
    mf.add(5)
    assert mf.median() == 5, "eight fives: the average of two fives is 5."


def test_ascending_and_descending_input():
    for order in (list(range(1, 201)), list(range(200, 0, -1))):
        mf = MedianFinder()
        seen = []
        for x in order:
            mf.add(x)
            seen.append(x)
            assert mf.median() == statistics.median(seen), (
                f"after adding {len(seen)} numbers in sorted order the median should be {statistics.median(seen)}, "
                f"got {mf.median()}. Check that new numbers that are bigger (or smaller) than everything move to the correct half.")


@pytest.mark.parametrize("seed", range(40))
def test_random_streams_match_statistics_median(seed):
    rng = random.Random(seed)
    mf = MedianFinder()
    seen = []
    for _ in range(rng.randint(1, 60)):
        x = rng.randint(-20, 20)
        mf.add(x)
        seen.append(x)
        expected = statistics.median(seen)
        assert mf.median() == expected, (
            f"after adding {seen} the median should be {expected}, got {mf.median()}. "
            "Check the sizes of the two halves and that the top of the lower half is never bigger than the top of the upper half.")


def test_floats():
    rng = random.Random(5)
    mf = MedianFinder()
    seen = []
    for _ in range(100):
        x = rng.uniform(-1, 1)
        mf.add(x)
        seen.append(x)
        assert mf.median() == pytest.approx(statistics.median(seen)), "floats are numbers too: same rule."


BIG = """
import random
from solution import MedianFinder
rng = random.Random(11)
mf = MedianFinder()
total = 0
for _ in range(100000):
    mf.add(rng.randint(-10**6, 10**6))
    total += mf.median()
print(total)
"""

BIG_CHECK = """
import random
rng = random.Random(11)
import heapq
low, high, total = [], [], 0
for _ in range(100000):
    x = rng.randint(-10**6, 10**6)
    heapq.heappush(low, -x)
    heapq.heappush(high, -heapq.heappop(low))
    if len(high) > len(low):
        heapq.heappush(low, -heapq.heappop(high))
    total += -low[0] if len(low) > len(high) else (-low[0] + high[0]) / 2
print(total)
"""


def run_code(code, seconds):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=seconds)
    except subprocess.TimeoutExpired:
        return None
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    return r.stdout.strip()


def test_one_hundred_thousand_numbers_in_time():
    got = run_code(BIG, 10)
    assert got is not None, (
        "100,000 adds, each followed by a median() call, did not finish in 10 seconds. Sorting (or scanning) all numbers "
        "on every call is too slow: keep two heaps, add in O(log n) and read the median from the tops in O(1).")
    want = run_code(BIG_CHECK, 30)
    assert got == want, f"the sum of the 100,000 medians should be {want}, got {got}."
