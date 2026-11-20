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
from collections import deque


def expected(n, edges):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    depth = [-1] * (n + 1)
    depth[1] = 0
    q = deque([1])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if depth[v] < 0:
                depth[v] = depth[u] + 1
                q.append(v)
    return f"{max(depth[1:])} {sum(depth[1:])}"


def text(n, edges):
    return f"{n}\n" + "".join(f"{u} {v}\n" for u, v in edges)


def check(n, edges, what):
    r = None
    import subprocess
    r = subprocess.run([sys.executable, str(SOLUTION)], input=text(n, edges), capture_output=True,
                       text=True, timeout=30)
    assert "RecursionError" not in r.stderr, (
        f"RecursionError on {what}. A recursive DFS cannot go 2*10**5 levels deep in CPython. "
        "Use an explicit stack (a list with append/pop).")
    assert r.returncode == 0, f"Your program crashed on {what}.\n{r.stderr[-600:]}"
    assert r.stdout.split() == expected(n, edges).split(), f"Wrong answer on {what}."


def test_example():
    assert run("5\n1 2\n2 3\n1 4\n4 5\n") == ["2 6"]


def test_single_vertex():
    assert run("1\n") == ["0 0"], "n = 1 has no edges: the only vertex is the root at depth 0."


def test_edges_in_any_orientation():
    assert run("4\n3 2\n2 1\n4 1\n") == ["2 4"], "Edges are undirected: the pair '3 2' also connects 2 to 3."


def test_long_chain():
    n = 200000
    check(n, [(i, i + 1) for i in range(1, n)], "a path of 200000 vertices")


def test_shuffled_chain():
    rng = random.Random(8)
    n = 200000
    perm = list(range(2, n + 1))
    rng.shuffle(perm)
    order = [1] + perm
    edges = [(order[i + 1], order[i]) for i in range(n - 1)]
    rng.shuffle(edges)
    check(n, edges, "a shuffled path (root in the middle of the label order)")


def test_star_and_random_tree():
    n = 200000
    check(n, [(1, i) for i in range(2, n + 1)], "a star")
    rng = random.Random(81)
    edges = [(rng.randint(1, i - 1), i) for i in range(2, n + 1)]
    check(n, edges, "a random tree")
