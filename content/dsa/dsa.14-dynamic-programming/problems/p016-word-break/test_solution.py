import pathlib
import random
import subprocess
import sys

from solution import word_break

HERE = pathlib.Path(__file__).parent


def brute(s, words):
    """Try every first word (plain recursion, short strings only)."""
    if s == "":
        return True
    return any(s.startswith(w) and brute(s[len(w):], words) for w in words)


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_examples():
    assert word_break("leetcode", ["leet", "code"]) is True, "'leetcode' = 'leet' + 'code'."
    assert word_break("applepenapple", ["apple", "pen"]) is True, (
        "'applepenapple' = apple + pen + apple: a word may be used more than once.")
    assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False, (
        "'catsandog' cannot be cut: 'cats' + 'and' leaves 'og', 'cat' + 'sand' leaves 'og'. Return False.")


def test_empty_and_whole():
    assert word_break("", ["a"]) is True, "The empty string needs no cut: f(0) = True."
    assert word_break("abc", ["abc"]) is True, "The whole string is one word."
    assert word_break("abc", ["ab", "bc"]) is False, "'ab' leaves 'c'; 'bc' does not start the string."


def test_greedy_longest_first_fails():
    assert word_break("aaaaaaa", ["aaaa", "aaa"]) is True, (
        "'aaaaaaa' = 'aaaa' + 'aaa' (or 'aaa' + 'aaaa'). Greedy 'take the longest word that fits' also works "
        "here, but not in the next test: try all cut points.")
    assert word_break("aaab", ["a", "aa", "aab"]) is True, (
        "'aaab' = 'a' + 'aab'. Taking 'aa' first leaves 'ab', which fails: the DP must try every cut.")


def test_random_against_brute_force():
    rng = random.Random(1616)
    for _ in range(400):
        words = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 3))) for _ in range(rng.randint(1, 4))]
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 12)))
        want = brute(s, words)
        got = word_break(s, list(words))
        assert got == want, (
            f"s={s!r}, words={words}: expected {want}, got {got}. f(i) is True if some j < i has f(j) True "
            "and s[j:i] in the word set; f(0) = True.")


def test_not_exponential():
    code = (
        "import sys\n"
        "sys.setrecursionlimit(5000)\n"
        "from solution import word_break\n"
        "words = ['a' * k for k in range(1, 11)]\n"
        "print(word_break('a' * 40 + 'b', words))\n"
    )
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for 'a' * 40 + 'b': exponential: add a memo. Without one, every way of cutting the "
        "a's is tried before failing at 'b'.")
    assert r.returncode == 0, "Your code crashed:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False"], f"'a' * 40 + 'b' cannot be cut (no word has a 'b'), got {r.stdout}."


def test_long_strings():
    code = (
        "import sys\n"
        "sys.setrecursionlimit(5000)\n"
        "from solution import word_break\n"
        "words = ['a' * k for k in range(1, 11)]\n"
        "print(word_break('a' * 1000 + 'b', words), word_break('a' * 1000, words))\n"
        "w2 = ['abc' * 6, 'ab', 'cab', 'c']\n"
        "print(word_break('abc' * 333, w2), word_break('abc' * 333 + 'a', w2))\n"
        "print(word_break('x' * 999 + 'y', ['x' * 20, 'x' * 19, 'xy']))\n"
    )
    r = run_big(code, 10)
    assert r is not None, (
        "Time limit (10 s) for strings of length 1000: use a table (or a memo over positions), turn the words "
        "into a set, and only look back as far as the longest word.")
    assert r.returncode == 0, "Your code crashed on long strings:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True", "True", "False", "True"], (
        f"Long strings: expected False True / True False / True, got {r.stdout.split()}.")
