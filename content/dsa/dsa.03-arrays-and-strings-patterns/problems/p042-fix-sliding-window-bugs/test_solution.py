import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10, crash_hint: str = "") -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed. {crash_hint}\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


def ask(s, k, timeout=10, crash_hint=""):
    return run(f"{s}\n{k}\n", timeout=timeout, crash_hint=crash_hint)


def brute(s, k):
    best = total = 0
    for i in range(len(s)):
        seen = set()
        for j in range(i, len(s)):
            seen.add(s[j])
            if len(seen) > k:
                break
            best = max(best, j - i + 1)
            total += 1
    return [str(best), str(total)]


ZERO_HINT = ("If it is a KeyError or IndexError: a count dropped to 0 but the key stayed in the dictionary, so "
             "len(count) never goes down and the window shrinks past the end. Delete the key when its count is 0.")


def test_example():
    assert ask("eceba", 2) == ["3", "10"], "Expected 3 (the substring 'ece') and 10 for the example."


@pytest.mark.parametrize("s, k, want", [
    ("aaaa", 1, ["4", "10"]),
    ("ab", 2, ["2", "3"]),
    ("z", 1, ["1", "1"]),
])
def test_bug_off_by_one_length(s, k, want):
    got = ask(s, k, crash_hint=ZERO_HINT)
    assert got[:1] == want[:1], (
        f"Input {s!r}, k = {k}: expected longest {want[0]}, got {got[:1]}. The window s[left..right] holds "
        "right - left + 1 characters, not right - left (an off-by-one in the length).")
    assert got == want, f"Input {s!r}, k = {k}: expected {want}, got {got}."


@pytest.mark.parametrize("s, k, want", [
    ("aabbcc", 2, ["4", "17"]),
    ("abaccc", 2, ["4", "15"]),
    ("abcd", 1, ["1", "4"]),
])
def test_bug_zero_counts_not_deleted(s, k, want):
    got = ask(s, k, crash_hint=ZERO_HINT)
    assert got == want, (
        f"Input {s!r}, k = {k}: expected {want}, got {got}. A character whose count dropped to 0 has left the "
        "window, but if its key stays in the dictionary, len(count) still counts it. Delete keys at 0.")


@pytest.mark.parametrize("s, k, want", [
    ("eceba", 2, ["3", "10"]),
    ("aaabbbcab", 2, ["6", "29"]),
    ("abcabc", 1, ["1", "6"]),
])
def test_bug_if_instead_of_while(s, k, want):
    got = ask(s, k, crash_hint=ZERO_HINT)
    assert got[:1] == want[:1], f"Input {s!r}, k = {k}: expected longest {want[0]}, got {got[:1]}."
    assert got == want, (
        f"Input {s!r}, k = {k}: expected {want}, got {got}. The longest length is right but the count is too "
        "big: after one character leaves, the window can still have more than k distinct characters (when the "
        "leaving character appears again inside). Shrink with `while`, not `if`, so the window is good before "
        "you add right - left + 1.")


def test_k_zero():
    assert ask("abc", 0, crash_hint=ZERO_HINT) == ["0", "0"], (
        "With k = 0 no non-empty substring is good: the window must shrink to empty (left = right + 1) every time.")


def test_k_covers_everything():
    s = "abcabcab"
    n = len(s)
    assert ask(s, 26, crash_hint=ZERO_HINT) == [str(n), str(n * (n + 1) // 2)], (
        "When k is at least the number of distinct letters, every substring is good: longest n, count n(n+1)/2.")


def test_random_small_against_brute_force():
    rng = random.Random(42)
    for _ in range(30):
        n = rng.randint(1, 30)
        s = "".join(rng.choice("abcd") for _ in range(n))
        k = rng.randint(0, 4)
        got = ask(s, k, crash_hint=ZERO_HINT)
        assert got == brute(s, k), f"Input {s!r}, k = {k}: expected {brute(s, k)}, got {got}."


def test_large_speed():
    rng = random.Random(7)
    n = 200000
    s = "".join(rng.choice("abcde") for _ in range(n))
    k = 3
    # independent check: the window ending at r starts just after the (k+1)-th most recent distinct letter
    last = {}
    best = total = 0
    for r, ch in enumerate(s):
        last[ch] = r
        recent = sorted(last.values(), reverse=True)
        start = recent[k] + 1 if len(recent) > k else 0
        best = max(best, r - start + 1)
        total += r - start + 1
    got = ask(s, k, timeout=8, crash_hint=ZERO_HINT)
    assert got == [str(best), str(total)], (
        f"n = 200000: expected {[str(best), str(total)]}, got {got}. The window must move forward only; "
        "do not re-count each window from scratch.")
