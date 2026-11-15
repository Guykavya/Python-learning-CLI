import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import bisect
import random


def ask(a, cmds, timeout=10):
    text = f"{len(a)}\n" + " ".join(map(str, a)) + f"\n{len(cmds)}\n" + "\n".join(cmds) + "\n"
    return run(text, timeout=timeout)


def check(a, cmds, want, why, timeout=10):
    got = ask(a, cmds, timeout=timeout)
    assert len(got) == len(want), (
        f"Log {a}, commands {cmds}: expected {len(want)} output lines, got {len(got)}: {got}. "
        "Print exactly one line per command, also for `error`.")
    for c, g, w in zip(cmds, got, want):
        assert g == w, f"Log {a}, command `{c}`: expected `{w}`, got `{g}`. {why}"


# ---------- a slow but obviously correct model, for small logs ----------

def is_int(s):
    d = s[1:] if s.startswith("-") else s
    return d.isdigit()


def model(a, line):
    n = len(a)
    parts = line.split()
    arity = {"sum": 2, "best": 1, "maxsub": 1, "longest_le": 1, "above": 2, "maxwin": 1}
    if not parts or parts[0] not in arity:
        return "error"
    name, args = parts[0], parts[1:]
    if len(args) != arity[name] or not all(is_int(x) for x in args):
        return "error"
    v = [int(x) for x in args]
    stretches = [(i, j) for i in range(n) for j in range(i, n)]
    if name == "sum":
        l, r = v
        return str(sum(a[l - 1:r])) if 1 <= l <= r <= n else "error"
    if name == "maxsub":
        return str(max(sum(x - v[0] for x in a[i:j + 1]) for i, j in stretches))
    if name == "longest_le":
        return str(max([j - i + 1 for i, j in stretches if sum(a[i:j + 1]) <= v[0]] + [0]))
    k = v[0]
    if not 1 <= k <= n:
        return "error"
    windows = [a[i:i + k] for i in range(n - k + 1)]
    if name == "best":
        return str(max(sum(w) for w in windows))
    if name == "above":
        return str(sum(1 for w in windows if sum(w) >= v[1] * k))
    return " ".join(str(max(w)) for w in windows)


# ---------- independent fast answers, for large logs ----------

def prefix(a):
    P = [0]
    for x in a:
        P.append(P[-1] + x)
    return P


def fast_maxsub(a, b):
    """Prefix-minimum version of Kadane."""
    best, low, s = None, 0, 0
    for x in a:
        s += x - b
        if best is None or s - low > best:
            best = s - low
        low = min(low, s)
    return str(best)


def fast_longest_le(a, S):
    """Prefix sums are non-decreasing (readings >= 0): binary search the earliest start for each end."""
    P = prefix(a)
    best = 0
    for r in range(1, len(P)):
        l = bisect.bisect_left(P, P[r] - S, 0, r)
        best = max(best, r - l)
    return str(best)


def fast_maxwin(a, k):
    """Block method: suffix maxima inside blocks of k plus prefix maxima of the next block."""
    n = len(a)
    pre, suf = a[:], a[:]
    for i in range(1, n):
        if i % k:
            pre[i] = max(pre[i - 1], a[i])
    for i in range(n - 2, -1, -1):
        if (i + 1) % k:
            suf[i] = max(suf[i + 1], a[i])
    return " ".join(str(max(suf[i], pre[i + k - 1])) for i in range(n - k + 1))


EXAMPLE = [3, 1, 4, 1, 5, 9, 2, 6]


# ======================================================================== the example

def test_example():
    cmds = ["sum 2 5", "best 3", "maxsub 4", "longest_le 10", "above 2 5", "maxwin 3",
            "sum 5 2", "mean 1 2", "best 0", "maxsub -2"]
    want = ["11", "17", "6", "4", "2", "4 4 5 9 9 9", "error", "error", "error", "47"]
    check(EXAMPLE, cmds, want, "This is the example from problem.md; follow its explanation line by line.")


# ======================================================================== sum

@pytest.mark.parametrize("cmd, want, why", [
    ("sum 1 8", "31", "the whole log"),
    ("sum 3 3", "4", "l = r: a single reading"),
    ("sum 1 1", "3", "the first reading: P[1] - P[0]"),
    ("sum 8 8", "6", "the last reading"),
    ("sum 0 3", "error", "positions start at 1"),
    ("sum 2 9", "error", "r is past the end (n = 8)"),
    ("sum 6 4", "error", "l > r is not a stretch"),
])
def test_sum(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why}) The sum of a[l..r] is P[r] - P[l - 1] with P[0] = 0.")


def test_sum_many_queries_fast():
    rng = random.Random(601)
    n = 200000
    a = [rng.randint(0, 10**9) for _ in range(n)]
    P = prefix(a)
    cmds, want = [], []
    for _ in range(200000):
        l = rng.randint(1, n)
        r = rng.randint(l, n)
        cmds.append(f"sum {l} {r}")
        want.append(str(P[r] - P[l - 1]))
    got = ask(a, cmds, timeout=10)
    assert got == want, (
        "200000 `sum` commands on 200000 readings give wrong answers or not one line each. If it timed out, you "
        "add up the range for every command (O(n) each); build prefix sums once and answer each in O(1).")


# ======================================================================== best

@pytest.mark.parametrize("cmd, want, why", [
    ("best 1", "9", "k = 1: the largest single reading"),
    ("best 8", "31", "k = n: only one window, the whole log"),
    ("best 2", "14", "5 + 9"),
    ("best 9", "error", "k > n: no window of 9 readings exists"),
    ("best -1", "error", "k must be at least 1"),
])
def test_best(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why})")


def test_best_and_above_wide_window():
    rng = random.Random(607)
    n, k = 200000, 100000
    a = [rng.randint(0, 10**9) for _ in range(n)]
    P = prefix(a)
    sums = [P[i + k] - P[i] for i in range(n - k + 1)]
    t = sorted(sums)[len(sums) // 2] // k
    check(a, [f"best {k}", f"above {k} {t}"],
          [str(max(sums)), str(sum(1 for x in sums if x >= t * k))],
          "With k = 100000, adding up each window again (sum of a slice) is about 10^10 steps. Slide the window "
          "or use prefix sums: each window sum is P[i + k] - P[i].", timeout=8)


# ======================================================================== maxsub

@pytest.mark.parametrize("cmd, want, why", [
    ("maxsub 0", "31", "baseline 0: every reading counts positively, the whole log wins"),
    ("maxsub 100", "-91", "every value minus 100 is negative: the best stretch is the single largest reading, 9 - 100. "
                          "The stretch is non-empty, so the answer is not 0"),
    ("maxsub 5", "4", "values minus 5: -2 -4 -1 -4 0 4 -3 1; the best is the 4 alone (or 0 4)"),
    ("maxsub 3", "10", "values minus 3: 0 -2 1 -2 2 6 -1 3; the best is 2 6 -1 3: crossing the -1 pays off"),
])
def test_maxsub(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why}) Run Kadane on a[i] - b, starting best at the first value, not at 0.")


def test_maxsub_large():
    rng = random.Random(602)
    a = [rng.randint(0, 10**9) for _ in range(200000)]
    b = 500000000
    check(a, [f"maxsub {b}"], [fast_maxsub(a, b)],
          "Kadane must be one pass; trying every stretch is O(n^2).", timeout=8)


# ======================================================================== longest_le

@pytest.mark.parametrize("cmd, want, why", [
    ("longest_le 31", "8", "S equals the total: the whole log fits"),
    ("longest_le 1000", "8", "S above the total"),
    ("longest_le 0", "0", "no reading of this log is 0, so nothing fits in 0"),
    ("longest_le -1", "0", "S is negative: even one reading (>= 0) is too much; print 0, do not crash"),
    ("longest_le 5", "2", "3 1, 1 4 and 4 1 fit; no three readings in a row stay within 5"),
    ("longest_le 8", "3", "3 1 4 = 8"),
])
def test_longest_le(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why}) Grow the window to the right; shrink from the left WHILE the sum is > S.")


def test_longest_le_with_zeros():
    a = [0, 0, 5, 0, 0, 0, 7]
    check(a, ["longest_le 0", "longest_le 5", "longest_le 6"], ["3", "6", "6"],
          "Zeros cost nothing: with S = 0 the longest run of zeros fits (length 3). The comparison is <= S, not < S.")


def test_longest_le_large():
    rng = random.Random(603)
    a = [rng.randint(0, 1000) for _ in range(200000)]
    S = 300000
    check(a, [f"longest_le {S}"], [fast_longest_le(a, S)],
          "A variable window moves each end at most n times: O(n). Re-summing each candidate is O(n^2).", timeout=8)


# ======================================================================== above

@pytest.mark.parametrize("cmd, want, why", [
    ("above 2 5", "2", "the example"),
    ("above 3 0", "6", "t = 0: every one of the n - k + 1 = 6 windows has average >= 0"),
    ("above 1 5", "3", "k = 1: the readings 5, 9 and 6"),
    ("above 4 -3", "5", "a negative t is allowed: all 5 windows qualify"),
    ("above 8 4", "0", "the only window has average 31 / 8 = 3.875 < 4"),
    ("above 3 6", "0", "average >= 6 means sum >= 18; the best window of 3 is 9 2 6 = 17"),
    ("above 0 1", "error", "k must be at least 1"),
    ("above 2", "error", "`above` needs two arguments"),
])
def test_above(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why}) Compare the window SUM with t * k: no floats, and >= (not >).")


def test_above_exact_average_counts():
    check([2, 4, 3, 3], ["above 2 3"], ["3"],
          "Windows 2 4, 4 3 and 3 3 have averages 3, 3.5 and 3: all are >= 3. An average exactly equal to t counts.")


# ======================================================================== maxwin

@pytest.mark.parametrize("cmd, want, why", [
    ("maxwin 3", "4 4 5 9 9 9", "the example"),
    ("maxwin 1", "3 1 4 1 5 9 2 6", "k = 1: each reading is its own maximum"),
    ("maxwin 8", "9", "k = n: one window"),
    ("maxwin 2", "3 4 4 5 9 9 6", "the 9 must leave once its window has passed"),
    ("maxwin 9", "error", "k > n"),
])
def test_maxwin(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why}) A monotonic deque of indices; drop the front when it leaves the window.")


def test_maxwin_large():
    rng = random.Random(604)
    a = [rng.randint(0, 10**9) for _ in range(200000)]
    k = 70000
    check(a, [f"maxwin {k}"], [fast_maxwin(a, k)],
          "max() over every window is O(n k); a monotonic deque is O(n).", timeout=8)


# ======================================================================== errors

@pytest.mark.parametrize("cmd, why", [
    ("", "a blank line"),
    ("   ", "a line with only spaces"),
    ("SUM 1 2", "names are lower case"),
    ("average 1 2", "an unknown command"),
    ("sum 1", "too few arguments"),
    ("sum 1 2 3", "too many arguments"),
    ("maxsub", "no argument"),
    ("best 1.5", "1.5 is not an integer"),
    ("best abc", "letters are not an integer"),
    ("best +3", "a '+' sign is not part of the integer format"),
    ("longest_le -", "a lone '-' has no digits"),
    ("maxwin 0", "k = 0 breaks 1 <= k <= n"),
])
def test_errors(cmd, why):
    check(EXAMPLE, [cmd, "sum 1 2"], ["error", "4"],
          f"({why}) Print `error` and keep going: the next command must still be answered.")


@pytest.mark.parametrize("cmd, want, why", [
    ("maxsub -5", str(31 + 8 * 5), "a negative baseline is a valid integer"),
    ("above 2 -1", "7", "a negative t is a valid integer"),
    ("sum 007 008", "8", "leading zeros are still digits: 7 to 8 is 2 + 6"),
    ("best   2", "14", "extra spaces between words are fine (split() handles them)"),
])
def test_valid_unusual_arguments(cmd, want, why):
    check(EXAMPLE, [cmd], [want], f"({why}) Do not reject it as an error.")


# ======================================================================== everything together

def test_random_small_logs_against_model():
    rng = random.Random(605)
    names = ["sum", "best", "maxsub", "longest_le", "above", "maxwin"]
    for _ in range(12):
        n = rng.randint(1, 9)
        a = [rng.randint(0, 9) for _ in range(n)]
        cmds = []
        for _ in range(15):
            name = rng.choice(names)
            if name == "sum":
                cmds.append(f"sum {rng.randint(0, n + 1)} {rng.randint(0, n + 1)}")
            elif name == "above":
                cmds.append(f"above {rng.randint(0, n + 1)} {rng.randint(-2, 10)}")
            elif name in ("maxsub", "longest_le"):
                cmds.append(f"{name} {rng.randint(-3, 30)}")
            else:
                cmds.append(f"{name} {rng.randint(0, n + 1)}")
        want = [model(a, c) for c in cmds]
        check(a, cmds, want, "Compare with a slow, obviously correct model of every command.")


def test_one_reading():
    check([7], ["sum 1 1", "best 1", "maxsub 10", "longest_le 6", "longest_le 7", "above 1 7", "maxwin 1"],
          ["7", "7", "-3", "0", "1", "1", "7"],
          "A log with one reading: every command must still work (n = 1).")


def test_large_mixed():
    rng = random.Random(606)
    n = 200000
    a = [rng.randint(0, 10**6) for _ in range(n)]
    P = prefix(a)
    k1, k2, t = 1000, 50000, 500000
    cmds = [f"best {k1}", f"above {k2} {t}", "maxsub 600000", "longest_le 5000000", f"maxwin {k1}"]
    want = [
        str(max(P[i + k1] - P[i] for i in range(n - k1 + 1))),
        str(sum(1 for i in range(n - k2 + 1) if P[i + k2] - P[i] >= t * k2)),
        fast_maxsub(a, 600000),
        fast_longest_le(a, 5000000),
        fast_maxwin(a, k1),
    ]
    for _ in range(50000):
        l = rng.randint(1, n)
        r = rng.randint(l, n)
        cmds.append(f"sum {l} {r}")
        want.append(str(P[r] - P[l - 1]))
    got = ask(a, cmds, timeout=10)
    assert len(got) == len(want), f"Expected {len(want)} lines, got {len(got)}."
    for c, g, w in zip(cmds, got, want):
        assert g == w, (
            f"Command `{c}` on a large log gives a wrong answer (expected starts with {w[:40]}, got {g[:40]}). "
            "Each heavy command must be one pass, and `sum` must use prefix sums.")
