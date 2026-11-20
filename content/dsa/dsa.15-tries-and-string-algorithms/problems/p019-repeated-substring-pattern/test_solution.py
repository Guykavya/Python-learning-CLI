import pathlib
import random
import subprocess
import sys

from solution import repeat_info

HERE = pathlib.Path(__file__).parent


def slow(s):
    n = len(s)
    for d in range(1, n):
        if n % d == 0 and s[:d] * (n // d) == s:
            return s[:d], n // d
    return s, 1


def test_examples():
    assert repeat_info("abcabcabc") == ("abc", 3)
    assert repeat_info("aaaa") == ("a", 4), "The SHORTEST block: 'a' four times, not 'aa' twice."
    assert repeat_info("z") == ("z", 1) and repeat_info("aa") == ("a", 2)


def test_period_must_divide():
    got = repeat_info("abcab")
    assert got == ("abcab", 1), (
        f"abcab has the smallest period 3, but 3 does not divide 5: expected ('abcab', 1), got {got}.")
    assert repeat_info("abaaba") == ("aba", 2)
    assert repeat_info("abaab") == ("abaab", 1)


def test_random_against_divisors():
    rng = random.Random(1519)
    for _ in range(1500):
        block = "".join(rng.choice("ab") for _ in range(rng.randint(1, 4)))
        s = block * rng.randint(1, 4)
        if rng.random() < 0.3:
            s = s + rng.choice("ab")
        want = slow(s)
        got = repeat_info(s)
        assert got == want, f"repeat_info({s!r}): expected {want}, got {got}."


def test_long_strings():
    code = (
        "from solution import repeat_info\n"
        "a = repeat_info('abcde' * 200000)\n"
        "b = repeat_info('a' * 999999 + 'b')\n"
        "c = repeat_info(('ab' * 499 + 'c') * 1000)\n"
        "print(a[0], a[1], b[1], len(c[0]), c[1])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (30 s) for strings of 10**6 characters: use the prefix function, O(n)."
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["abcde", "200000", "1", "999", "1000"], (
        f"Long strings: expected abcde 200000 1 999 1000, got {r.stdout.split()}.")
