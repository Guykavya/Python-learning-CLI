import pathlib
import random
import subprocess
import sys

from solution import count_palindromes, manacher

HERE = pathlib.Path(__file__).parent


def slow_p(s):
    t = "#" + "".join(ch + "#" for ch in s)
    out = []
    for i in range(len(t)):
        k = 0
        while i - k - 1 >= 0 and i + k + 1 < len(t) and t[i - k - 1] == t[i + k + 1]:
            k += 1
        out.append(k)
    return out


def slow_count(s):
    return sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])


def test_examples():
    assert manacher("babad") == [0, 1, 0, 3, 0, 3, 0, 1, 0, 1, 0]
    assert manacher("") == [0] and manacher("x") == [0, 1, 0]
    assert count_palindromes("aaa") == 6, "a three times, aa twice, aaa once: 6. Each centre gives (p + 1) // 2."
    assert count_palindromes("abba") == 6 and count_palindromes("abc") == 3


def test_cap_at_the_edge():
    got = manacher("abacaba")
    assert got == slow_p("abacaba"), (
        f"Expected {slow_p('abacaba')}, got {got}. Start inside the box at min(r - i, p[2c - i]), then expand.")


def test_hash_inside_s():
    assert manacher("#a#") == [0, 1, 0, 3, 0, 1, 0]
    assert count_palindromes("a#b#a") == slow_count("a#b#a")


def test_random_against_expansion():
    rng = random.Random(1526)
    for _ in range(800):
        s = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 16)))
        assert manacher(s) == slow_p(s), f"manacher({s!r}) should be {slow_p(s)}."
        assert count_palindromes(s) == slow_count(s), f"count_palindromes({s!r}) should be {slow_count(s)}."


def test_long_strings():
    code = (
        "import random\n"
        "from solution import count_palindromes, manacher\n"
        "n = 2 * 10**5\n"
        "rng = random.Random(26)\n"
        "r = ''.join(rng.choice('ab') for _ in range(n))\n"
        "print(count_palindromes('a' * n), max(manacher('a' * n)), count_palindromes(r), max(manacher(r)))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=30, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (30 s) for 2 * 10**5 equal letters. Expanding around every centre from scratch is O(n**2) "
        "there; copy the mirror's radius and expand only past the right edge.")
    assert r.returncode == 0, "Your code crashed on a long string:\n" + r.stderr[-800:]
    want = ["20000100000", "200000", "600866", "37"]
    assert r.stdout.split() == want, f"Long strings: expected {want}, got {r.stdout.split()}."
