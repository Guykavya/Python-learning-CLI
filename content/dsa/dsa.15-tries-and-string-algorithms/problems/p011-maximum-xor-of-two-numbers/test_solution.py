import pathlib
import random
import subprocess
import sys

from solution import max_xor

HERE = pathlib.Path(__file__).parent


def brute(nums):
    return max((a ^ b for i, a in enumerate(nums) for b in nums[i + 1:]), default=0)


def test_examples():
    assert max_xor([3, 10, 5, 25, 2, 8]) == 28, "Expected 28 (5 ^ 25)."
    assert max_xor([0]) == 0, "One number: 0."
    assert max_xor([7, 7]) == 0, "Equal numbers: 7 ^ 7 = 0."


def test_not_max_and_min():
    got = max_xor([1, 2, 4, 8])
    assert got == 12, f"Expected 12 (4 ^ 8), got {got}. max ^ min = 9 is not the best pair."


def test_high_bits():
    got = max_xor([2**30, 2**30 - 1, 5])
    assert got == 2**31 - 1, (
        f"2**30 ^ (2**30 - 1) = 2**31 - 1, got {got}. Use 31 bits: with fewer bits the high ones are lost.")


def test_random_against_brute_force():
    rng = random.Random(1511)
    for _ in range(300):
        nums = [rng.randrange(0, rng.choice([2, 16, 1000, 2**31])) for _ in range(rng.randint(1, 12))]
        want = brute(nums)
        got = max_xor(list(nums))
        assert got == want, f"nums={nums}: expected {want}, got {got}. Prefer the opposite bit, highest bit first."


def test_large_list():
    code = (
        "import random\n"
        "from solution import max_xor\n"
        "rng = random.Random(1511)\n"
        "nums = [rng.randrange(2**31) & ~(1 << 30) for _ in range(10**5)]\n"
        "nums[777] |= 1 << 30\n"
        "print(max_xor(nums))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 10**5 numbers. All pairs is 5 * 10**9 XORs; the binary trie needs 31 steps per number.")
    assert r.returncode == 0, "Your code crashed on the large list:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["2147474189"], f"Large list: expected 2147474189, got {r.stdout.split()}."
