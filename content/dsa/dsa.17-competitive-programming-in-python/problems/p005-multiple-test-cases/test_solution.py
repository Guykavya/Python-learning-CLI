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



import random


def test_example():
    assert run("2\n3\n1 2 6\n4\n5 5 5 5\n") == ["1", "0"]


def test_numbers_spread_over_lines_and_blank_lines():
    stdin = "2\n\n3\n1\n2 6\n\n4 5 5\n5 5\n"
    assert run(stdin) == ["1", "0"], (
        "The numbers of one test case may be on several lines, with blank lines in between. "
        "Read all tokens with sys.stdin.read().split() and walk through them.")


def test_single_element_and_negatives():
    assert run("1\n1\n7\n") == ["0"], "n = 1: the only number equals the average, not strictly greater."
    assert run("1\n3\n-5 1 2\n") == ["2"], "Sum -2: 1*3 = 3 > -2 and 2*3 = 6 > -2, but -5*3 = -15 is not."


def test_state_does_not_leak():
    assert run("3\n2\n1 3\n2\n1 3\n2\n1 3\n") == ["1", "1", "1"], (
        "Each test case must start with a fresh list and a fresh total.")


def test_many_cases():
    rng = random.Random(5)
    t = 50000
    lines = [str(t)]
    want = []
    for _ in range(t):
        n = 3
        a = [rng.randint(-10**9, 10**9) for _ in range(n)]
        lines.append(str(n))
        lines.append(" ".join(map(str, a)))
        s = sum(a)
        want.append(str(sum(1 for x in a if x * n > s)))
    got = run("\n".join(lines) + "\n", timeout=10)
    assert got == want, "Wrong answers on many small test cases."
