import pathlib
import random
import re
import subprocess
import sys

from solution import is_match

HERE = pathlib.Path(__file__).parent


def random_pattern(rng):
    """A safe pattern: at most 5 units, so re.fullmatch stays fast on it."""
    return "".join(rng.choice(["a", "b", ".", "a*", "b*", ".*"]) for _ in range(rng.randint(0, 5)))


def test_examples():
    assert is_match("aa", "a") is False, "The pattern must match the WHOLE string."
    assert is_match("aa", "a*") is True, "'a*' matches any number of a's."
    assert is_match("ab", ".*") is True, "'.*' matches any string."
    assert is_match("aab", "c*a*b") is True, (
        "Expected True: c* is empty, a* = 'aa'. Zero copies of a unit x* means f(i, j-2): skip BOTH characters.")
    assert is_match("mississippi", "mis*is*p*.") is False, "Expected False."


def test_empty_string():
    assert is_match("", "") is True, "Empty matches empty."
    assert is_match("", "a*") is True, (
        "'' matches 'a*' (zero copies). Fill the first row: f(0, j) = f(0, j-2) when p[j-1] == '*'.")
    assert is_match("", "a*b*.*") is True, "Every unit can be empty."
    assert is_match("", ".") is False, "'.' needs exactly one character."
    assert is_match("", "a*b") is False, "The final b needs a letter."


def test_star_repeats_one_element():
    assert is_match("ab", "a*") is False, "'a*' repeats a only; it cannot produce b. This is not a wildcard star."
    assert is_match("b", "a*") is False, (
        "'a*' cannot match 'b'. 'One more copy' (f(i-1, j)) is only allowed when s[i-1] matches p[j-2].")
    assert is_match("aaa", "a*a") is True, "a* = 'aa', then 'a'."
    assert is_match("aaa", "ab*a*c*a") is True, "b* and c* are empty, a* = 'a'."
    assert is_match("abcd", ".*d") is True, "'.*' eats 'abc'."


def test_random_against_re():
    rng = random.Random(66)
    for _ in range(800):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 7)))
        p = random_pattern(rng)
        want = re.fullmatch(p, s) is not None
        got = is_match(s, p)
        assert got == want, (
            f"is_match({s!r}, {p!r}): expected {want} (as re.fullmatch says), got {got}. For x*: "
            "f(i, j-2) or (s[i-1] matches x and f(i-1, j)); otherwise s[i-1] matches p[j-1] and f(i-1, j-1).")


def test_large_input_in_time():
    code = (
        "from solution import is_match\n"
        "print(is_match('a' * 300, 'a*' * 150 + 'b'))\n"
        "print(is_match('a' * 300, 'a*' * 150))\n"
        "print(is_match('aab' * 60, 'a*a*b' * 60))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 300 letters and 150 units 'a*'. Trying every count for every unit is "
        "exponential (re.fullmatch too): add a memo on (i, j), or fill the table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True", "True"], f"Expected False, True, True; got {r.stdout.split()}."
