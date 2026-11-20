import pathlib
import random
import subprocess
import sys

from solution import kmp_search

HERE = pathlib.Path(__file__).parent


def by_find(text, pattern):
    out, start = [], 0
    while True:
        i = text.find(pattern, start)
        if i == -1 or i > len(text):
            return out
        out.append(i)
        start = i + 1


def test_examples():
    assert kmp_search("abcabcabd", "abcabd") == [3], "Expected [3]."
    assert kmp_search("abababab", "abab") == [0, 2, 4], "Expected [0, 2, 4]."
    assert kmp_search("hello", "xyz") == [] and kmp_search("abc", "abc") == [0]


def test_overlapping():
    got = kmp_search("aaaaa", "aa")
    assert got == [0, 1, 2, 3], (
        f"Expected [0, 1, 2, 3], got {got}. After a full match set k = pi[m - 1], not 0, so overlapping "
        "matches are found.")


def test_edges():
    assert kmp_search("abc", "abcd") == [], "A pattern longer than the text: []."
    assert kmp_search("ab", "") == [0, 1, 2], "The empty pattern occurs at 0, 1, ..., len(text)."
    assert kmp_search("", "") == [0] and kmp_search("", "a") == []
    assert kmp_search("a#b#a#b", "#") == [1, 3, 5], "Any characters may appear."


def test_random_against_find():
    rng = random.Random(1515)
    for _ in range(1500):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 20)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        want = by_find(text, pattern)
        got = kmp_search(text, pattern)
        assert got == want, f"kmp_search({text!r}, {pattern!r}): expected {want}, got {got}."


def test_worst_case_in_time():
    code = (
        "from solution import kmp_search\n"
        "text = 'a' * 10**6\n"
        "print(len(kmp_search(text, 'a' * 1000 + 'b')), len(kmp_search(text, 'a' * 1000)),\n"
        "      len(kmp_search('ab' * 5 * 10**5, 'abab')), kmp_search('x' * 999 + 'yx', 'xy'))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s). Worst case: repeated pattern like aaaa...b in a text of a's. The naive search compares "
        "1000 letters at each of 10**6 starts; KMP reads every text letter once.")
    assert r.returncode == 0, "Your code crashed on a long text:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["0", "999001", "499999", "[998]"], (
        f"Long texts: expected 0 999001 499999 [998], got {r.stdout.split()}.")
