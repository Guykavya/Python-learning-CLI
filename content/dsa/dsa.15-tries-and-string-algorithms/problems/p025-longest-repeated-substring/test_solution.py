import pathlib
import random
import subprocess
import sys

from solution import longest_repeat

HERE = pathlib.Path(__file__).parent


def slow_len(s):
    best = 0
    for L in range(1, len(s)):
        seen = set()
        for i in range(len(s) - L + 1):
            if s[i:i + L] in seen:
                best = L
                break
            seen.add(s[i:i + L])
    return best


def occurs_twice(s, t):
    i = s.find(t)
    return i != -1 and s.find(t, i + 1) != -1


def check(s, got, want_len):
    if not isinstance(got, str):
        return f"return a string, got {got!r}"
    if len(got) != want_len:
        return f"the longest repeat has length {want_len}, you returned {got!r} (length {len(got)})"
    if got and not occurs_twice(s, got):
        return f"{got!r} does not occur twice in {s!r} (verify hash matches by comparing the strings)"
    return None


def test_examples():
    assert longest_repeat("banana") == "ana", "Expected 'ana' (positions 1 and 3, overlapping)."
    assert longest_repeat("abcd") == "", "No character repeats: ''."
    assert longest_repeat("aaaaa") == "aaaa", "Expected 'aaaa' (positions 0 and 1)."
    error = check("mississippi", longest_repeat("mississippi"), 4)
    assert error is None, f"mississippi: {error}."


def test_edges():
    assert longest_repeat("") == "" and longest_repeat("x") == "" and longest_repeat("xx") == "x"


def test_random_validated():
    rng = random.Random(1525)
    for _ in range(500):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 16)))
        error = check(s, longest_repeat(s), slow_len(s))
        assert error is None, f"longest_repeat({s!r}): {error}."


def test_long_strings():
    code = (
        "import random\n"
        "from solution import longest_repeat\n"
        "rng = random.Random(25)\n"
        "s = ''.join(rng.choice('abc') for _ in range(10**5))\n"
        "t = s[:40000] + s[10000:30000] + ''.join(rng.choice('abc') for _ in range(40000))\n"
        "a, b, c = longest_repeat(s), longest_repeat(t), longest_repeat('a' * 10**5)\n"
        "print(len(a), s.find(a) != s.rfind(a), len(b), len(c))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (60 s) for 10**5 characters. Sets of all substrings of every length are O(n**2); binary "
        "search the length and test each one with prefix hashes in O(n).")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    want = ["20", "True", "20002", "99999"]
    assert r.stdout.split() == want, (
        f"Long strings: expected lengths 20, a real repeat, 20002 and 99999, got {r.stdout.split()}.")
