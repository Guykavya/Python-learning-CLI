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
    assert run("3\n1000000000000 6 1000000007\n6 3 7\n10 7 7\n") == ["333332169", "2", "-1"]


def test_small_primes_and_zero_numerator():
    assert run("3\n1 2 5\n0 4 3\n5 1 2\n") == ["3", "0", "1"], "1/2 mod 5 = 3 (2*3 = 6 = 1 mod 5); 0/4 = 0; 5/1 mod 2 = 1."


def test_denominator_multiple_of_p():
    assert run("2\n5 14 7\n5 0 7\n") == ["-1", "-1"], (
        "When b is divisible by p (also b = 0) there is no inverse: print -1, not 0.")


def test_large_values_satisfy_the_definition():
    rng = random.Random(10)
    primes = [10**9 + 7, 998244353, 1000003, 65537]
    cases = []
    for _ in range(100000):
        p = rng.choice(primes)
        cases.append((rng.randint(0, 10**18), rng.randint(0, 10**18), p))
    stdin = f"{len(cases)}\n" + "".join(f"{a} {b} {p}\n" for a, b, p in cases)
    got = run(stdin, timeout=10)
    assert len(got) == len(cases)
    for (a, b, p), g in zip(cases, got):
        if b % p == 0:
            assert g == "-1", f"b = {b} is a multiple of p = {p}: expected -1, got {g}."
        else:
            x = int(g)
            assert 0 <= x < p and x * b % p == a % p, (
                f"For a = {a}, b = {b}, p = {p} your answer {g} does not satisfy x * b = a (mod p) with 0 <= x < p.")
