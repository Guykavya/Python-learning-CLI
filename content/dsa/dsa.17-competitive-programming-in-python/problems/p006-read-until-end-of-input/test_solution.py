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


def test_example_with_trailing_space_and_blank_line():
    assert run("1 2\n\n3 \n") == ["3", "0", "3", "total: 6"], (
        "A blank line must give 0, and a trailing space must not break int().")


def test_empty_input():
    assert run("") == ["total: 0"], "No lines at all: print only the total line."


def test_no_final_newline():
    assert run("5 5") == ["10", "total: 10"]


def test_windows_line_endings_and_tabs():
    assert run("1 2\r\n3\r\n") == ["3", "3", "total: 6"], "Use line.split() (no argument): it also removes \\r."
    assert run("4\t5\n") == ["9", "total: 9"]


def test_whitespace_only_line_and_negatives():
    assert run("   \n-3 1\n") == ["0", "-2", "total: -2"]


def test_many_lines():
    rng = random.Random(6)
    lines = []
    sums = []
    for _ in range(100000):
        k = rng.randint(0, 4)
        nums = [rng.randint(-1000, 1000) for _ in range(k)]
        lines.append(" ".join(map(str, nums)))
        sums.append(sum(nums))
    want = [str(s) for s in sums] + [f"total: {sum(sums)}"]
    assert run("\n".join(lines) + "\n", timeout=10) == want
