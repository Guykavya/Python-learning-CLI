import pathlib
import random
import subprocess
import sys

from solution import longest_palindrome, palindrome_queries

HERE = pathlib.Path(__file__).parent


def slow_longest(s):
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            if j - i > len(best) and s[i:j] == s[i:j][::-1]:
                best = s[i:j]
    return best


def test_examples():
    assert longest_palindrome("babad") == "bab", (
        "Expected 'bab': 'aba' is as long but starts later. Update the best only on a strictly larger length.")
    assert longest_palindrome("cbbd") == "bb" and longest_palindrome("forgeeksskeegfor") == "geeksskeeg"
    assert longest_palindrome("") == "" and longest_palindrome("abc") == "a"


def test_queries():
    got = palindrome_queries("abacdcaba", [(0, 3), (0, 9), (1, 4), (3, 6)])
    assert got == [True, True, False, True], (
        f"Expected [True, True, False, True], got {got}. The centre of s[l:r] is index l + r of the transformed "
        "string, and s[l:r] is a palindrome when p[l + r] >= r - l.")
    assert palindrome_queries("abba", [(0, 4), (1, 3), (0, 2), (2, 3)]) == [True, True, False, True]


def test_random_against_slow():
    rng = random.Random(1527)
    for _ in range(500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 14)))
        assert longest_palindrome(s) == slow_longest(s), f"longest_palindrome({s!r}) should be {slow_longest(s)!r}."
        qs = [(l, r) for l in range(len(s)) for r in range(l + 1, len(s) + 1)]
        want = [s[l:r] == s[l:r][::-1] for l, r in qs]
        assert palindrome_queries(s, qs) == want, f"palindrome_queries on {s!r}: some answers are wrong."


def test_long_text():
    code = (
        "import random\n"
        "from solution import longest_palindrome, palindrome_queries\n"
        "rng = random.Random(27)\n"
        "n = 2 * 10**5\n"
        "half = ''.join(rng.choice('ab') for _ in range(n // 2))\n"
        "s = half + half[::-1]\n"
        "qs = [(i, n - i) for i in range(0, n // 2, 2)] + [(0, n - 1 - i) for i in range(n // 2)]\n"
        "ans = palindrome_queries(s, qs)\n"
        "print(len(longest_palindrome(s)), sum(ans), len(longest_palindrome('ab' * (n // 2))))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for a text of 2 * 10**5 characters and 1.5 * 10**5 queries over long ranges. Slicing "
        "each range is O(r - l); one Manacher array answers each query in O(1).")
    assert r.returncode == 0, "Your code crashed on the long text:\n" + r.stderr[-800:]
    want = ["200000", "50000", "199999"]
    assert r.stdout.split() == want, f"Long text: expected {want}, got {r.stdout.split()}."
