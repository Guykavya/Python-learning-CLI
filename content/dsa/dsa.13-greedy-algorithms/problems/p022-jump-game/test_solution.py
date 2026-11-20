import pathlib
import random
import subprocess
import sys

from solution import can_jump

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Mark every index reachable, one jump at a time (slow but obviously right)."""
    reach = [False] * len(nums)
    reach[0] = True
    for i in range(len(nums)):
        if reach[i]:
            for j in range(i + 1, min(len(nums), i + nums[i] + 1)):
                reach[j] = True
    return reach[-1]


def test_chapter_examples():
    assert can_jump([2, 3, 1, 1, 4]) is True, "[2, 3, 1, 1, 4] is reachable (0 -> 1 -> 4)."
    assert can_jump([3, 2, 1, 0, 4]) is False, (
        "[3, 2, 1, 0, 4]: farthest stays 3 for indices 0..3, then index 4 > 3: stuck on the zero at index 3.")


def test_single_element():
    assert can_jump([0]) is True, "One element: you start on the last index, so True even though it is 0."
    assert can_jump([5]) is True, "One element: True."


def test_zeros_can_be_jumped_over():
    assert can_jump([2, 0, 0]) is True, (
        "Jump 2 from index 0 lands on the last index. A zero is only a wall if farthest stops on it; "
        "the last index being 0 does not matter.")
    assert can_jump([1, 0, 1]) is False, "Index 1 is a 0 and nothing jumps past it."


def test_keep_the_maximum():
    assert can_jump([3, 1, 0, 0]) is True, (
        "Index 0 already reaches index 3. Use farthest = max(farthest, i + nums[i]); a short jump later must "
        "not make you forget an earlier long one.")
    assert can_jump([4, 1, 1, 0, 0, 1]) is False, "Index 0 reaches index 4 at most, and index 4 is a 0."


def test_longest_jump_is_not_always_best():
    assert can_jump([2, 3, 0, 1]) is True, (
        "Jumping as far as possible from index 0 lands on the 0 at index 2, but jumping 1 to index 1 and then 2 "
        "reaches the end. Do not pick landing places; track the farthest reachable index.")


def test_random_against_brute_force():
    rng = random.Random(22)
    for _ in range(1000):
        nums = [rng.randint(0, 3) for _ in range(rng.randint(1, 9))]
        want = brute(nums)
        got = can_jump(list(nums))
        assert got is want, (
            f"nums={nums}: expected {want}, got {got!r}. Keep farthest = max(farthest, i + nums[i]) and stop "
            "when i > farthest. Return True or False.")


def test_large_input():
    code = (
        "from solution import can_jump\n"
        "n = 10**5\n"
        "print(can_jump([n] * n), can_jump([1] * (n - 2) + [0, 0]))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100,000 elements of value 100,000. Marking every index each jump can reach is "
        "O(n * jump); keep one number, farthest, and make one pass.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "False"], (
        f"Large inputs: expected True (big jumps) and False (ones ending in 0, 0); got {r.stdout.split()}.")
