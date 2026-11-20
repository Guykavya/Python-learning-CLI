import pathlib
import random
import subprocess
import sys

from solution import lcs_string

HERE = pathlib.Path(__file__).parent


def lcs_len(a, b):
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            cur[j] = prev[j - 1] + 1 if ch == b[j - 1] else max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]


def is_subsequence(s, t):
    it = iter(t)
    return all(ch in it for ch in s)


def problem_with(a, b, got):
    """None if got is a longest common subsequence of a and b, else a message."""
    if not isinstance(got, str):
        return f"return a string, got {got!r}"
    want = lcs_len(a, b)
    if not is_subsequence(got, a):
        return f"{got!r} is not a subsequence of a={a!r} (did you forget to reverse the collected characters?)"
    if not is_subsequence(got, b):
        return f"{got!r} is not a subsequence of b={b!r}"
    if len(got) != want:
        return (f"{got!r} has length {len(got)}, but the LCS length is {want}. On a mismatch move to the "
                "LARGER neighbour (up if f[i-1][j] >= f[i][j-1], else left), never diagonally")
    return None


def test_chapter_examples():
    for a, b in (("abcde", "ace"), ("AGGTAB", "GXTXAYB"), ("ABCBDAB", "BDCABA")):
        msg = problem_with(a, b, lcs_string(a, b))
        assert msg is None, f"a={a!r}, b={b!r}: {msg}."


def test_nothing_in_common_and_empty():
    assert lcs_string("abc", "xyz") == "", "Nothing in common: the empty string ''."
    assert lcs_string("", "abc") == "", "An empty string: ''."
    assert lcs_string("abc", "") == "", "An empty string: ''."


def test_order_is_kept():
    msg = problem_with("abcde", "ace", lcs_string("abcde", "ace"))
    assert msg is None, msg
    assert lcs_string("abcde", "ace") == "ace", (
        "The only LCS of 'abcde' and 'ace' is 'ace'. 'eca' means the collected characters were not reversed.")


def test_mismatch_does_not_drop_both():
    assert lcs_string("ab", "b") == "b", "Expected 'b'. On a mismatch move up or left, not diagonally."
    assert lcs_string("abcabc", "abc") == "abc", "'abc' appears in both."


def test_random_validated():
    rng = random.Random(56)
    for _ in range(400):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 9)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 9)))
        msg = problem_with(a, b, lcs_string(a, b))
        assert msg is None, f"a={a!r}, b={b!r}: {msg}."


def test_big_input_is_fast():
    rng = random.Random(5656)
    a = "".join(rng.choice("ACGT") for _ in range(400))
    b = "".join(rng.choice("ACGT") for _ in range(400))
    code = (
        "from solution import lcs_string\n"
        f"print(lcs_string({a!r}, {b!r}))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on two strings of length 400. A recursion without a memo is exponential: add a memo, "
        "or fill the table and walk back once.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    msg = problem_with(a, b, r.stdout.strip())
    assert msg is None, f"Large input (two DNA strings of length 400): {msg}."
