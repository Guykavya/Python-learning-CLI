import pathlib
import random
import subprocess
import sys

from solution import is_interleave

HERE = pathlib.Path(__file__).parent


def brute(s1, s2, s3):
    """Plain recursion: try both strings at every step. Exponential, fine for tiny inputs."""
    if not s3:
        return not s1 and not s2
    if s1 and s1[0] == s3[0] and brute(s1[1:], s2, s3[1:]):
        return True
    if s2 and s2[0] == s3[0] and brute(s1, s2[1:], s3[1:]):
        return True
    return False


def test_examples():
    assert is_interleave("aabcc", "dbbca", "aadbbcbcac") is True, "Expected True (aa|dbbc|bc|a|c)."
    assert is_interleave("aabcc", "dbbca", "aadbbbaccc") is False, "Expected False."


def test_empty_and_lengths():
    assert is_interleave("", "", "") is True, "Three empty strings: True (f(0, 0) = True)."
    assert is_interleave("", "abc", "abc") is True, "s1 empty: True exactly when s3 == s2."
    assert is_interleave("abc", "", "abd") is False, "s2 empty and s3 != s1: False."
    assert is_interleave("a", "b", "a") is False, (
        "Expected False: the b of s2 is never used. Check len(s1) + len(s2) == len(s3) first.")
    assert is_interleave("a", "b", "abb") is False, "s3 is too long: False."


def test_greedy_is_not_enough():
    assert is_interleave("ab", "ac", "acab") is True, (
        "Expected True: the first 'a' must come from s2. Taking from s1 whenever it fits gets stuck; when both "
        "strings offer the same letter, try both (that is why this is DP).")
    assert is_interleave("ac", "ab", "abac") is True, "Same idea with the strings swapped."


def test_returns_bool():
    assert isinstance(is_interleave("a", "b", "ab"), bool), "Return True or False, not a number or None."


def test_random_against_brute():
    rng = random.Random(64)
    for _ in range(600):
        s1 = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        s2 = "".join(rng.choice("ab") for _ in range(rng.randint(0, 5)))
        if rng.random() < 0.5:
            # a real shuffle, so that True answers are common
            letters, i, j = [], 0, 0
            while i < len(s1) or j < len(s2):
                if j == len(s2) or (i < len(s1) and rng.random() < 0.5):
                    letters.append(s1[i])
                    i += 1
                else:
                    letters.append(s2[j])
                    j += 1
            s3 = "".join(letters)
        else:
            s3 = "".join(rng.choice("ab") for _ in range(len(s1) + len(s2) + rng.choice([0, 0, 0, -1, 1])))
        want = brute(s1, s2, s3)
        got = is_interleave(s1, s2, s3)
        assert got == want, (
            f"is_interleave({s1!r}, {s2!r}, {s3!r}): expected {want} (all splits tried), got {got}. The last letter "
            "of s3[:i+j] comes from s1 (needs f(i-1, j)) or from s2 (needs f(i, j-1)).")


def test_large_input_in_time():
    code = (
        "from solution import is_interleave\n"
        "print(is_interleave('a' * 300, 'a' * 300, 'a' * 599 + 'b'))\n"
        "print(is_interleave('a' * 300 + 'b', 'a' * 299 + 'c', 'a' * 599 + 'bc'))\n"
        "print(is_interleave('a' * 300 + 'b', 'a' * 299 + 'c', 'a' * 599 + 'cb'))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on strings of 300 letters. A recursion that tries both strings without a memo is "
        "exponential: add a memo on (i, j), or fill the table.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True", "True"], (
        f"Expected False, True, True; got {r.stdout.split()}.")
