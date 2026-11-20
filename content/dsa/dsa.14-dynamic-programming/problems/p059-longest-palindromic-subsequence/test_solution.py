import itertools
import pathlib
import random
import subprocess
import sys

from solution import longest_pal_subseq

HERE = pathlib.Path(__file__).parent


def brute_len(s):
    """Length of the longest palindromic subsequence by trying every subsequence (len(s) <= 12 only)."""
    best = 0
    for r in range(len(s) + 1):
        for idx in itertools.combinations(range(len(s)), r):
            t = "".join(s[i] for i in idx)
            if t == t[::-1]:
                best = max(best, r)
    return best


def is_subsequence(t, s):
    it = iter(s)
    return all(ch in it for ch in t)


def check(s, got, want_len):
    """Returns an error message or None."""
    if not isinstance(got, str):
        return f"return a string, got {got!r}"
    if got != got[::-1]:
        return f"{got!r} is not a palindrome (did you put both matching letters at the front?)"
    if not is_subsequence(got, s):
        return f"{got!r} is not a subsequence of {s!r} (the letters must appear in s in this order)"
    if len(got) != want_len:
        return f"{got!r} has length {len(got)}, but the longest palindromic subsequence has length {want_len}"
    return None


def test_examples():
    for s, n in [("bbbab", 4), ("character", 5), ("cbbd", 2), ("a", 1), ("", 0)]:
        error = check(s, longest_pal_subseq(s), n)
        assert error is None, f"longest_pal_subseq({s!r}): {error}."


def test_subsequence_not_substring():
    got = longest_pal_subseq("bbbab")
    assert got == "bbbb", (
        f"Expected 'bbbb' (skip the 'a'), got {got!r}. 'bbb' is the longest palindromic SUBSTRING; a subsequence "
        "may leave out letters in between.")


def test_odd_middle_letter():
    error = check("racecar", longest_pal_subseq("racecar"), 7)
    assert error is None, f"'racecar' is itself a palindrome with one middle letter: {error}."
    error = check("abcxyz", longest_pal_subseq("abcxyz"), 1)
    assert error is None, f"All letters different: any single letter is the answer. {error}."


def test_random_validated():
    rng = random.Random(5959)
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 11)))
        error = check(s, longest_pal_subseq(s), brute_len(s))
        assert error is None, (
            f"longest_pal_subseq({s!r}): {error}. Fill f[i][j] by length, then walk from (0, n - 1): matching "
            "ends go one to the front and one to the back; otherwise move toward the bigger neighbour.")


def test_long_string():
    code = (
        "import random\n"
        "from solution import longest_pal_subseq\n"
        "rng = random.Random(59)\n"
        "s = ''.join(rng.choice('abcd') for _ in range(1000))\n"
        "t = longest_pal_subseq(s)\n"
        "it = iter(s)\n"
        "print(len(t), t == t[::-1], all(ch in it for ch in t))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for a string of 1000 letters: the table has 10**6 cells, fill each once. "
        "A recursion without a memo is exponential.")
    if "RecursionError" in r.stderr:
        assert False, "RecursionError on 1000 letters: fill the table by length instead of recursing."
    assert r.returncode == 0, "Your code crashed on the long string:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["661", "True", "True"], (
        f"Long string: expected length 661, a palindrome, and a subsequence; got {r.stdout.split()}.")
