import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

from solution import critical_connections

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


def connected(n, edges, a, b):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {a}
    stack = [a]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return b in seen


def brute(n, edges):
    """Remove each edge in turn: a bridge is one whose ends are then cut apart."""
    out = []
    for i, (u, v) in enumerate(edges):
        rest = edges[:i] + edges[i + 1:]
        if not connected(n, rest, u, v):
            out.append((u, v))
    return Counter(out)


def test_the_examples():
    got = critical_connections(4, [(0, 1), (1, 2), (2, 0), (1, 3)])
    assert sorted(got) == [(1, 3)], f"only the cable to server 3 is on no cycle: expected [(1, 3)], got {sorted(got)}."
    got = critical_connections(2, [(0, 1), (0, 1)])
    assert got == [], (
        f"two parallel cables between 0 and 1: removing one leaves the other, so neither is critical; got {got}. "
        "Skip only the EDGE you came by (its index), not every edge back to the parent vertex.")


def test_return_edges_as_given():
    got = critical_connections(3, [(1, 0), (2, 1)])
    assert sorted(got) == [(1, 0), (2, 1)], (
        f"on a path every cable is critical, and each must be returned exactly as listed: [(1, 0), (2, 1)]; got {sorted(got)}.")


def test_strictly_greater():
    # A triangle hanging from a line: 0 - 1, then triangle 1 2 3.
    got = critical_connections(4, [(0, 1), (1, 2), (2, 3), (3, 1)])
    assert sorted(got) == [(0, 1)], (
        f"only 0 - 1 is a bridge; the triangle edges are on a cycle. Got {sorted(got)}. If triangle edges appear, "
        "you used low[c] >= tin[p]; for bridges the rule is low[c] > tin[p].")


def test_chapter_network_and_disconnected_parts():
    net = [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 6), (6, 4), (6, 7)]
    got = sorted(critical_connections(8, net))
    assert got == [(1, 3), (3, 4), (6, 7)], f"the chapter's network has the bridges [(1, 3), (3, 4), (6, 7)]; got {got}."
    got = sorted(critical_connections(6, [(0, 1), (2, 3), (3, 4), (4, 2), (4, 5)]))
    assert got == [(0, 1), (4, 5)], f"two separate parts: both have a bridge. Expected [(0, 1), (4, 5)], got {got}. Start a DFS from every unvisited vertex."


def test_no_edges():
    assert critical_connections(3, []) == [], "no cables, no critical cables."


def test_random_graphs_against_removing_each_edge():
    rng = random.Random(66)
    for _ in range(400):
        n = rng.randint(1, 9)
        edges = []
        for _ in range(rng.randint(0, 14)):
            u, v = rng.randrange(n), rng.randrange(n)
            if u != v:
                edges.append((u, v))
        want = brute(n, edges)
        got = Counter(critical_connections(n, edges))
        assert got == want, f"critical_connections({n}, {edges}): expected {sorted(want.elements())}, got {sorted(got.elements())}."


BIG = """
from solution import critical_connections
n = 100000
line = [(i, i + 1) for i in range(n - 1)]
a = critical_connections(n, line)
ring = line + [(n - 1, 0)]
b = critical_connections(n, ring)
print(len(a), len(b))
"""


def test_a_line_of_100000_servers():
    got = run_big(BIG)
    assert got != "RECURSION", (
        "your DFS went 100,000 calls deep and hit the recursion limit. Write it with frames "
        "(vertex, edge you came by, iterator over its neighbours), as in chapter section 17.")
    assert got != "TIMEOUT", (
        "a line of 100,000 servers did not finish in 20 seconds. Removing every edge and searching again is "
        "O(E (V + E)); the low-link DFS is O(V + E).")
    assert got == "99999 0", f"a line of 100,000 servers has 99,999 bridges, and closing it into a ring leaves 0; got {got}."
