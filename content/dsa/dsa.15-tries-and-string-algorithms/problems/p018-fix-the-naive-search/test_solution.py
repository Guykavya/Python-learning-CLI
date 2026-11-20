import pathlib
import random
import subprocess
import sys

from solution import find_all

HERE = pathlib.Path(__file__).parent


def old(text, pattern):
    n, m = len(text), len(pattern)
    found = []
    for start in range(n - m + 1):
        k = 0
        while k < m and text[start + k] == pattern[k]:
            k += 1
        if k == m:
            found.append(start)
    return found


def test_examples():
    assert find_all("abcabcabc", "cab") == [2, 5]
    assert find_all("aaaa", "aa") == [0, 1, 2], "Overlapping matches are included."
    assert find_all("ab", "abc") == [], "Pattern longer than the text: []."


def test_same_answers_as_before():
    rng = random.Random(1518)
    for _ in range(1500):
        text = "".join(rng.choice("ab") for _ in range(rng.randint(0, 20)))
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 5)))
        want = old(text, pattern)
        got = find_all(text, pattern)
        assert got == want, f"find_all({text!r}, {pattern!r}): the old version gave {want}, yours {got}."


def test_the_slow_log_line():
    code = (
        "from solution import find_all\n"
        "text = 'a' * 10**6\n"
        "print(len(find_all(text, 'a' * 9999 + 'b')), len(find_all(text + 'b', 'a' * 9999 + 'b')))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=20, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (20 s). Worst case: repeated pattern like aaaa...b. Every start matches 9999 letters and "
        "then fails: 10**10 comparisons. Use KMP so each text letter is read once.")
    assert r.returncode == 0, "Your code crashed on the long log line:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["0", "1"], f"Expected 0 and 1 matches, got {r.stdout.split()}."
