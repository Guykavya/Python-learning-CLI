import pathlib
import random
import subprocess
import sys
from itertools import permutations

from solution import topo_kahn

HERE = pathlib.Path(__file__).parent
FUNC = topo_kahn


def has_order(n, edges):
    """Brute force on small graphs: does any permutation respect all edges?"""
    return any(all(p.index(u) < p.index(v) for u, v in edges) for p in permutations(range(n)))


def check(n, edges, got, label):
    assert isinstance(got, list), f"{label}: return a list, got {type(got).__name__}."
    assert not (got == [] and n > 0), (
        f"{label}: you returned [] (cycle), but this graph has NO cycle. "
        + ("Count every listed edge in the in-degree, also a repeated one." if "kahn" in __name__ or "kahn" in FUNC.__name__
           else "Meeting a finished (BLACK) vertex again is not a cycle; only a GREY one is."))
    assert sorted(got) == list(range(n)), (
        f"{label}: the order must contain every vertex 0..{n - 1} exactly once, got {got}. "
        "If vertices are missing, check that every vertex with in-degree 0 starts in the queue.")
    pos = {v: i for i, v in enumerate(got)}
    for u, v in edges:
        assert pos[u] < pos[v], (
            f"{label}: edge ({u}, {v}) says {u} comes before {v}, but your order {got} puts {v} first. "
            "Did you read the edge backwards?")


def test_examples():
    check(4, [(0, 1), (0, 2), (1, 3), (2, 3)], FUNC(4, [(0, 1), (0, 2), (1, 3), (2, 3)]), "diamond")
    assert FUNC(3, [(0, 1), (1, 2), (2, 0)]) == [], (
        "A cycle 0 -> 1 -> 2 -> 0 has no topological order: return [] (not a partial order, not None).")
    check(3, [], FUNC(3, []), "no edges")


def test_cycle_cases():
    assert FUNC(2, [(1, 1)]) == [], "A self loop (1, 1) is a cycle: return []."
    assert FUNC(5, [(0, 1), (1, 2), (2, 3), (3, 2), (3, 4)]) == [], (
        "The cycle 2 <-> 3 blocks 2, 3 and 4 (which comes after the cycle): return [], not the partial order [0, 1].")


def test_parallel_edges_and_many_sources():
    edges = [(0, 2), (0, 2), (1, 2), (2, 3), (4, 3)]
    check(5, edges, FUNC(5, edges), "parallel edge 0->2 listed twice, sources 0, 1, 4")
    edges = [(3, 0), (2, 0), (1, 0)]
    check(4, edges, FUNC(4, edges), "edges into vertex 0 (vertex 0 is NOT a source)")


def test_random_small_graphs():
    rng = random.Random(31)
    for _ in range(400):
        n = rng.randint(1, 6)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 7))]
        if rng.random() < 0.6:
            edges = [(min(u, v), max(u, v)) for u, v in edges if u != v]
            perm = list(range(n))
            rng.shuffle(perm)
            edges = [(perm[u], perm[v]) for u, v in edges]
        got = FUNC(n, edges)
        if has_order(n, edges):
            check(n, edges, got, f"n={n}, edges={edges}")
        else:
            assert got == [], f"n={n}, edges={edges} has a cycle: expected [], got {got}."


def test_big_graph():
    code = (
        "import random\n"
        "from solution import " + FUNC.__name__ + " as f\n"
        "n = 100000\n"
        "rng = random.Random(5)\n"
        "perm = list(range(n)); rng.shuffle(perm)\n"
        "edges = [(perm[i], perm[i + 1]) for i in range(n - 1)]\n"
        "edges += [(perm[a], perm[b]) for a, b in (sorted(rng.sample(range(n), 2)) for _ in range(100000))]\n"
        "order = f(n, edges)\n"
        "pos = [0] * n\n"
        "for i, v in enumerate(order): pos[v] = i\n"
        "print(len(order) == n and all(pos[u] < pos[v] for u, v in edges))\n"
        "print(f(n, edges + [(perm[-1], perm[0])]) == [])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (15 s) on 100,000 vertices and 200,000 edges: keep a queue of ready vertices; do not "
        "search all vertices for in-degree 0 after every step.")
    assert "RecursionError" not in r.stderr, "RecursionError on a chain of 100,000 vertices: use an explicit stack or queue."
    assert r.returncode == 0, "Your code crashed on the big graph:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "True"], (
        f"Big graph: expected a valid order, then [] after closing a cycle; got {r.stdout.split()}.")
