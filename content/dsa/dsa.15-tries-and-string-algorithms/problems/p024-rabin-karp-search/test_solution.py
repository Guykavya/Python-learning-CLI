import pathlib
import random
import subprocess
import sys

from solution import rabin_karp, window_hashes

HERE = pathlib.Path(__file__).parent


def direct(s, B, M):
    h = 0
    for ch in s:
        h = (h * B + ord(ch)) % M
    return h


def by_find(text, pattern):
    if not pattern:
        return list(range(len(text) + 1))
    out, start = [], 0
    while (i := text.find(pattern, start)) != -1:
        out.append(i)
        start = i + 1
    return out


def test_window_hashes():
    got = window_hashes("abcabcab", 3, 31, 101)
    want = [direct("abcabcab"[i:i + 3], 31, 101) for i in range(6)]
    assert got == want, f"Expected {want}, got {got}. Rolling update: ((h - ord(front) * B**(m-1)) * B + ord(new)) % M."
    assert window_hashes("ab", 3, 31, 101) == [], "m > len(text): no windows."
    assert window_hashes("xyz", 3, 7, 11) == [direct("xyz", 7, 11)], "One window."


def test_window_hashes_random():
    rng = random.Random(1524)
    for _ in range(300):
        text = "".join(rng.choice("abz#") for _ in range(rng.randint(1, 20)))
        m = rng.randint(1, len(text))
        B, M = rng.choice([(31, 101), (131, 1_000_000_007), (2, 3), (257, 65537)])
        want = [direct(text[i:i + m], B, M) for i in range(len(text) - m + 1)]
        assert window_hashes(text, m, B, M) == want, f"window_hashes({text!r}, {m}, {B}, {M}) should be {want}."


def test_search_examples():
    assert rabin_karp("abababab", "abab") == [0, 2, 4]
    assert rabin_karp("aaaaa", "aa") == [0, 1, 2, 3] and rabin_karp("abc", "abcd") == []
    assert rabin_karp("ab", "") == [0, 1, 2], "The empty pattern occurs at every position."


def test_crafted_collision():
    text = "xxdiexcabx"
    assert direct("die", 31, 101) == direct("cab", 31, 101), "(test data: 'die' and 'cab' collide for (31, 101))"
    got = rabin_karp(text, "cab", params=((31, 101),), verify=False)
    assert got == [2, 6], (
        f"Trusting a single (31, 101) hash, 'die' at 2 is a false alarm and must be reported: expected [2, 6], "
        f"got {got}. Report every window whose hash equals the pattern's when verify is False.")
    got = rabin_karp(text, "cab", params=((31, 101),), verify=True)
    assert got == [6], f"With verify=True the false alarm is removed: expected [6], got {got}."
    got = rabin_karp(text, "cab", params=((31, 101), (37, 103)), verify=False)
    assert got == [6], (
        f"With two hash pairs, a window must match in BOTH: expected [6], got {got}.")


def test_random_against_find():
    rng = random.Random(15240)
    for _ in range(800):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 20)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        want = by_find(text, pattern)
        assert rabin_karp(text, pattern) == want, f"rabin_karp({text!r}, {pattern!r}) should be {want}."


def test_long_text():
    code = (
        "import random\n"
        "from solution import rabin_karp\n"
        "rng = random.Random(24)\n"
        "text = ''.join(rng.choice('ab') for _ in range(10**6))\n"
        "print(len(rabin_karp(text, text[5000:5020])), len(rabin_karp('a' * 10**6, 'a' * 999 + 'b')))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=60, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (60 s) for a text of 10**6 characters. Worst case: repeated pattern like aaaa...b with a "
        "1000-letter pattern; recomputing each window's hash from scratch is O(n * m). Roll the hash.")
    assert r.returncode == 0, "Your code crashed on a long text:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["2", "0"], f"Long text: expected 2 and 0 matches, got {r.stdout.split()}."
