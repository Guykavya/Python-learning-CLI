import pathlib
import random
import subprocess
import sys
from itertools import combinations
from math import comb

from solution import num_distinct

HERE = pathlib.Path(__file__).parent


def brute(s, t):
    """Try every set of len(t) positions of s."""
    return sum(1 for pos in combinations(range(len(s)), len(t)) if all(s[p] == c for p, c in zip(pos, t)))


def test_examples():
    assert num_distinct("rabbbit", "rabbit") == 3, (
        "Expected 3: any one of the three b's can be left out. If you got 1, you only took the diagonal when the "
        "letters are equal (that is LCS); counting needs 'use it' PLUS 'skip it'.")
    assert num_distinct("babgbag", "bag") == 5, "Expected 5 position sets."


def test_empty_target_and_too_long():
    assert num_distinct("abc", "") == 1, "Empty t: exactly one way (pick nothing). Base case f(i, 0) = 1."
    assert num_distinct("", "") == 1, "Both empty: one way."
    assert num_distinct("", "a") == 0, "Empty s cannot give a non-empty t: f(0, j) = 0."
    assert num_distinct("ab", "abc") == 0, "t longer than s: 0 ways."


def test_one_letter_used_once():
    assert num_distinct("a", "aa") == 0, (
        "Expected 0: the single 'a' cannot play both letters of t. With one rolling list, loop j DOWNWARDS.")
    assert num_distinct("aaa", "aa") == 3, "Choose 2 of the 3 a's: 3 ways."


def test_random_against_brute():
    rng = random.Random(63)
    for _ in range(500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 10)))
        t = "".join(rng.choice("ab") for _ in range(rng.randint(0, 4)))
        want = brute(s, t)
        got = num_distinct(s, t)
        assert got == want, (
            f"s={s!r}, t={t!r}: expected {want} (every set of positions checked), got {got}. "
            "f(i, j) = f(i-1, j) + (f(i-1, j-1) if s[i-1] == t[j-1]).")


def test_large_input_in_time():
    code = (
        "from solution import num_distinct\n"
        "print(num_distinct('a' * 400, 'a' * 200))\n"
        "print(num_distinct('ab' * 200, 'c'), num_distinct('a' * 400, 'a' * 400))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 'a' * 400 and 'a' * 200. Exponential: add a memo, or fill the table "
        "(400 x 200 cells is fast).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    lines = r.stdout.split()
    assert lines == [str(comb(400, 200)), "0", "1"], (
        "Expected C(400, 200) (choose which 200 of the 400 a's), then 0 and 1. Do not take the count modulo "
        f"anything. Got {[x[:20] for x in lines]}.")
