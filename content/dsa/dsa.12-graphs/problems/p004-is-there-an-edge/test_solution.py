import pathlib
import random
import subprocess
import sys

from solution import EdgeIndex

HERE = pathlib.Path(__file__).parent


def test_the_examples():
    g = EdgeIndex(4, [(0, 1), (2, 0), (1, 2)])
    assert g.neighbours(0) == [1, 2], f"neighbours(0) must be [1, 2] in edge-list order, got {g.neighbours(0)}."
    assert g.neighbours(3) == [], "Vertex 3 has no edges."
    assert g.has_edge(0, 2) is True and g.has_edge(2, 0) is True, "Undirected: the edge (2, 0) works in both directions."
    assert g.has_edge(0, 3) is False, "There is no edge 0-3."
    d = EdgeIndex(2, [(0, 1)], directed=True)
    assert d.has_edge(0, 1) is True and d.has_edge(1, 0) is False, "Directed: (0, 1) does not give an edge 1 -> 0."
    assert d.neighbours(1) == [], "Directed: vertex 1 has no outgoing edges."


def test_self_loops_and_parallel_edges():
    g = EdgeIndex(2, [(0, 0), (0, 1), (0, 1)])
    assert g.neighbours(0) == [0, 1, 1], "A self loop once, parallel edges twice, in edge-list order."
    assert g.has_edge(0, 0) is True, "A self loop is an edge from 0 to 0."


def test_neighbours_returns_a_copy():
    g = EdgeIndex(2, [(0, 1)])
    g.neighbours(0).append(99)
    assert g.neighbours(0) == [1], "Changing the list returned by neighbours() changed the graph: return a copy (list(...))."


def test_random_against_a_model():
    rng = random.Random(1204)
    for _ in range(200):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 20))]
        for directed in (False, True):
            g = EdgeIndex(n, edges, directed)
            for u in range(n):
                want = []
                for a, b in edges:
                    if a == u:
                        want.append(b)
                    elif not directed and b == u:
                        want.append(a)
                assert g.neighbours(u) == want, f"EdgeIndex({n}, {edges}, directed={directed}).neighbours({u}) should be {want}."
                for v in range(n):
                    w = (u, v) in edges or (not directed and (v, u) in edges)
                    assert g.has_edge(u, v) == w, f"has_edge({u}, {v}) in {edges} (directed={directed}) should be {w}."


def test_star_is_fast_and_fits_in_memory():
    code = (
        "from solution import EdgeIndex\n"
        "n = 100000\n"
        "g = EdgeIndex(n, [(0, i) for i in range(1, n)])\n"
        "hits = sum(g.has_edge(0, v) for v in range(n - 1, -1, -1))\n"
        "back = sum(g.has_edge(v, 0) for v in range(n))\n"
        "print(hits, back)\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "A star with 100,000 vertices and 100,000 has_edge questions took more than 10 seconds. "
            "Do you search a LIST (v in adj[u] is O(degree))? Keep a set per vertex for has_edge.") from None
    assert r.returncode == 0, (
        "The star test crashed. If it is a MemoryError, you built an n x n matrix (10 billion cells for n = 100,000): "
        "use a set per vertex instead.\n" + r.stderr[-600:])
    assert r.stdout.split() == ["99999", "99999"], f"On the star, vertex 0 has 99,999 neighbours (and no self loop); got {r.stdout!r}."
