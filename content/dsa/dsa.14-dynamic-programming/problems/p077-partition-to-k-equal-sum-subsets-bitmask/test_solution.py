import pathlib
import random
import subprocess
import sys

from solution import can_split

HERE = pathlib.Path(__file__).parent


def brute(nums, k):
    """Give every number a group number 0..k-1, all k**n ways (small inputs only)."""
    total = sum(nums)
    if total % k:
        return False
    target = total // k
    sums = [0] * k

    def place(i):
        if i == len(nums):
            return all(s == target for s in sums)
        for g in range(k):
            sums[g] += nums[i]
            ok = place(i + 1)
            sums[g] -= nums[i]
            if ok:
                return True
        return False

    return place(0)


def test_examples():
    assert can_split([4, 3, 2, 3, 5, 2, 1], 4) is True, "Expected True: (5), (1, 4), (2, 3), (2, 3)."
    assert can_split([1, 2, 3, 4], 3) is False, "Expected False: the total 10 is not a multiple of 3."
    assert can_split([7], 1) is True, "One number, one group: True."


def test_sum_divisible_is_not_enough():
    got = can_split([2, 2, 2, 2, 3, 4, 5], 4)
    assert got is False, (
        "[2, 2, 2, 2, 3, 4, 5] sums to 20 = 4 * 5, but 4 needs a partner 1 that does not exist: expected False. "
        "The divisibility check alone is not enough.")


def test_number_bigger_than_target():
    assert can_split([12, 1, 1, 1, 1, 1, 1, 1, 1], 2) is False, (
        "Total 20, so each group needs 10, but 12 alone is already more than 10: expected False.")
    assert can_split([10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 2) is True, (
        "Total 20: (10) and the ten 1s. A number exactly equal to the target is a group on its own: True.")


def test_greedy_largest_first_fails():
    got = can_split([3, 3, 2, 2, 2, 2], 2)
    assert got is True, (
        "[3, 3, 2, 2, 2, 2] into 2 groups of 7: 3 + 2 + 2 twice. Expected True. Putting 3 + 3 together first "
        "(largest first, never undoing) gets stuck at 6: the DP must try every order.")


def test_k_one_and_k_n():
    assert can_split([5, 1, 9], 1) is True, "k = 1: the whole list is one group, always True."
    assert can_split([4, 4, 4], 3) is True, "k = n with equal numbers: every number alone, True."
    assert can_split([4, 4, 5], 3) is False, "k = n with different numbers: False."


def test_random_against_brute_force():
    rng = random.Random(7777)
    for _ in range(300):
        n = rng.randint(1, 8)
        nums = [rng.randint(1, 9) for _ in range(n)]
        k = rng.randint(1, min(n, 4))
        want = brute(nums, k)
        got = can_split(list(nums), k)
        assert got == want, (
            f"can_split({nums}, {k}): expected {want}, got {got}. State: the set of placed numbers; the "
            "current group's fill is sum(mask) % target; a number fits if fill + x <= target.")


def test_sixteen_numbers():
    code = (
        "from solution import can_split\n"
        "a = [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 10]\n"
        "b = [5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 3, 3, 3, 3, 3, 3]\n"
        "c = [16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]\n"
        "print(can_split(a, 4), can_split(b, 4), can_split(c, 4), can_split(c, 8))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 16 numbers: giving each number a group is 4**16 = 4.3 billion ways. "
        "The mask DP has only 2**16 = 65,536 states.")
    assert r.returncode == 0, "Your code crashed on 16 numbers:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True", "True", "True"], (
        "16 numbers: expected False (fifteen 6s and a 10 cannot make four groups of 25), True (5 + 5 + 3 + 3 "
        f"four times), True (1..16 into 4 groups of 34), True (8 pairs of 17); got {r.stdout.split()}.")
