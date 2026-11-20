import pathlib
import random
import subprocess
import sys

from solution import all_periods, smallest_period

HERE = pathlib.Path(__file__).parent


def periods_slow(s):
    n = len(s)
    return [p for p in range(1, n + 1) if all(s[i] == s[i + p] for i in range(n - p))]


def test_examples():
    assert smallest_period("abcabcab") == 3 and all_periods("abcabcab") == [3, 6, 8], (
        "abcabcab: periods 3, 6 and 8 (the borders abcab, ab and the empty one).")
    assert smallest_period("aaaa") == 1 and smallest_period("abcd") == 4
    assert smallest_period("z") == 1 and all_periods("z") == [1], "One letter: period 1."


def test_cut_short_block():
    assert smallest_period("abcab") == 3, (
        "abcab has period 3 although 3 does not divide 5: the last block may be cut short.")


def test_not_only_multiples():
    got = all_periods("aabaa")
    assert got == [3, 4, 5], (
        f"aabaa: expected [3, 4, 5], got {got}. Walk all borders (aa, a, empty), not the multiples of 3.")


def test_random_against_definition():
    rng = random.Random(1517)
    for _ in range(1000):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 14)))
        want = periods_slow(s)
        assert all_periods(s) == want, f"all_periods({s!r}): expected {want}, got {all_periods(s)}."
        assert smallest_period(s) == want[0], f"smallest_period({s!r}): expected {want[0]}."


def test_long_strings():
    code = (
        "from solution import all_periods, smallest_period\n"
        "n = 5 * 10**5\n"
        "print(smallest_period('a' * (n - 1) + 'b'), len(all_periods('a' * n)),\n"
        "      all_periods('abaab' * (n // 5))[:3], smallest_period('ab' * (n // 2) + 'a'))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 5 * 10**5 characters. Worst case: repeated pattern like aaaa...b, where checking "
        "each p letter by letter is O(n**2). Use the prefix function.")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["500000", "500000", "[5,", "10,", "15]", "2"], (
        f"Long strings: expected 500000 500000 [5, 10, 15] 2, got {r.stdout.split()}.")
