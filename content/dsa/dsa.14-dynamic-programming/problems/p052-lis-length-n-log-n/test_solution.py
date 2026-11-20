import pathlib
import random
import subprocess
import sys

from solution import lis_len

HERE = pathlib.Path(__file__).parent


def quadratic(nums):
    if not nums:
        return 0
    f = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
    return max(f)


def test_chapter_examples():
    assert lis_len([10, 9, 2, 5, 3, 7, 101, 18]) == 4, "Expected 4 (tails ends as [2, 3, 7, 18])."
    assert lis_len([4, 10, 4, 3, 8, 9]) == 3, "Expected 3, for example 4, 8, 9."


def test_equal_values():
    assert lis_len([2, 2, 3, 3, 1]) == 2, (
        "Strictly increasing: 2, 3. If you got 4, you used bisect_right (that counts non-decreasing). "
        "Use bisect_left so an equal number replaces instead of appending.")
    assert lis_len([5] * 10) == 1, "Ten equal numbers: 1."


def test_replace_step():
    assert lis_len([10, 1, 2, 3]) == 3, (
        "Expected 3 (1, 2, 3). If you got 1, you never replace: 1 must replace 10 in tails.")
    assert lis_len([1, 5, 2, 3]) == 3, (
        "Expected 3 (1, 2, 3). 2 must replace 5, the first tails value >= 2, not the last one.")


def test_empty_and_single():
    assert lis_len([]) == 0, "Empty list: 0."
    assert lis_len([-3]) == 1, "One number: 1."


def test_random_against_quadratic_dp():
    rng = random.Random(52)
    for _ in range(400):
        nums = [rng.randint(-4, 9) for _ in range(rng.randint(0, 30))]
        want = quadratic(nums)
        got = lis_len(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (O(n^2) DP), got {got}. "
            "bisect_left, append when k == len(tails), else replace tails[k].")


def test_big_input_is_n_log_n():
    rng = random.Random(5252)
    big = [rng.randint(1, 10**9) for _ in range(10**5)]
    small_range = [rng.randint(1, 50) for _ in range(10**5)]
    code = (
        "import random\n"
        "from solution import lis_len\n"
        "rng = random.Random(5252)\n"
        "big = [rng.randint(1, 10**9) for _ in range(10**5)]\n"
        "small_range = [rng.randint(1, 50) for _ in range(10**5)]\n"
        "print(lis_len(big), lis_len(small_range), lis_len(list(range(10**5))), lis_len([7] * 10**5))\n"
    )
    from bisect import bisect_left
    want = []
    for nums in (big, small_range):
        tails = []
        for x in nums:
            k = bisect_left(tails, x)
            if k == len(tails):
                tails.append(x)
            else:
                tails[k] = x
        want.append(len(tails))
    want += [10**5, 1]
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100,000 numbers. The O(n^2) DP needs billions of steps; use the tails list "
        "with bisect_left (one binary search per number).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}. The second list has values 1..50 only, "
        "so its LIS is at most 50; the last is 100,000 equal numbers: 1.")
