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



import random
from collections import Counter, deque


def test_examples():
    assert run("A\n2\naabbb\nabab\n") == ["3", "0"], "Problem A: count positions equal to the previous one."
    assert run("B\n1\n5 6\n1 5 3 3 3\n") == ["4"], "Problem B: (1,5) and three pairs among the three 3s."
    assert run("C\n3 4\n##..\n#..#\n..##\n") == ["2"], "Problem C: two islands."


def test_a_edge_cases():
    assert run("A\n3\na\naaaa\nabba\n") == ["0", "3", "1"]


def test_b_edge_cases():
    assert run("B\n2\n2 0\n0 0\n3 4\n2 2 2\n") == ["1", "3"], (
        "Equal numbers pair with each other: two 0s with k = 0 give 1 pair; three 2s with k = 4 give 3 pairs.")
    assert run("B\n1\n1 5\n5\n") == ["0"], "One element cannot pair with itself."


def test_c_edge_cases():
    assert run("C\n1 1\n#\n") == ["1"]
    assert run("C\n2 3\n...\n...\n") == ["0"]
    assert run("C\n2 2\n#.\n.#\n") == ["2"], "Diagonal cells are not connected."


def test_a_big():
    rng = random.Random(19)
    cases = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 4))) for _ in range(50000)]
    stdin = f"A\n{len(cases)}\n" + "\n".join(cases) + "\n"
    out, err, ins, wr, sec = run_counted(stdin, timeout=15)
    want = [str(sum(1 for i in range(1, len(s)) if s[i] == s[i - 1])) for s in cases]
    assert out.split() == want, "Problem A: wrong answers on many test cases."
    assert ins <= 1000 and wr <= 1000 and sec < 6, f"Problem A: input() calls {ins}, writes {wr}, {sec:.1f} s: read and write once."


def test_b_big():
    rng = random.Random(190)
    n = 200000
    a = [rng.randint(0, 3000) for _ in range(n)]
    k = 3000
    stdin = f"B\n1\n{n} {k}\n" + " ".join(map(str, a)) + "\n"
    out, err, ins, wr, sec = run_counted(stdin, timeout=20)
    cnt = Counter()
    ans = 0
    for x in a:
        ans += cnt[k - x]
        cnt[x] += 1
    assert out.split() == [str(ans)], "Problem B: wrong count on the big input."
    assert sec < 6, f"Problem B: {sec:.1f} s. A double loop over pairs needs about 2*10**10 steps; use a dictionary of counts."


def grid_islands(rows):
    n, m = len(rows), len(rows[0])
    seen = [[False] * m for _ in range(n)]
    cnt = 0
    for i in range(n):
        for j in range(m):
            if rows[i][j] == "#" and not seen[i][j]:
                cnt += 1
                seen[i][j] = True
                q = deque([(i, j)])
                while q:
                    x, y = q.popleft()
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        u, v = x + dx, y + dy
                        if 0 <= u < n and 0 <= v < m and rows[u][v] == "#" and not seen[u][v]:
                            seen[u][v] = True
                            q.append((u, v))
    return cnt


def test_c_big_random():
    rng = random.Random(1900)
    n = m = 500
    rows = ["".join("#" if rng.random() < 0.45 else "." for _ in range(m)) for _ in range(n)]
    stdin = f"C\n{n} {m}\n" + "\n".join(rows) + "\n"
    out, err, ins, wr, sec = run_counted(stdin, timeout=20)
    assert out.split() == [str(grid_islands(rows))], "Problem C: wrong island count on a random grid."
    assert sec < 6, f"Problem C: {sec:.1f} s."


def test_c_snake_needs_no_recursion():
    n, m = 600, 600
    rows = []
    for i in range(n):
        if i % 2 == 0:
            rows.append("#" * m)
        elif (i // 2) % 2 == 0:
            rows.append("." * (m - 1) + "#")
        else:
            rows.append("#" + "." * (m - 1))
    stdin = f"C\n{n} {m}\n" + "\n".join(rows) + "\n"
    try:
        out, err, ins, wr, sec = run_counted(stdin, timeout=30)
    except AssertionError as e:
        assert "RecursionError" not in str(e), (
            "RecursionError: the island is a snake of 180000 cells. A recursive DFS cannot follow it; use an explicit stack.")
        raise
    assert out.split() == ["1"], "A snake is a single island."
    assert sec < 6, f"Problem C: {sec:.1f} s on a snake."
