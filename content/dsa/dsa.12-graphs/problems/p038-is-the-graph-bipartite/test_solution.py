import random
from itertools import product

from solution import is_bipartite


def brute(n, edges):
    return any(all(c[u] != c[v] for u, v in edges) for c in product((0, 1), repeat=n))


def test_examples():
    assert is_bipartite(4, [(0, 1), (1, 2), (2, 3), (3, 0)]) is True, "A square (even cycle) is bipartite."
    assert is_bipartite(3, [(0, 1), (1, 2), (2, 0)]) is False, (
        "A triangle (odd cycle) is not bipartite: check an edge whose two ends got the SAME colour.")
    assert is_bipartite(5, [(0, 1), (2, 3), (3, 4), (4, 2)]) is False, (
        "The triangle 2-3-4 is in another piece: start a BFS from every uncoloured vertex.")
    assert is_bipartite(3, []) is True, "No edges: bipartite."


def test_self_loop_and_parallel_edges():
    assert is_bipartite(2, [(1, 1)]) is False, "A self loop joins a vertex with itself: not bipartite."
    assert is_bipartite(2, [(0, 1), (0, 1)]) is True, "Two parallel edges 0-1 are still fine (an even cycle of length 2)."


def test_random_against_brute_force():
    rng = random.Random(38)
    for _ in range(500):
        n = rng.randint(1, 9)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, n + 2))]
        if rng.random() < 0.6:
            edges = [(u, v) for u, v in edges if u != v]
        if rng.random() < 0.4:
            side = [rng.randint(0, 1) for _ in range(n)]
            edges = [(u, v) for u, v in edges if side[u] != side[v]]
        expected = brute(n, edges)
        assert is_bipartite(n, edges) is expected, (
            f"n={n}, edges={edges}: expected {expected}. Colour every piece, check every edge, count self loops.")


def test_long_path_and_ring():
    n = 100000
    path = [(i, i + 1) for i in range(n - 1)]
    crashed = False
    try:
        a = is_bipartite(n, path)
        b = is_bipartite(n, path + [(n - 1, 0)])
        c = is_bipartite(n - 1, [(i, i + 1) for i in range(n - 2)] + [(n - 2, 0)])
    except RecursionError:
        crashed = True
    assert not crashed, "RecursionError on a path of 100,000 vertices: use BFS (a queue) or an explicit stack."
    assert a is True, "A path is always bipartite."
    assert b is True, "A ring of 100,000 vertices (even) is bipartite."
    assert c is False, "A ring of 99,999 vertices (odd) is not bipartite."
