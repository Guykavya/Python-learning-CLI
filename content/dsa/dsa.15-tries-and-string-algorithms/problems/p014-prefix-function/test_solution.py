import pathlib
import random
import subprocess
import sys

from solution import prefix_function

HERE = pathlib.Path(__file__).parent


def slow(s):
    out = []
    for i in range(len(s)):
        t = s[:i + 1]
        out.append(max((k for k in range(1, len(t)) if t[:k] == t[-k:]), default=0))
    return out


def test_examples():
    assert prefix_function("abcabcd") == [0, 0, 0, 1, 2, 3, 0], "Expected [0, 0, 0, 1, 2, 3, 0]."
    assert prefix_function("aaaa") == [0, 1, 2, 3], "Expected [0, 1, 2, 3]: borders must be proper."
    assert prefix_function("") == [] and prefix_function("x") == [0], "'' gives [], one letter gives [0]."


def test_fallback():
    got = prefix_function("aabaaab")
    assert got == [0, 1, 0, 1, 2, 2, 3], (
        f"Expected [0, 1, 0, 1, 2, 2, 3], got {got}. At i = 5 the border 2 cannot grow ('b' != 'a'); fall back "
        "to pi[1] = 1 and compare again: 'a' == 'a' gives 2. Use pi[k - 1], not pi[k].")
    assert prefix_function("abacabab") == [0, 0, 1, 0, 1, 2, 3, 2], "The string of p013."


def test_random_against_definition():
    rng = random.Random(1514)
    for _ in range(1500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 14)))
        want = slow(s)
        got = prefix_function(s)
        assert got == want, f"prefix_function({s!r}): expected {want}, got {got}."


def test_long_strings():
    code = (
        "import random\n"
        "from solution import prefix_function\n"
        "rng = random.Random(14)\n"
        "n = 5 * 10**5\n"
        "a = prefix_function('a' * (n - 1) + 'b')\n"
        "b = prefix_function(''.join(rng.choice('ab') for _ in range(n)))\n"
        "c = prefix_function('abaab' * (n // 5))\n"
        "print(sum(a), a[-1], sum(b), max(b), c[-1])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for strings of 5 * 10**5 characters. Worst case: repeated pattern like aaaa...b. "
        "Checking every border length from scratch is O(n**2) or worse; keep k and fall back with pi[k - 1].")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    want = ["124999250001", "0", "865765", "20", "499995"]
    assert r.stdout.split() == want, f"Long strings: expected {want}, got {r.stdout.split()}."
