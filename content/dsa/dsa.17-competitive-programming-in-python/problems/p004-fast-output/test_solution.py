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
    assert run("4\n3 -2 0 10\n") == ["9", "4", "0", "100"]


def test_numbers_on_many_lines():
    assert run("3\n5\n6\n-7\n") == ["25", "36", "49"], "The numbers may be on one line or on many lines; split() handles both."


def test_many_lines_few_writes():
    rng = random.Random(4)
    n = 200000
    nums = [rng.randint(-10**6, 10**6) for _ in range(n)]
    stdin = f"{n}\n" + " ".join(map(str, nums)) + "\n"
    out, err, ins, wr, sec = run_counted(stdin)
    assert out.split() == [str(x * x) for x in nums], "Wrong output on a large input."
    assert wr <= 1000, (
        f"Your program wrote to standard output {wr} times. One write per line is slow on big outputs. "
        "Build a list of strings and write '\\n'.join(list) once.")
