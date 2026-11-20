import pathlib
import random
import subprocess
import sys

from solution import shortest_palindrome

HERE = pathlib.Path(__file__).parent


def slow(s):
    for k in range(len(s), -1, -1):
        if s[:k] == s[:k][::-1]:
            return s[k:][::-1] + s
    return s


def test_examples():
    assert shortest_palindrome("aacecaaa") == "aaacecaaa"
    assert shortest_palindrome("abcd") == "dcbabcd"
    assert shortest_palindrome("aba") == "aba", "Already a palindrome: add nothing."
    assert shortest_palindrome("") == "" and shortest_palindrome("x") == "x"


def test_separator_inside_the_string():
    got = shortest_palindrome("#a")
    assert got == "a#a", (
        f"Expected 'a#a', got {got!r}. With '#' as separator, the border '#a#' of '#a#a#' crosses it. Use a "
        "separator that cannot occur in s, for example None in a list.")
    for s in ["a#", "#", "##a", "a#b#a#", "\x00ab"]:
        assert shortest_palindrome(s) == slow(s), f"shortest_palindrome({s!r}) should be {slow(s)!r}."


def test_random_against_slow():
    rng = random.Random(1520)
    for _ in range(1500):
        s = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 12)))
        want = slow(s)
        got = shortest_palindrome(s)
        assert got == want, f"shortest_palindrome({s!r}): expected {want!r}, got {got!r}."


def test_long_string():
    code = (
        "from solution import shortest_palindrome\n"
        "n = 3 * 10**5\n"
        "a = shortest_palindrome('a' * (n // 2) + 'b' + 'a' * (n // 2 - 2) + 'c')\n"
        "b = shortest_palindrome('ab' * (n // 2))\n"
        "print(len(a), a == a[::-1], len(b))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s) for 3 * 10**5 characters. Testing every prefix for being a palindrome copies "
        "O(n**2) characters. Use the prefix function on s + separator + reversed(s).")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["450000", "True", "300001"], (
        f"Long strings: expected 450000 True 300001, got {r.stdout.split()}.")
