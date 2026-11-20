import pathlib
import random
import subprocess
import sys

from solution import longest_pal_dp, longest_pal_expand

HERE = pathlib.Path(__file__).parent
BOTH = [("longest_pal_dp", longest_pal_dp), ("longest_pal_expand", longest_pal_expand)]


def brute(s):
    """Leftmost longest palindromic substring, checking every substring (short strings only)."""
    best = ""
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            t = s[i:j]
            if t == t[::-1] and len(t) > len(best):
                best = t
    return best


def test_examples():
    for name, f in BOTH:
        assert f("babad") == "bab", (
            f"{name}('babad'): expected 'bab'. 'aba' is as long but starts later; update the best only on a "
            "STRICTLY longer palindrome (> not >=).")
        assert f("forgeeksskeegfor") == "geeksskeeg", f"{name}('forgeeksskeegfor'): expected 'geeksskeeg'."


def test_even_length():
    for name, f in BOTH:
        got = f("cbbd")
        assert got == "bb", (
            f"{name}('cbbd'): expected 'bb', got {got!r}. Even-length palindromes have a GAP as their centre: "
            "also expand from (c, c + 1), and handle length 2 in the table.")
        assert f("abba") == "abba", f"{name}('abba'): the whole string, even length."


def test_small_cases():
    for name, f in BOTH:
        assert f("") == "", f"{name}(''): the empty string gives ''."
        assert f("x") == "x", f"{name}('x'): one letter is a palindrome."
        assert f("abc") == "a", f"{name}('abc'): every letter is a palindrome of length 1; return the first, 'a'."
        assert f("aaaa") == "aaaa", f"{name}('aaaa'): the whole string."


def test_off_by_one_after_expanding():
    for name, f in BOTH:
        got = f("xabacdy")
        assert got == "aba", (
            f"{name}('xabacdy'): expected 'aba', got {got!r}. When the while loop stops, lo and hi are one step "
            "past the palindrome: it is s[lo + 1:hi].")


def test_random_against_brute_force():
    rng = random.Random(6060)
    for _ in range(300):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 14)))
        want = brute(s)
        for name, f in BOTH:
            got = f(s)
            assert got == want, (
                f"{name}({s!r}): expected {want!r} (the leftmost of the longest), got {got!r}.")


def test_long_strings():
    code = (
        "import random\n"
        "from solution import longest_pal_dp, longest_pal_expand\n"
        "rng = random.Random(60)\n"
        "s = ''.join(rng.choice('ab') for _ in range(3000))\n"
        "a = 'a' * 3000\n"
        "x = longest_pal_expand(s)\n"
        "print(len(x), s.index(x), len(longest_pal_expand(a)))\n"
        "y = longest_pal_dp(s)\n"
        "print(len(y), s.index(y), len(longest_pal_dp(a)))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (60 s) for strings of 3000 characters. Checking every substring with t == t[::-1] is "
        "O(n**3); both methods here are O(n**2).")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    lines = r.stdout.split("\n")
    assert lines[0].split() == ["33", "1580", "3000"], (
        "longest_pal_expand on 3000 characters: expected (length, start, all-'a' length) 33 1580 3000, "
        f"got {lines[0]}.")
    assert lines[1].split() == ["33", "1580", "3000"], (
        f"longest_pal_dp on 3000 characters: expected 33 1580 3000, got {lines[1]}.")
