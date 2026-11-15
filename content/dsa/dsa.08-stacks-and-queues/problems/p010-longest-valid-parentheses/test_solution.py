import random
import subprocess
import sys
from pathlib import Path

import pytest

from solution import longest_valid

HERE = Path(__file__).parent


def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def balanced(t):
    depth = 0
    for ch in t:
        depth += 1 if ch == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def slow(s):
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if j - i > len(best) and balanced(s[i:j]):
                best = s[i:j]
    return best


@pytest.mark.parametrize("s, want, why", [
    (")()())", "()()", "the example: the run is from index 1 to 4"),
    ("(()", "()", "the first ( is never closed"),
    ("()(())", "()(())", "the whole string"),
    ("())(())", "(())", "an unmatched ) splits the string into two runs: do not join them"),
    ("))((", "", "no valid run at all: return the empty string"),
    ("", "", "empty input"),
    ("()", "()", "one pair"),
    ("()))()", "()", "two runs of length 2: return the FIRST one (use > not >=)"),
    ("(()(((()", "()", "two runs of length 2 (at index 1 and index 6): return the earliest"),
    ("((()))())", "((()))()", "a nested run followed by a pair"),
])
def test_cases(s, want, why):
    got = longest_valid(s)
    assert got == want, f"longest_valid({s!r}) should be {want!r}, got {got!r}: {why}."


def test_random_against_slow():
    rng = random.Random(10)
    for _ in range(1500):
        s = "".join(rng.choice("()") for _ in range(rng.randint(0, 14)))
        want = slow(s)
        got = longest_valid(s)
        assert got == want, (f"longest_valid({s!r}) should be {want!r}, got {got!r}. "
                             "Check the wall after an unmatched ')' and the start index stack[-1] + 1.")


def test_long_input_in_time():
    code = (
        "from solution import longest_valid\n"
        "s = '(' * 50000 + ')' * 49999 + ')(' + '()' * 10\n"
        "print(len(longest_valid(s)))\n"
    )
    out = run_code(code, 20, "A string of 100,000 parentheses (use the O(n) stack of indices, not every substring)")
    assert out == "100000", f"The longest run in the big test has length 100000, got {out}."
