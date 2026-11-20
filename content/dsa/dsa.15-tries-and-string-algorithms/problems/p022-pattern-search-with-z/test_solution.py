import os
import pathlib
import random
import subprocess
import sys

from solution import match_lengths, z_search

HERE = pathlib.Path(__file__).parent


def slow_lengths(text, pattern):
    return [len(os.path.commonprefix([pattern, text[i:]])) for i in range(len(text))]


def by_find(text, pattern):
    if not pattern:
        return list(range(len(text) + 1))
    out, start = [], 0
    while (i := text.find(pattern, start)) != -1:
        out.append(i)
        start = i + 1
    return out


def test_examples():
    got = match_lengths("abaab", "aba")
    assert got == [3, 0, 1, 2, 0], (
        f"Expected [3, 0, 1, 2, 0], got {got}. Cap every value at len(pattern): position 0 has z = 5 in "
        "'aba' + 'abaab', but only 3 of it is the pattern.")
    assert z_search("abababab", "abab") == [0, 2, 4], "Overlapping matches: [0, 2, 4]."


def test_any_characters():
    got = z_search("a#a#a", "#a")
    assert got == [1, 3], f"'#' is an ordinary character here: expected [1, 3], got {got}."
    assert match_lengths("##", "#") == [1, 1]


def test_edges():
    assert match_lengths("xyz", "") == [0, 0, 0] and z_search("xy", "") == [0, 1, 2]
    assert match_lengths("", "abc") == [] and z_search("", "a") == []
    assert z_search("ab", "abc") == [] and match_lengths("ab", "abc") == [2, 0], (
        "A pattern longer than the text: no occurrence, but the lengths still count the partial match.")


def test_random_against_slow():
    rng = random.Random(1522)
    for _ in range(1000):
        text = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 15)))
        pattern = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 4)))
        assert match_lengths(text, pattern) == slow_lengths(text, pattern), (
            f"match_lengths({text!r}, {pattern!r}) should be {slow_lengths(text, pattern)}.")
        assert z_search(text, pattern) == by_find(text, pattern), (
            f"z_search({text!r}, {pattern!r}) should be {by_find(text, pattern)}.")


def test_long_text():
    code = (
        "from solution import match_lengths, z_search\n"
        "text = 'a' * 5 * 10**5\n"
        "lengths = match_lengths(text, 'a' * 10**5)\n"
        "print(sum(lengths), len(z_search(text, 'a' * 10**5)), len(z_search(text, 'a' * 999 + 'b')))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s). Worst case: a repeated pattern like aaaa...b, where comparing from scratch at every "
        "position is O(n * m). One Z-function of pattern + text is linear.")
    assert r.returncode == 0, "Your code crashed on a long text:\n" + r.stderr[-800:]
    want = ["45000050000", "400001", "0"]
    assert r.stdout.split() == want, f"Long text: expected {want}, got {r.stdout.split()}."
