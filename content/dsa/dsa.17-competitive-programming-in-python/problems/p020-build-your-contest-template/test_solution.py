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


def run_counted(stdin, timeout=20, script=None):
    """Run solution.py; return (stdout, stderr, input_calls, write_calls, seconds)."""
    t0 = time.perf_counter()
    try:
        r = subprocess.run([sys.executable, "-c", RUNNER, str(script or SOLUTION)], input=stdin,
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

import solution
from solution import Reader, Out, solve_cases, make_ncr, mod_div, tree_depths

HERE = Path(__file__).parent


def test_importing_reads_nothing():
    r = subprocess.run([sys.executable, "-c", "import solution"], cwd=HERE, input="", capture_output=True,
                       text=True, timeout=10)
    assert r.returncode == 0 and r.stdout == "", f"Importing the module must not read input or print.\n{r.stderr[-400:]}"


def test_reader():
    r = Reader("3\r\n10 -20 30\nabc\n..#\n#..\n")
    assert r.int() == 3
    assert r.ints(3) == [10, -20, 30], "ints(n) returns a list of n ints."
    assert r.has_more()
    assert r.word() == "abc"
    assert r.grid(2) == ["..#", "#.."], "grid(n) returns n tokens as strings, without \\r or spaces."
    assert not r.has_more(), "has_more() is False after the last token."
    assert Reader("").has_more() is False


def test_out():
    o = Out()
    assert o.text() == "", "No lines: the text is empty, not a blank line."
    o.add(1)
    o.add("x")
    o.add(2.5)
    assert o.text() == "1\nx\n2.5\n", "text() joins the lines with newlines and ends with one."


def test_solve_cases():
    def solve(r):
        n = r.int()
        return sum(r.ints(n))

    assert solve_cases(solve, "2\n3\n1 2 3\n2\n10 20\n") == "6\n30\n"
    assert solve_cases(solve, "0\n") == ""
    assert solve_cases(solve, "2\n\n1\n\n5\n\n2 7 8\n") == "5\n15\n", "Blank lines and line breaks inside a case are fine."


def test_mod_div():
    assert mod_div(6, 3, 7) == 2
    assert mod_div(10, 7, 7) is None, "b divisible by p: no inverse, return None."
    p = 10**9 + 7
    x = mod_div(10**18, 10**18 - 1, p)
    assert x * (10**18 - 1) % p == 10**18 % p


def test_make_ncr():
    p = 10**9 + 7
    ncr = make_ncr(2000, p)
    assert ncr(5, 2) == 10 and ncr(0, 0) == 1 and ncr(7, 7) == 1
    assert ncr(3, 5) == 0 and ncr(4, -1) == 0, "r > n or r < 0 gives 0."
    rng = random.Random(20)
    for _ in range(300):
        n = rng.randint(0, 2000)
        r = rng.randint(0, n)
        assert ncr(n, r) == math.comb(n, r) % p, f"C({n}, {r}) mod p is wrong."


def test_tree_depths():
    d = tree_depths(5, [(1, 2), (2, 3), (1, 4), (4, 5)])
    assert d == [-1, 0, 1, 2, 1, 2], f"Expected [-1, 0, 1, 2, 1, 2], got {d}. d[0] is unused (-1), d[root] = 0."
    d = tree_depths(4, [(2, 3)], root=2)
    assert d == [-1, -1, 0, 1, -1], "Unreachable vertices stay -1; the root can be any vertex."


# ---- the library solves four earlier problems on big inputs -----------------------------------------------

def test_p005_with_the_library():
    def solve(r):
        n = r.int()
        a = r.ints(n)
        s = sum(a)
        return sum(1 for x in a if x * n > s)

    rng = random.Random(205)
    t = 50000
    lines = [str(t)]
    want = []
    for _ in range(t):
        a = [rng.randint(-10**9, 10**9) for _ in range(3)]
        lines += ["3", " ".join(map(str, a))]
        s = sum(a)
        want.append(str(sum(1 for x in a if x * 3 > s)))
    stdin = "\n".join(lines) + "\n"
    script = HERE / "_use_p005.py"
    script.write_text(
        "from solution import main_from_stdin\n"
        "def solve(r):\n"
        "    n = r.int()\n"
        "    a = r.ints(n)\n"
        "    s = sum(a)\n"
        "    return sum(1 for x in a if x * n > s)\n"
        "main_from_stdin(solve)\n", encoding="utf-8")
    try:
        out, err, ins, wr, sec = run_counted(stdin, timeout=20, script=script)
    finally:
        script.unlink()
    assert out.split() == want, "The template gave wrong answers on 50000 small test cases."
    assert ins == 0 and wr <= 3, f"main_from_stdin must read with one read() and write once (input calls {ins}, writes {wr})."
    assert sec < 6, f"{sec:.1f} s"


def test_p007_grid_with_the_library():
    rng = random.Random(207)
    n = m = 1000
    rows = ["".join(rng.choice(".#") for _ in range(m)) for _ in range(n)]
    text = f"{n} {m}\n" + "\n".join(rows) + "\n"
    r = Reader(text)
    nn, mm = r.int(), r.int()
    got = r.grid(nn)
    assert got == rows and (nn, mm) == (n, m), "grid(n) must return exactly the n row strings."


def test_p008_chain_with_the_library():
    n = 200000
    d = tree_depths(n, [(i, i + 1) for i in range(1, n)])
    assert d[n] == n - 1 and sum(d[1:]) == n * (n - 1) // 2, "tree_depths must be iterative: a chain of 200000 vertices."


def test_p011_ncr_with_the_library():
    import time
    p = 10**9 + 7
    t0 = time.perf_counter()
    ncr = make_ncr(10**6, p)
    assert time.perf_counter() - t0 < 5, "Building the tables for N = 10**6 must take a few seconds at most."
    assert ncr(10**6, 0) == 1 and ncr(10**6, 10**6) == 1 and ncr(10**6, 1) == 10**6 % p
    assert (ncr(999999, 400000) + ncr(999999, 400001)) % p == ncr(10**6, 400001), "Pascal's rule must hold."
    assert ncr(10**6, 123456) == ncr(10**6, 10**6 - 123456), "Symmetry must hold."
