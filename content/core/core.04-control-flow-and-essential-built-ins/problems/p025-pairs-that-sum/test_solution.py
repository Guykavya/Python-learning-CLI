import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def expected(nums, t):
    out = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == t:
                out.append(f"{nums[i]} + {nums[j]}")
    return out + [f"Pairs: {len(out)}"]


def check(nums, t, msg):
    got = run(" ".join(map(str, nums)) + f"\n{t}\n")
    assert got == expected(nums, t), f"{nums}, target {t}: expected {expected(nums, t)}, got {got}. {msg}"


def test_example():
    check([3, 5, 2, 4, 3], 6, "A number is never paired with itself, and each pair appears once.")


def test_no_self_pairs():
    check([3], 6, "One number cannot form a pair with itself.")
    check([5, 1], 10, "5 + 5 would need two 5s.")


def test_duplicates_count_separately():
    check([2, 2, 2], 4, "Three 2s at three positions make three pairs: (0,1), (0,2), (1,2).")


def test_negatives_and_zero():
    check([-1, 1, 0, 0, 7, -7], 0, "Negative numbers and zeros work like any others.")


def test_order():
    check([1, 9, 2, 8, 3, 7], 10, "Pairs come in order of the first position, then the second.")


def test_empty_line():
    assert run("\n5\n") == ["Pairs: 0"], "No numbers: no pairs, but still print the count."
