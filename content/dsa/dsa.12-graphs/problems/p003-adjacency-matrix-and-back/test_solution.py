import random

from solution import to_edges, to_matrix


def test_the_examples():
    assert to_matrix(3, [(0, 1), (1, 2)]) == [[0, 1, 0], [1, 0, 1], [0, 1, 0]], "Undirected: the edge (u, v) sets m[u][v] AND m[v][u]."
    assert [tuple(e) for e in to_edges([[0, 1, 0], [1, 0, 1], [0, 1, 0]])] == [(0, 1), (1, 2)], (
        "Undirected to_edges: list each edge once, as (u, v) with u <= v, in row order.")
    assert to_matrix(2, [(1, 0)], directed=True) == [[0, 0], [1, 0]], "Directed: only m[u][v] is set."
    assert [tuple(e) for e in to_edges([[0, 0], [1, 0]], directed=True)] == [(1, 0)], "Directed to_edges: every 1 in the table."


def test_rows_are_separate():
    m = to_matrix(3, [(0, 1)])
    assert m[1][1] == 0 and m[2][1] == 0, "Setting m[0][1] also set m[2][1]: the rows share one list. Did you write [[0] * n] * n?"


def test_self_loop_and_parallel_edges():
    assert to_matrix(2, [(1, 1)]) == [[0, 0], [0, 1]], "A self loop (1, 1) sets the diagonal cell m[1][1]."
    assert [tuple(e) for e in to_edges([[0, 0], [0, 1]])] == [(1, 1)], "to_edges must keep the diagonal (self loops): start the inner loop at u, not u + 1."
    assert to_matrix(2, [(0, 1), (0, 1), (1, 0)]) == [[0, 1], [1, 0]], "Parallel edges still give 1, not a count."


def test_empty():
    assert to_matrix(0, []) == [], "n = 0: an empty matrix."
    assert to_edges([]) == [], "An empty matrix has no edges."
    assert to_matrix(2, []) == [[0, 0], [0, 0]], "No edges: all zeros."


def test_round_trip_random():
    rng = random.Random(1203)
    for _ in range(200):
        n = rng.randint(1, 9)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 15))]
        for directed in (False, True):
            m = to_matrix(n, edges, directed)
            assert len(m) == n and all(len(row) == n for row in m), "The matrix must be n x n."
            for u in range(n):
                for v in range(n):
                    if directed:
                        want = int((u, v) in edges)
                    else:
                        want = int((u, v) in edges or (v, u) in edges)
                    assert m[u][v] == want, f"to_matrix({n}, {edges}, directed={directed}): cell [{u}][{v}] should be {want}."
            if directed:
                want_edges = sorted(set(edges))
            else:
                want_edges = sorted(set((min(u, v), max(u, v)) for u, v in edges))
            got = [tuple(e) for e in to_edges(m, directed)]
            assert got == want_edges, f"to_edges of that matrix (directed={directed}) should be {want_edges}, got {got}."


def test_two_hundred_vertices():
    n = 200
    edges = [(i, (i * 7 + 3) % n) for i in range(n)]
    m = to_matrix(n, edges)
    assert sum(map(sum, m)) == sum(2 if u != v else 1 for u, v in set((min(a, b), max(a, b)) for a, b in edges)), "Wrong number of 1s in a 200 x 200 matrix."
