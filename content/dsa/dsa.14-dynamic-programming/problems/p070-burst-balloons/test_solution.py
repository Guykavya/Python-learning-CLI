import pathlib
import random
import subprocess
import sys

from solution import max_coins

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Try every order of bursting: n! orders, so tiny inputs only."""
    if not nums:
        return 0
    best = 0
    for i in range(len(nums)):
        left = nums[i - 1] if i > 0 else 1
        right = nums[i + 1] if i + 1 < len(nums) else 1
        best = max(best, left * nums[i] * right + brute(nums[:i] + nums[i + 1:]))
    return best


def test_examples():
    assert max_coins([3, 1, 5, 8]) == 167, (
        "Expected 167. Choose the LAST balloon k in each range: it bursts with neighbours a[i] and a[j], "
        "and the two sides are independent.")
    assert max_coins([1, 5]) == 10, "Expected 10: burst 1 first (1*1*5), then 5 (1*5*1)."


def test_small_rows():
    assert max_coins([]) == 0, "No balloons: 0 coins."
    assert max_coins([7]) == 7, "One balloon: both neighbours are missing, so 1 * 7 * 1 = 7. Pad with 1s."
    assert max_coins([0, 0]) == 0, "Zeros earn nothing."
    assert max_coins([2, 3]) == 9, "Burst 2 (1*2*3 = 6), then 3 (1*3*1 = 3): 9."


def test_does_not_change_the_input():
    nums = [3, 1, 5, 8]
    max_coins(nums)
    assert nums == [3, 1, 5, 8], "Do not change the caller's list: build a new padded list a = [1] + nums + [1]."


def test_random_against_every_order():
    rng = random.Random(70)
    for trial in range(250):
        size = rng.randint(0, 6) if trial < 240 else 8
        nums = [rng.randint(0, 9) for _ in range(size)]
        want = brute(nums)
        got = max_coins(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (every order tried), got {got}. f(i, j) = max over i < k < j of "
            "f(i, k) + f(k, j) + a[i] * a[k] * a[j], filled with short ranges first.")


def test_large_input_in_time():
    rng = random.Random(7000)
    nums = [rng.randint(0, 100) for _ in range(150)]
    code = (
        "import sys\n"
        "from solution import max_coins\n"
        "nums = [int(x) for x in sys.stdin.read().split()]\n"
        "print(max_coins(nums), max_coins([1] * 150))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, input=" ".join(map(str, nums)),
                           capture_output=True, text=True, timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 150 balloons. Trying orders (or a recursion without a memo) is exponential: "
        "add a memo on (i, j), or fill the table by gap (O(n^3)).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["44703190", "150"], (
        f"Expected 44703190 for the random row and 150 for 150 ones (every burst earns 1); got {r.stdout.split()}.")
