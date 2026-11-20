import pathlib
import random
import subprocess
import sys

from solution import count_distinct

HERE = pathlib.Path(__file__).parent


def slow(s):
    return len({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})


def test_examples():
    assert count_distinct("aba") == 5, "a, b, ab, ba, aba: 5."
    assert count_distinct("abc") == 6, "All 6 substrings differ."
    assert count_distinct("") == 0 and count_distinct("z") == 1


def test_repeats_count_once():
    got = count_distinct("aaa")
    assert got == 3, f"'aaa' has the distinct substrings a, aa, aaa: 3, got {got}. Count each string once."
    assert count_distinct("abab") == 7, "a, b, ab, ba, aba, bab, abab: 7."


def test_random_against_a_set():
    rng = random.Random(1523)
    for _ in range(400):
        s = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 14)))
        want = slow(s)
        got = count_distinct(s)
        assert got == want, f"count_distinct({s!r}): expected {want}, got {got}."


def test_n_2000():
    code = (
        "import random\n"
        "from solution import count_distinct\n"
        "rng = random.Random(23)\n"
        "print(count_distinct(''.join(rng.choice('ab') for _ in range(2000))),\n"
        "      count_distinct('a' * 2000), count_distinct('ab' * 1000))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (60 s) for n = 2000. A set of all substrings holds about 1.3 * 10**9 characters; count only "
        "the new suffixes at each step with a Z-function.")
    assert r.returncode == 0, "Your code crashed for n = 2000 (out of memory?):\n" + r.stderr[-800:]
    want = ["1981445", "2000", "3999"]
    assert r.stdout.split() == want, f"n = 2000: expected {want}, got {r.stdout.split()}."
