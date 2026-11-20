import pathlib
import random
import subprocess
import sys
from fnmatch import fnmatchcase

from solution import wildcard_match

HERE = pathlib.Path(__file__).parent


def test_examples():
    assert wildcard_match("aa", "a") is False, "The pattern must match the WHOLE string: 'a' leaves one 'a' over."
    assert wildcard_match("aa", "*") is True, "'*' matches any sequence."
    assert wildcard_match("cb", "?a") is False, "'?' matches c, but 'a' does not match 'b'."
    assert wildcard_match("adceb", "*a*b") is True, (
        "Expected True: the first * is empty, the second eats 'dce'. A star that eats one letter must STAY: "
        "read f(i-1, j), not f(i-1, j-1).")
    assert wildcard_match("acdcb", "a*c?b") is False, "Expected False."


def test_empty_cases():
    assert wildcard_match("", "") is True, "Empty matches empty: f(0, 0) = True."
    assert wildcard_match("", "*") is True, "A star may be empty. Fill the first row: f(0, j) = f(0, j-1) and p[j-1] == '*'."
    assert wildcard_match("", "**") is True, "Two empty stars."
    assert wildcard_match("", "?") is False, "'?' needs exactly one character."
    assert wildcard_match("", "*a") is False, "The 'a' needs a letter; the first row stops being True at it."
    assert wildcard_match("a", "") is False, "An empty pattern only matches the empty string."


def test_star_eats_many():
    assert wildcard_match("abcd", "a*") is True, (
        "Expected True: the star eats 'bcd'. If a star can only eat one letter, it moves j as well; keep j.")
    assert wildcard_match("abcd", "*d") is True, "Leading star eats 'abc'."
    assert wildcard_match("abcd", "a*c") is False, "The pattern ends with c, the string with d."


def test_random_against_fnmatch():
    rng = random.Random(65)
    for _ in range(800):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 7)))
        p = "".join(rng.choice("ab?**") for _ in range(rng.randint(0, 6)))
        want = fnmatchcase(s, p)
        got = wildcard_match(s, p)
        assert got == want, (
            f"wildcard_match({s!r}, {p!r}): expected {want} (as the fnmatch module says), got {got}. "
            "'*' -> f(i, j-1) or f(i-1, j); '?' or the same letter -> f(i-1, j-1).")


def test_large_input_in_time():
    code = (
        "from solution import wildcard_match\n"
        "print(wildcard_match('a' * 300, '*a' * 150 + 'b'))\n"
        "print(wildcard_match('a' * 300, 'a*' * 150))\n"
        "print(wildcard_match('ab' * 150, '?*' * 150))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 300 letters and 150 stars. Trying every length for every star is exponential: "
        "add a memo on (i, j), or fill the table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True", "True"], f"Expected False, True, True; got {r.stdout.split()}."
