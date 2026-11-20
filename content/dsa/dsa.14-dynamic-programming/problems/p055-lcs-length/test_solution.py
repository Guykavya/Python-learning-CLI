import pathlib
import random
import subprocess
import sys

from solution import lcs_length

HERE = pathlib.Path(__file__).parent


def plain_recursion(a, b):
    """The definition, with no memo (only for short strings)."""
    if not a or not b:
        return 0
    if a[-1] == b[-1]:
        return plain_recursion(a[:-1], b[:-1]) + 1
    return max(plain_recursion(a[:-1], b), plain_recursion(a, b[:-1]))


def two_rows(a, b):
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            cur[j] = prev[j - 1] + 1 if ch == b[j - 1] else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def test_chapter_examples():
    assert lcs_length("abcde", "ace") == 3, "Expected 3 (ace)."
    assert lcs_length("AGGTAB", "GXTXAYB") == 4, "Expected 4 (GTAB)."
    assert lcs_length("abc", "xyz") == 0, "Nothing in common: 0."


def test_empty_strings():
    assert lcs_length("", "abc") == 0, "An empty string has nothing in common with anything: 0."
    assert lcs_length("abc", "") == 0, "An empty string has nothing in common with anything: 0."
    assert lcs_length("", "") == 0, "Two empty strings: 0."


def test_order_and_repeats():
    assert lcs_length("aaaa", "aa") == 2, "Repeats count: 'aa'. Counting common letters gives 1."
    assert lcs_length("ab", "ba") == 1, "Order matters: 'a' or 'b', not both."
    assert lcs_length("ab", "b") == 1, (
        "Expected 1. On a mismatch, drop ONE last character (max of up and left), not both (the diagonal).")


def test_subsequence_not_substring():
    assert lcs_length("axbxc", "abc") == 3, "A subsequence may skip characters: 'abc' is in both."


def test_random_against_plain_recursion():
    rng = random.Random(55)
    for _ in range(300):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        want = plain_recursion(a, b)
        got = lcs_length(a, b)
        assert got == want, (
            f"a={a!r}, b={b!r}: expected {want} (from the recursive definition), got {got}. "
            "Equal last characters: diagonal + 1; different: max(up, left).")


def test_big_input_is_fast():
    rng = random.Random(5555)
    a = "".join(rng.choice("abcd") for _ in range(400))
    b = "".join(rng.choice("abcd") for _ in range(400))
    want = [two_rows(a, b), 0, 400]
    code = (
        "from solution import lcs_length\n"
        f"print(lcs_length({a!r}, {b!r}), lcs_length('x' * 400, 'y' * 400), lcs_length('ab' * 200, 'ab' * 200))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on two strings of length 400. Without a memo every mismatch makes two calls: "
        "exponential: add a memo, or fill the (n+1) x (m+1) table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == [str(w) for w in want], (
        f"Large inputs: expected {want}, got {r.stdout.split()}.")
