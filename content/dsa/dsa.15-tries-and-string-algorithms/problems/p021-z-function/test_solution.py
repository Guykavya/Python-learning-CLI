import os
import pathlib
import random
import subprocess
import sys

from solution import z_function

HERE = pathlib.Path(__file__).parent


def slow(s):
    return [len(os.path.commonprefix([s, s[i:]])) for i in range(len(s))]


def test_examples():
    assert z_function("aabxaab") == [7, 1, 0, 0, 3, 1, 0]
    assert z_function("abacaba") == [7, 0, 1, 0, 3, 0, 1]
    assert z_function("aaaa") == [4, 3, 2, 1]
    assert z_function("") == [] and z_function("q") == [1], "'' gives []; z[0] = len(s)."


def test_cap_at_box_edge():
    got = z_function("aaab")
    assert got == [4, 2, 1, 0], (
        f"Expected [4, 2, 1, 0], got {got}. At i = 2 the box is [1, 3) and z[1] = 2, but only r - i = 1 letter "
        "is known: start from min(r - i, z[i - l]) = 1, then compare 'b' with 'a'.")
    got = z_function("aabaab")
    assert got == [6, 1, 0, 3, 1, 0], (
        f"Expected [6, 1, 0, 3, 1, 0], got {got}. Inside the box, start from min(r - i, z[i - l]); never trust "
        "the copy beyond r.")


def test_random_against_definition():
    rng = random.Random(1521)
    for _ in range(1500):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 16)))
        want = slow(s)
        got = z_function(s)
        assert got == want, f"z_function({s!r}): expected {want}, got {got}."


def test_long_strings():
    code = (
        "import random\n"
        "from solution import z_function\n"
        "n = 5 * 10**5\n"
        "a = z_function('a' * n)\n"
        "rng = random.Random(21)\n"
        "b = z_function(''.join(rng.choice('ab') for _ in range(n)))\n"
        "c = z_function('abaab' * (n // 5))\n"
        "print(sum(a), sum(b), max(b[1:]), c[5], c[3])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 5 * 10**5 characters. Worst case: a repeated pattern like aaaa..., where comparing "
        "from scratch at every i is O(n**2). Reuse the Z-box.")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    want = ["125000250000", "1000186", "22", "499995", "3"]
    assert r.stdout.split() == want, f"Long strings: expected {want}, got {r.stdout.split()}."
