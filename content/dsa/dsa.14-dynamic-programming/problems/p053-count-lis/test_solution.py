import pathlib
import random
import subprocess
import sys

from solution import count_lis

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Count every longest increasing subsequence by positions (only for short lists)."""
    n = len(nums)
    best, count = 0, 0
    for mask in range(1, 1 << n):
        picked = [nums[i] for i in range(n) if mask >> i & 1]
        if all(picked[k] < picked[k + 1] for k in range(len(picked) - 1)):
            if len(picked) > best:
                best, count = len(picked), 1
            elif len(picked) == best:
                count += 1
    return count


def pairs(nums):
    n = len(nums)
    if n == 0:
        return 0
    f, c = [1] * n, [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if f[j] + 1 > f[i]:
                    f[i], c[i] = f[j] + 1, c[j]
                elif f[j] + 1 == f[i]:
                    c[i] += c[j]
    m = max(f)
    return sum(c[i] for i in range(n) if f[i] == m)


def test_examples():
    assert count_lis([1, 3, 5, 4, 7]) == 2, (
        "Expected 2: 1,3,5,7 and 1,3,4,7. If you got 1, on equal length you set c[i] = c[j] instead of adding.")
    assert count_lis([1, 2, 4, 3, 5, 4, 7, 2]) == 3, "Expected 3 longest subsequences of length 5."


def test_all_equal_and_decreasing():
    assert count_lis([2, 2, 2, 2, 2]) == 5, (
        "Every single item is a longest strictly increasing subsequence: 5. Add c[i] for EVERY i with f[i] == max.")
    assert count_lis([5, 4, 3, 2, 1]) == 5, "Decreasing: the LIS length is 1, and there are 5 of them."


def test_increasing_has_one():
    assert count_lis([1, 2, 3]) == 1, (
        "Only 1, 2, 3 has length 3. If you got more, you did not reset c[i] when a longer length was found.")


def test_positions_not_values():
    assert count_lis([1, 2, 2]) == 2, "1,2 with the first 2, and 1,2 with the second 2: positions differ, 2 ways."


def test_empty_and_single():
    assert count_lis([]) == 0, "An empty list has no longest subsequence: 0."
    assert count_lis([9]) == 1, "One item: one subsequence of length 1."


def test_random_against_brute_force():
    rng = random.Random(53)
    for _ in range(400):
        nums = [rng.randint(0, 6) for _ in range(rng.randint(0, 11))]
        want = brute(nums)
        got = count_lis(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (counted every subsequence), got {got}. "
            "Longer length: c[i] = c[j]; equal length: c[i] += c[j]; answer: sum of c[i] where f[i] is the max.")


def test_big_input_is_fast():
    rng = random.Random(5353)
    nums = [rng.randint(1, 200) for _ in range(800)]
    rising = [k // 3 for k in range(600)]         # 200 levels of 3 equal values: 3**200 longest ones
    want = [pairs(nums), pairs(rising)]
    code = (
        "from solution import count_lis\n"
        f"print(count_lis({nums!r}), count_lis({rising!r}))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 800 numbers. Listing subsequences is exponential: add a memo, or keep the "
        "two tables f and c and fill them in O(n^2).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: wrong count (expected {str(want[0])[:30]} and 3**200 = {str(want[1])[:20]}...).")
