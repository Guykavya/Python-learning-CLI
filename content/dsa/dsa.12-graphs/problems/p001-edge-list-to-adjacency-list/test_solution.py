import random

from solution import build_adj


def model(n, edges, directed):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if not directed and u != v:
            adj[v].append(u)
    return adj


def test_the_examples():
    assert build_adj(4, [(0, 1), (2, 0), (1, 2)]) == [[1, 2], [0, 2], [0, 1], []], (
        "Undirected: each edge (u, v) adds v to adj[u] AND u to adj[v], in the order of the edges. Vertex 3 has no edges and still gets [].")
    assert build_adj(3, [(0, 1), (2, 0)], directed=True) == [[1], [], [0]], (
        "Directed: the edge (u, v) only adds v to adj[u].")
    assert build_adj(2, [(1, 1)]) == [[], [1]], "A self loop (1, 1) appears once in adj[1], not twice."


def test_every_vertex_has_a_list():
    got = build_adj(5, [(0, 1)])
    assert len(got) == 5, f"n = 5 needs 5 lists (isolated vertices too), got {len(got)}."
    assert got[2] == [] and got[3] == [] and got[4] == [], "Vertices 2, 3, 4 have no edges: their lists are empty."
    assert build_adj(0, []) == [], "n = 0: an empty list of lists."
    assert build_adj(3, []) == [[], [], []], "No edges: three empty lists."


def test_lists_are_separate_objects():
    got = build_adj(3, [(0, 1)])
    assert got[2] == [], "adj[2] changed when you appended to adj[0]: did you write [[]] * n? That is ONE list repeated n times."
    assert got[0] is not got[1] and got[1] is not got[2], "Every vertex needs its own list object: use [[] for _ in range(n)]."


def test_order_follows_the_edges():
    got = build_adj(4, [(3, 0), (0, 2), (1, 0)])
    assert got[0] == [3, 2, 1], f"adj[0] must list 3, 2, 1 in the order of the edges, not sorted; got {got[0]}."


def test_parallel_edges_and_self_loops():
    assert build_adj(2, [(0, 1), (0, 1)]) == [[1, 1], [0, 0]], "Parallel edges are kept: (0, 1) twice gives two entries on each side."
    assert build_adj(2, [(0, 0), (0, 1)], directed=True) == [[0, 1], []], "Directed self loop: once in adj[0]."


def test_random_graphs():
    rng = random.Random(1201)
    for _ in range(300):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 20))]
        for directed in (False, True):
            want = model(n, edges, directed)
            got = build_adj(n, edges, directed)
            assert got == want, f"build_adj({n}, {edges}, directed={directed}) should be {want}, got {got}."


def test_big_input():
    n = 10 ** 5
    edges = [(i, i + 1) for i in range(n - 1)]
    got = build_adj(n, edges)
    assert got[0] == [1] and got[n - 1] == [n - 2] and got[500] == [499, 501], "A path of 100,000 vertices: wrong lists at the ends or in the middle."
