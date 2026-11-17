import random
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import pytest

from solution import connect_sticks

HERE = Path(__file__).parent


@lru_cache(maxsize=None)
def best(sticks):
    """The cheapest cost by trying every pair at every step (only for a few sticks)."""
    if len(sticks) <= 1:
        return 0
    answer = None
    for i in range(len(sticks)):
        for j in range(i + 1, len(sticks)):
            rest = [s for t, s in enumerate(sticks) if t != i and t != j]
            joined = sticks[i] + sticks[j]
            cost = joined + best(tuple(sorted(rest + [joined])))
            if answer is None or cost < answer:
                answer = cost
    return answer


def test_the_examples():
    assert connect_sticks([2, 4, 3]) == 14, "join 2+3 (5), then 5+4 (9): 14. Joining 4+3 first costs 16."
    assert connect_sticks([1, 8, 3, 5]) == 30, "1+3=4, 4+5=9, 9+8=17: 4 + 9 + 17 = 30."


def test_nothing_to_join():
    assert connect_sticks([]) == 0, "no sticks: cost 0."
    assert connect_sticks([5]) == 0, "one stick is already one stick: cost 0, not 5."


def test_two_sticks():
    assert connect_sticks([3, 4]) == 7, "one join of 3 and 4 costs 7."


def test_equal_sticks():
    assert connect_sticks([1, 1, 1, 1]) == 8, (
        "(1+1) + (1+1) + (2+2) = 8. Joining in a chain (1+1, 2+1, 3+1) would cost 9: the new stick must go back into the heap.")
    assert connect_sticks([5, 5, 5]) == 25, "5+5 = 10, then 10+5 = 15: 25."


def test_the_greedy_order_matters():
    assert connect_sticks([1, 2, 3, 4, 5]) == 33, "1+2=3, 3+3=6, 4+5=9, 6+9=15: 3 + 6 + 9 + 15 = 33."
    assert connect_sticks([10, 1, 1]) == 14, "1+1 = 2 first, then 2+10 = 12: 14. Joining 10 early costs more."


def test_the_input_is_not_changed():
    sticks = [9, 1, 7, 3]
    connect_sticks(sticks)
    assert sticks == [9, 1, 7, 3], "your function changed the caller's list (heapify on the input?). Work on a copy."


@pytest.mark.parametrize("seed", range(100))
def test_random_small_inputs_against_the_brute_force(seed):
    rng = random.Random(seed)
    sticks = [rng.randint(1, 12) for _ in range(rng.randint(0, 6))]
    want = best(tuple(sorted(sticks)))
    got = connect_sticks(list(sticks))
    assert got == want, (
        f"sticks = {sticks}: the cheapest total is {want}, you returned {got}. "
        "Always join the two SHORTEST sticks, and put the new stick back before the next round.")


BIG = """
from solution import connect_sticks
print(connect_sticks([1] * 65536), connect_sticks([3] * 32768))
"""


def test_many_sticks_in_time():
    try:
        r = subprocess.run([sys.executable, "-c", BIG], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail(
            "65,536 sticks did not finish in 10 seconds. Sorting the list again after every join costs O(n log n) per "
            "round. A heap gives the two shortest sticks in O(log n).")
    assert r.returncode == 0, "your code crashed on the big case:\n" + r.stderr[-600:]
    # 2**16 sticks of length 1: every stick is paid 16 times; 2**15 sticks of length 3: 3 * 2**15 * 15
    assert r.stdout.split() == ["1048576", "1474560"], (
        f"65,536 sticks of length 1 cost 65536 * 16 = 1048576 and 32,768 sticks of length 3 cost 3 * 32768 * 15 = 1474560 "
        f"(each stick is paid once per level of the join tree). Got {r.stdout.strip()!r}.")
