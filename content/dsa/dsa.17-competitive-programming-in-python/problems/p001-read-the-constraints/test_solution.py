import re
import subprocess
import sys
import time
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")

RUNNER = r"""
import builtins, runpy, sys
calls = {"input": 0, "write": 0}
_input = builtins.input
def counted_input(*a):
    calls["input"] += 1
    return _input(*a)
builtins.input = counted_input
class W:
    def __init__(self, real):
        self.real = real
    def write(self, x):
        calls["write"] += 1
        return self.real.write(x)
    def __getattr__(self, name):
        return getattr(self.real, name)
sys.stdout = W(sys.stdout)
try:
    runpy.run_path(sys.argv[1], run_name="__main__")
finally:
    sys.stdout.real.flush()
    sys.stderr.write("\nCALLS %d %d\n" % (calls["input"], calls["write"]))
"""


def run_counted(stdin, timeout=20):
    """Run solution.py; return (stdout, stderr, input_calls, write_calls, seconds)."""
    t0 = time.perf_counter()
    try:
        r = subprocess.run([sys.executable, "-c", RUNNER, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"Your program did not finish in {timeout} seconds. It is far too slow for this input.")
    sec = time.perf_counter() - t0
    m = re.search(r"CALLS (\d+) (\d+)", r.stderr)
    ins, wr = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr[-800:]}"
    return r.stdout, r.stderr, ins, wr, sec


def run(stdin, timeout=20):
    """Plain run: return the printed lines (right-stripped)."""
    out = run_counted(stdin, timeout)[0]
    return [line.rstrip() for line in out.strip().splitlines()]



CASES = [
    ((10**5, 1), "n log n"),   # budget 1e7: n sqrt n = 3.2e7 is too much
    ((10**5, 2), "n log n"),   # budget 2e7: still below 3.2e7
    ((10**5, 4), "n sqrt n"),  # budget 4e7 >= 3.2e7, n^2 = 1e10 is not
    ((2 * 10**5, 2), "n log n"),   # n sqrt n = 8.9e7
    ((3000, 1), "n^2"),        # 9e6 <= 1e7
    ((5000, 1), "n sqrt n"),   # n^2 = 2.5e7 > 1e7, n sqrt n = 3.5e5
    ((200, 3), "n^3"),         # 8e6 <= 3e7
    ((20, 1), "2^n"),          # 2**20 = 1.05e6
    ((25, 1), "n^3"),          # 2**25 = 3.4e7 > 1e7, 25**3 = 15625
    ((10**6, 1), "n"),         # n log n = 2.0e7 > 1e7
    ((10**6, 3), "n log n"),   # 2.0e7 <= 3e7
    ((10**9, 10), "log n"),    # budget 1e8 < 1e9
]


def test_example():
    assert run("3\n100000 1\n1000000 1\n20 1\n") == ["n log n", "n", "2^n"]


def test_all_cases_together():
    stdin = f"{len(CASES)}\n" + "".join(f"{n} {s}\n" for (n, s), _ in CASES)
    got = run(stdin)
    want = [w for _, w in CASES]
    for (case, w), g in zip(CASES, got):
        assert g == w, (f"n = {case[0]}, s = {case[1]}: expected '{w}', got '{g}'. Budget is 10**7 * s; "
                        "a class fits when its cost is <= the budget.")
    assert len(got) == len(want), f"Expected {len(want)} lines, got {len(got)}."


def test_around_the_two_to_the_n_border():
    # n = 25, 2 seconds: 2**25 = 3.4e7 > 2e7, so n^3 (15625) is the slowest allowed class.
    # n = 24, 2 seconds: 2**24 = 1.7e7 <= 2e7, so 2^n is allowed again.
    assert run("2\n25 2\n24 2\n") == ["n^3", "2^n"], (
        "Compare 2**n with the budget 10**7 * s: 2**25 is just over 2*10**7, 2**24 is just under.")


def test_tiny_n():
    assert run("1\n1 1\n") == ["2^n"], "n = 1: every class costs at most 2 operations, so 2^n fits."


def test_huge_n_does_not_hang():
    assert run("1\n1000000000 1\n", timeout=5) == ["log n"], (
        "n = 10**9: computing 2 ** n would hang. Skip 2^n when n > 60. Only log n fits in 10**7 steps.")
