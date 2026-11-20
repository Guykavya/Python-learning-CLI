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
    assert run("3 4\n#..S\n.#..\nE..#\n") == ["1 4 3 1 3"]


def test_windows_line_endings():
    assert run("3 4\r\n#..S\r\n.#..\r\nE..#\r\n") == ["1 4 3 1 3"], (
        "Lines end with \\r\\n. split() removes it; with readline() use .rstrip().")


def test_one_row_and_no_walls():
    assert run("1 2\nSE\n") == ["1 1 1 2 0"]
    assert run("2 1\nE\nS\n") == ["2 1 1 1 0"], "A column grid: n != m."


def test_large_grid():
    rng = random.Random(7)
    n, m = 1000, 1000
    grid = [[rng.choice(".#") for _ in range(m)] for _ in range(n)]
    sr, sc = rng.randrange(n), rng.randrange(m)
    er, ec = (sr + 1) % n, rng.randrange(m)
    grid[sr][sc] = "S"
    grid[er][ec] = "E"
    walls = sum(row.count("#") for row in map("".join, grid))
    stdin = f"{n} {m}\n" + "\n".join("".join(row) for row in grid) + "\n"
    out, err, ins, wr, sec = run_counted(stdin)
    assert out.split() == [str(sr + 1), str(sc + 1), str(er + 1), str(ec + 1), str(walls)], "Wrong answer on a 1000x1000 grid."
    assert ins <= 1000, f"input() was called {ins} times; read the whole grid at once."
    assert sec < 5, f"{sec:.1f} s for a 1000x1000 grid is too slow. Use row.find / row.count instead of looping over every cell."
