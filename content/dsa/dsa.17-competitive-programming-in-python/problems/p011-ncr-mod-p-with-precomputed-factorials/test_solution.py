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



import math
import random

P = 10**9 + 7


def test_example():
    assert run("5\n5 2\n10 0\n10 10\n3 5\n0 0\n") == ["10", "1", "1", "0", "1"]


def test_r_larger_than_n_gives_zero():
    assert run("2\n4 7\n0 1\n") == ["0", "0"], "r > n means there is no way to choose: print 0 (not a negative index!)."


def test_small_values_against_math_comb():
    rng = random.Random(11)
    qs = [(rng.randint(0, 3000), rng.randint(0, 3000)) for _ in range(2000)]
    stdin = f"{len(qs)}\n" + "".join(f"{n} {r}\n" for n, r in qs)
    got = run(stdin)
    for (n, r), g in zip(qs, got):
        assert g == str(math.comb(n, r) % P if r <= n else 0), f"C({n}, {r}) mod p should be {math.comb(n, r) % P if r <= n else 0}, got {g}."


def test_large_values_pascal_and_symmetry():
    rng = random.Random(110)
    qs = []
    for _ in range(20000):
        n = rng.randint(1, 10**6 - 1)
        r = rng.randint(0, n)
        qs += [(n, r), (n, r + 1), (n + 1, r + 1), (n, n - r), (10**6, 500000)]
    stdin = f"{len(qs)}\n" + "".join(f"{n} {r}\n" for n, r in qs)
    got = [int(x) for x in run(stdin, timeout=15)]
    assert len(got) == len(qs)
    for i in range(0, len(qs), 5):
        (n, r) = qs[i]
        a, b, c, d, e = got[i:i + 5]
        assert (a + b) % P == c or r + 1 > n + 1, f"Pascal's rule fails at n = {n}, r = {r}: C(n,r) + C(n,r+1) must equal C(n+1,r+1)."
        assert a == d, f"Symmetry fails: C({n}, {r}) must equal C({n}, {n - r})."
    assert got[4] == got[9], "The same query gave different answers."
