import pathlib
import random
import subprocess
import sys

from solution import decode_ways

HERE = pathlib.Path(__file__).parent


def brute(s):
    """List every split into pieces, from the front (plain recursion, short strings only)."""
    if s == "":
        return 1
    if s[0] == "0":
        return 0
    total = brute(s[1:])
    if len(s) >= 2 and int(s[:2]) <= 26:
        total += brute(s[2:])
    return total


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_chapter_examples():
    assert decode_ways("226") == 3, "'226': 2 2 6, 22 6, 2 26 = 3 ways."
    assert decode_ways("12") == 2, "'12': 1 2 and 12 = 2 ways."
    assert decode_ways("1111") == 5, "'1111': 5 ways (a Fibonacci number)."


def test_zeros():
    assert decode_ways("06") == 0, (
        "'06' has no decoding: '0' is not a letter, and '06' is not a two-digit piece (it must be 10..26).")
    assert decode_ways("10") == 1, "'10' is only J. The single '0' is not a piece."
    assert decode_ways("2101") == 1, "'2101': only 2 10 1."
    assert decode_ways("0") == 0, "'0' alone: no decoding."
    assert decode_ways("100") == 0, "'100': '10' then '0', or '1' then '00': both invalid. 0 ways."
    assert decode_ways("30") == 0, "'30': 30 > 26 and '0' alone is invalid. 0 ways."


def test_two_digit_limits():
    assert decode_ways("26") == 2, "'26' is Z, or B F: 2 ways. 26 is still a valid piece (<= 26)."
    assert decode_ways("27") == 1, "'27': 27 > 26, so only 2 7."
    assert decode_ways("9") == 1, "One digit 1-9: one way."


def test_random_against_brute_force():
    rng = random.Random(1515)
    for _ in range(500):
        s = "".join(rng.choice("0112223456789") for _ in range(rng.randint(1, 14)))
        want = brute(s)
        got = decode_ways(s)
        assert got == want, (
            f"s={s!r}: expected {want} (all splits tried), got {got}. One digit is valid if it is not '0'; "
            "two digits if 10 <= value <= 26. f(0) = 1.")


def test_not_exponential():
    code = "from solution import decode_ways\nprint(decode_ways('1' * 60))\n"
    r = run_big(code, 5)
    assert r is not None, (
        "Time limit (5 s) for '1' * 60: exponential: add a memo. Without one, the recursion tries every "
        "split, about 1.6**60 of them.")
    assert r.returncode == 0, "Your code crashed on '1' * 60:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["2504730781961"], (
        f"'1' * 60 has 2504730781961 decodings (Fibonacci number F(61)), got {r.stdout.split()}.")


def test_long_strings():
    code = (
        "from solution import decode_ways\n"
        "out = []\n"
        "for s in ['1' * 5000, '10' * 2500, '226' * 1666, '1201' * 1250, '27' * 2500, '30' + '1' * 100]:\n"
        "    x = decode_ways(s)\n"
        "    out.append(str(x % 1000000007) + '/' + str(x.bit_length()))\n"
        "print(' '.join(out))\n"
    )
    r = run_big(code, 10)
    assert r is not None, "Time limit (10 s) for strings of length 5000: fill a table in one pass."
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for a string of length 5000: a memoised recursion is 5000 calls deep. "
            "Fill a table f[0..n] in a loop instead.")
    assert r.returncode == 0, "Your code crashed on long strings:\n" + r.stderr[-800:]
    want = ["419609281/3471", "1/1", "161357115/2641", "837752602/1250", "1/1", "0/0"]
    assert r.stdout.split() == want, (
        f"Long strings (shown as value mod 10**9+7 / bit length): expected {want}, got {r.stdout.split()}.")
