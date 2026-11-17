import random
import subprocess
import sys
from pathlib import Path

from solution import strongly_connected_components

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


def partition(n, comps):
    """Turn an answer into a set of frozensets, checking that it is a partition of 0..n-1."""
    seen = []
    for c in comps:
        seen.extend(c)
    assert sorted(seen) == list(range(n)), (
        f"every vertex 0..{n - 1} must appear in exactly one component; your components contain {sorted(seen)}.")
    return {frozenset(c) for c in comps}


def brute(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
    reach = []
    for s in range(n):
        seen = {s}
        stack = [s]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        reach.append(seen)
    return {frozenset(v for v in range(n) if v in reach[u] and u in reach[v]) for u in range(n)}


def show(p):
    return sorted(sorted(c) for c in p)


EX = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3), (6, 5), (6, 7), (7, 6)]


def test_the_examples():
    got = partition(8, strongly_connected_components(8, EX))
    assert got == brute(8, EX), f"expected {show(brute(8, EX))}, got {show(got)}."
    got = partition(3, strongly_connected_components(3, [(0, 1), (1, 2)]))
    assert got == {frozenset([0]), frozenset([1]), frozenset([2])}, (
        f"in 0 -> 1 -> 2 nobody can come back: three components of one vertex each; got {show(got)}. "
        "Strongly connected means reachable in BOTH directions.")


def test_direction_matters():
    got = partition(4, strongly_connected_components(4, [(0, 1), (1, 0), (1, 2), (2, 3), (3, 2)]))
    assert got == {frozenset([0, 1]), frozenset([2, 3])}, (
        f"{{0, 1}} and {{2, 3}} are two cycles joined by the one-way edge 1 -> 2: two components; got {show(got)}. "
        "If they were merged, your second pass searched the ORIGINAL graph instead of the reversed one, "
        "or took the vertices in the wrong finish order.")


def test_isolated_vertices_and_self_loops():
    got = partition(4, strongly_connected_components(4, [(1, 1), (2, 3)]))
    assert got == {frozenset([0]), frozenset([1]), frozenset([2]), frozenset([3])}, (
        f"no two vertices can reach each other: four single components (a self loop changes nothing); got {show(got)}.")


def test_an_edge_into_a_finished_component_does_not_merge():
    # Tarjan trap: the edge 3 -> 1 goes into the finished component {1, 2}.
    edges = [(0, 1), (1, 2), (2, 1), (0, 3), (3, 1), (3, 0)]
    got = partition(4, strongly_connected_components(4, edges))
    assert got == brute(4, edges), (
        f"expected {show(brute(4, edges))}, got {show(got)}. An edge into a component that is already closed "
        "must not join it (Tarjan: only vertices still on the stack count).")


def test_random_graphs():
    rng = random.Random(65)
    for _ in range(400):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 25))]
        want = brute(n, edges)
        got = partition(n, strongly_connected_components(n, edges))
        assert got == want, f"strongly_connected_components({n}, {edges}): expected {show(want)}, got {show(got)}."


BIG = """
from solution import strongly_connected_components
n = 100000
edges = [(i, i + 1) for i in range(n - 1)] + [(n - 1, 0)]
comps = strongly_connected_components(n, edges)
edges2 = [(i, i + 1) for i in range(n - 1)]
comps2 = strongly_connected_components(n, edges2)
print(len(comps), max(len(c) for c in comps), len(comps2), max(len(c) for c in comps2))
"""


def test_a_chain_of_100000_vertices():
    got = run_big(BIG)
    assert got != "RECURSION", (
        "your DFS went 100,000 calls deep and hit the recursion limit. Write it with an explicit stack: "
        "frames (vertex, iterator over its neighbours), and a vertex finishes when its iterator is empty.")
    assert got != "TIMEOUT", "a chain of 100,000 vertices did not finish in 20 seconds: both passes must be O(V + E)."
    assert got == "1 100000 100000 1", (
        f"a cycle through all 100,000 vertices is ONE component, and a chain without the back edge is 100,000 "
        f"components; got (components, largest, components, largest) = {got}.")
