import pathlib
import random
import subprocess
import sys

from solution import can_partition

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Try every subset (only for short lists)."""
    total = sum(nums)
    if total % 2:
        return False
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        if 2 * s == total:
            return True
    return False


def bits_answer(nums):
    total = sum(nums)
    if total % 2:
        return False
    bits = 1
    for x in nums:
        bits |= bits << x
    return (bits >> (total // 2)) & 1 == 1


def test_chapter_examples():
    assert can_partition([1, 5, 11, 5]) is True, "[11] and [1, 5, 5] both sum to 11: expected True."
    assert can_partition([1, 2, 3, 5]) is False, "The total 11 is odd, so no equal split exists: expected False."
    assert can_partition([2, 2]) is True, "[2] and [2]: expected True."


def test_odd_total_and_single():
    assert can_partition([7]) is False, "One number cannot be split into two equal groups (total 7 is odd)."
    assert can_partition([4]) is False, (
        "[4]: the groups would be [4] and [] with sums 4 and 0. Half of 4 is 2, and no subset sums to 2.")
    assert can_partition([1, 1]) is True, "[1] and [1]: expected True."


def test_each_number_only_once():
    assert can_partition([1, 2, 5]) is False, (
        "[1, 2, 5]: half of 8 is 4, and no subset sums to 4. If you got True, your loop over s runs "
        "upwards and reuses 1 (1 + 1 + 2). Loop s from half DOWN to x.")
    assert can_partition([2, 3, 7]) is False, (
        "[2, 3, 7]: half of 12 is 6; 2 + 2 + 2 or 3 + 3 would reuse a number. Loop s downwards.")


def test_greedy_is_not_enough():
    assert can_partition([3, 3, 2, 2, 2]) is True, (
        "[3, 3] and [2, 2, 2] both sum to 6. Putting each number in the lighter pile gives 7 and 5: "
        "greedy is not safe, use subset sum with target 6.")


def test_random_against_brute_force():
    rng = random.Random(41)
    for _ in range(400):
        nums = [rng.randint(1, 12) for _ in range(rng.randint(1, 11))]
        want = brute(nums)
        got = can_partition(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (checked by trying every subset), got {got}. "
            "Is the total odd? Is f[0] True? Does the s loop go downwards?")


def run_big(code):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_big_input_is_fast():
    rng = random.Random(4141)
    cases = [[3] * 198 + [2], [rng.randint(1, 100) for _ in range(200)], list(range(1, 201))]
    want = [bits_answer(c) for c in cases]
    code = (
        "from solution import can_partition\n"
        f"cases = {cases!r}\n"
        "print(*[can_partition(c) for c in cases])\n"
    )
    r = run_big(code)
    assert r is not None, (
        "Time limit (10 s) on 200 numbers. Trying every subset is 2**200 calls: exponential: add a memo, "
        "or fill a table f[s] for s up to total // 2.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    got = r.stdout.split()
    assert got == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {got}. The first list (198 threes and a 2) has an even total "
        "596, but no subset sums to 298.")
