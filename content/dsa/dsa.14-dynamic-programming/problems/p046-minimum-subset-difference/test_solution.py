import pathlib
import random
import subprocess
import sys

from solution import split_evenly

HERE = pathlib.Path(__file__).parent


def brute_diff(nums):
    """Smallest difference over every split (only for short lists)."""
    total = sum(nums)
    n = len(nums)
    best = total
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        best = min(best, abs(total - 2 * s))
    return best


def set_diff(nums):
    total = sum(nums)
    sums = {0}
    for x in nums:
        sums |= {s + x for s in sums}
    return min(abs(total - 2 * s) for s in sums)


def problem_with(nums, answer, best):
    """Return a message describing what is wrong with answer, or None if it is a correct answer."""
    if not isinstance(answer, tuple) or len(answer) != 2:
        return f"return a pair (difference, group), got {answer!r}"
    diff, group = answer
    if diff != best:
        return f"the smallest difference is {best}, you returned {diff}"
    group = list(group)
    if any(not isinstance(i, int) or not 0 <= i < len(nums) for i in group):
        return f"group {group} must contain indices from 0 to {len(nums) - 1} (indices, not weights)"
    if len(set(group)) != len(group):
        return f"group {group} uses an index twice: each parcel goes to one friend once"
    load_a = sum(nums[i] for i in group)
    real = abs(sum(nums) - 2 * load_a)
    if real != diff:
        return (f"group {group} carries {load_a} and the rest carries {sum(nums) - load_a}: difference {real}, "
                f"not {diff}. Walk back through the 2-D table to find the parcels")
    return None


def test_examples():
    for nums, best in ([1, 6, 11, 5], 1), ([3, 1, 4, 2, 2], 0), ([10], 10):
        msg = problem_with(nums, split_evenly(list(nums)), best)
        assert msg is None, f"nums={nums}: {msg}."


def test_two_equal_and_two_different():
    for nums, best in ([7, 7], 0), ([2, 9], 7), ([1, 1, 1], 1), ([5, 5, 10], 0):
        msg = problem_with(nums, split_evenly(list(nums)), best)
        assert msg is None, f"nums={nums}: {msg}."


def test_greedy_split_is_not_enough():
    nums = [3, 3, 2, 2, 2]
    msg = problem_with(nums, split_evenly(list(nums)), 0)
    assert msg is None, (
        f"nums={nums}: {msg}. [3, 3] and [2, 2, 2] both weigh 6; 'give each parcel to the lighter friend' "
        "gives 7 against 5.")


def test_random_against_brute_force():
    rng = random.Random(46)
    for _ in range(300):
        nums = [rng.randint(1, 15) for _ in range(rng.randint(1, 10))]
        best = brute_diff(nums)
        msg = problem_with(nums, split_evenly(list(nums)), best)
        assert msg is None, f"nums={nums} (checked against every split): {msg}."


def test_big_input_is_fast():
    rng = random.Random(4646)
    cases = [[rng.randint(1, 100) for _ in range(100)], [100] * 99 + [1], [3] * 60 + [2]]
    code = (
        "from solution import split_evenly\n"
        f"cases = {cases!r}\n"
        "for c in cases:\n"
        "    d, g = split_evenly(c)\n"
        "    print(d, ' '.join(map(str, g)) or '-')\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100 parcels. Trying every split is 2**100: exponential: add a memo, "
        "or fill the subset-sum table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    lines = r.stdout.strip().splitlines()
    assert len(lines) == len(cases), f"Expected {len(cases)} printed lines, got:\n{r.stdout[-500:]}"
    for nums, line in zip(cases, lines):
        parts = line.split(maxsplit=1)
        group = [] if parts[1] == "-" else [int(t) for t in parts[1].split()]
        msg = problem_with(nums, (int(parts[0]), group), set_diff(nums))
        assert msg is None, f"Large input of {len(nums)} parcels: {msg}."
