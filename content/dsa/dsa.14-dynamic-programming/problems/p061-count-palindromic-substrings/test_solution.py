import pathlib
import random
import subprocess
import sys

from solution import count_palindromes

HERE = pathlib.Path(__file__).parent


def brute(s):
    """Check every substring: obviously right, O(n^3)."""
    count = 0
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if s[i:j] == s[i:j][::-1]:
                count += 1
    return count


def test_examples():
    assert count_palindromes("abc") == 3, "Expected 3: only the single letters are palindromes."
    assert count_palindromes("aaa") == 6, (
        "Expected 6: 'a' three times, 'aa' twice, 'aaa' once. Substrings at different positions count "
        "separately; do not collect them in a set.")
    assert count_palindromes("abba") == 6, (
        "Expected 6 (a, b, b, a, bb, abba). If you got 4, you only expand around letters: the gaps between "
        "letters are centres too (even lengths).")


def test_empty_and_single():
    assert count_palindromes("") == 0, "The empty string has no non-empty substrings: 0."
    assert count_palindromes("x") == 1, "One letter is one palindrome."
    assert count_palindromes("xy") == 2, "'xy': only the two letters."
    assert count_palindromes("zz") == 3, "'zz': 'z', 'z' and 'zz'."


def test_odd_inside_needed():
    assert count_palindromes("aba") == 4, (
        "Expected 4 (a, b, a, aba). If 'aba' is missing, your table read is_pal[i+1][j-1] before it was "
        "filled: loop by length, or with i going DOWN.")
    assert count_palindromes("racecar") == 10, "Expected 10: 7 letters, 'cec', 'aceca', 'racecar'."


def test_random_against_brute():
    rng = random.Random(61)
    for _ in range(600):
        alphabet = rng.choice(["ab", "abc", "aab"])
        s = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 12)))
        want = brute(s)
        got = count_palindromes(s)
        assert got == want, (
            f"s={s!r}: expected {want} palindromic substrings (checked one by one), got {got}. Each successful "
            "expansion step is one palindrome; use both letter centres and gap centres.")


def test_large_inputs_in_time():
    code = (
        "from solution import count_palindromes\n"
        "print(count_palindromes('a' * 1500), count_palindromes('ab' * 1000), count_palindromes('abc' * 500))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on strings of 1,500 to 2,000 letters. If you count with a recursion on (i, j) "
        "without a memo, it is exponential: add a memo, or use the table or the expansion (O(n^2)).")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["1125750", "1001000", "1500"], (
        f"Expected 1125750 ('a' * 1500: n(n+1)/2), 1001000 ('ab' * 1000: every odd-length substring) and 1500 "
        f"('abc' * 500: only letters); got {r.stdout.split()}.")
