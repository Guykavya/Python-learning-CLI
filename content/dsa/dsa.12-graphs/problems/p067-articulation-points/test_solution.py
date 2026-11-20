import random
import subprocess
import sys
from pathlib import Path

from solution import articulation_points

HERE = Path(__file__).parent

def run_big(code, seconds=20):
    """Run code that imports your solution in its own process: a deep recursion or a slow loop
    cannot take the test run down with it."""
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=seconds)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if r.returncode != 0:
        if "RecursionError" in r.stderr or "maximum recursion depth" in r.stderr:
            return "RECURSION"
        return "CRASH: " + r.stderr[-600:]
    return r.stdout.strip()


def components(n, edges, removed=None):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        if removed not in (u, v):
            adj[u].append(v)
            adj[v].append(u)
    seen = set()
    count = 0
    for s in range(n):
        if s == removed or s in seen:
            continue
        count += 1
        seen.add(s)
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
    return count


def brute(n, edges):
    """Remove each vertex: it is a cut vertex if the rest falls into more pieces than before (minus itself)."""
    base = components(n, edges)
    out = []
    for u in range(n):
        alone = not any(u in e for e in edges)
        if components(n, edges, removed=u) > base - (1 if alone else 0):
            out.append(u)
    return out


def test_the_examples():
    got = articulation_points(5, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4)])
    assert got == [1, 3], f"removing 1 cuts {{0, 2}} from {{3, 4}}, removing 3 cuts off 4: expected [1, 3], got {got}."
    got = articulation_points(3, [(0, 1), (1, 2), (2, 0)])
    assert got == [], f"a triangle has no cut vertex; got {got}."


def test_the_root_rule():
    got = articulation_points(3, [(0, 1), (0, 2)])
    assert got == [0], (
        f"0 is the centre of a star: removing it separates 1 and 2. Expected [0], got {got}. "
        "The root is a cut vertex when it has two or more DFS children.")
    got = articulation_points(3, [(0, 1), (1, 2)])
    assert got == [1], (
        f"on the path 0 - 1 - 2 only the middle vertex cuts; got {got}. If 0 is in your answer, you used the "
        "normal rule for the root (it is always true there): count the root's DFS children instead.")


def test_root_neighbours_are_not_root_children():
    got = articulation_points(4, [(0, 1), (0, 2), (1, 2), (2, 3)])
    assert got == [2], (
        f"0 has two neighbours (1 and 2) but they are joined, so 0 is not a cut vertex; 2 cuts off 3. Expected [2], got {got}.")


def test_greater_or_equal():
    # 0 - 1, and a triangle 1 2 3: the triangle can climb back to 1 but not above it.
    got = articulation_points(4, [(0, 1), (1, 2), (2, 3), (3, 1)])
    assert got == [1], (
        f"removing 1 cuts 0 off from the rest of the triangle; expected [1], got {got}. The rule is low[c] >= tin[u]: "
        "climbing back exactly to u does not help, because u is the vertex being removed.")


def test_disconnected_and_no_duplicates():
    got = articulation_points(7, [(0, 1), (1, 2), (3, 4), (4, 5), (4, 6)])
    assert got == [1, 4], f"two parts: 1 is the middle of 0 - 1 - 2, 4 is the centre of a star; expected [1, 4] once each, sorted. Got {got}."


def test_parallel_edges():
    got = articulation_points(3, [(0, 1), (0, 1), (1, 2)])
    assert got == [1], f"a doubled edge does not change cut vertices: 1 still cuts off 2. Got {got}."


def test_random_graphs_against_removing_each_vertex():
    rng = random.Random(67)
    for _ in range(400):
        n = rng.randint(1, 9)
        edges = []
        for _ in range(rng.randint(0, 14)):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                edges.append((u, v))
        want = brute(n, edges)
        got = articulation_points(n, edges)
        assert got == want, f"articulation_points({n}, {edges}): expected {want}, got {got}."


BIG = """
from solution import articulation_points
n = 100000
line = [(i, i + 1) for i in range(n - 1)]
a = articulation_points(n, line)
b = articulation_points(n, line + [(n - 1, 0)])
print(len(a), a[0], a[-1], len(b))
"""


def test_a_line_of_100000_vertices():
    got = run_big(BIG)
    assert got != "RECURSION", "your DFS went 100,000 calls deep and hit the recursion limit. Write it with explicit frames."
    assert got != "TIMEOUT", "a line of 100,000 vertices did not finish in 20 seconds; removing each vertex and searching again is far too slow."
    assert got == "99998 1 99998 0", (
        f"on a line of 100,000 vertices every inner vertex (1 .. 99,998) is a cut vertex, and on a ring none; got {got} "
        "(count, first, last, count on the ring).")
