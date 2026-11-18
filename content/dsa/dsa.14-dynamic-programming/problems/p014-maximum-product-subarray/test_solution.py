import pathlib
import random
import subprocess
import sys

from solution import max_product

HERE = pathlib.Path(__file__).parent


def brute(nums):
    """Try every block i..j (O(n^2), small inputs only)."""
    best = nums[0]
    for i in range(len(nums)):
        product = 1
        for j in range(i, len(nums)):
            product *= nums[j]
            best = max(best, product)
    return best


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_examples():
    assert max_product([2, 3, -2, 4]) == 6, "Expected 6 (block [2, 3])."
    assert max_product([-3]) == -3, "One negative item: the block is that item, -3 (not 0 or 1)."


def test_two_negatives():
    got = max_product([-2, 3, -4])
    assert got == 24, (
        f"[-2, 3, -4]: expected 24 (the whole list), got {got}. At index 2, the best block extends the "
        "SMALLEST product ending at index 1 (-6), not the largest (3). Keep both hi and lo.")


def test_zeros():
    assert max_product([-2, 0, -1]) == 0, "Expected 0: the block [0] beats -2 and -1."
    assert max_product([0, 2]) == 2, "Expected 2: after a zero, start again from the next number."
    assert max_product([2, 0, 3, 4]) == 12, "Expected 12 (block [3, 4]): a zero cuts the list in two."
    assert max_product([-1, 0, -2, -3, 0, -4]) == 6, "Expected 6 (block [-2, -3])."


def test_old_values_used():
    assert max_product([-1, -2, -3, -4]) == 24, (
        "[-1, -2, -3, -4]: expected 24. If you got something else, you may compute the new lo from the NEW hi: "
        "compute both from the old values (one tuple assignment, or save the candidates first).")


def test_random_against_brute_force():
    rng = random.Random(1414)
    for _ in range(600):
        nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 12))]
        want = brute(nums)
        got = max_product(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} (all blocks tried), got {got}. Track the largest and the smallest "
            "product ending at each index; candidates are x, hi * x, lo * x.")


def test_large_input_is_linear():
    code = (
        "import random\n"
        "from solution import max_product\n"
        "a = [0, 2, 2, 2, -1, 3] * (10**5 // 6)\n"
        "b = [-2] * 1001\n"
        "rng = random.Random(1414)\n"
        "c = [rng.choice([1, -1, 1, -1, 2, 0]) for _ in range(10**5)]\n"
        "print(max_product(a), max_product(b) == 2**1000, max_product(c))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for 100,000 items: trying every block is O(n^2). One pass with hi and lo is enough.")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError on 100,000 items: use one loop, not recursion."
    assert r.returncode == 0, "Your code crashed on 100,000 items:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["8", "True", "8192"], (
        f"Large inputs: expected 8, True (2**1000 for 1001 times -2) and 8192; got {r.stdout.split()}.")
