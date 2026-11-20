import random

from solution import degrees


def test_the_examples():
    assert degrees(4, [(0, 1), (0, 2), (1, 2), (2, 3)]) == [2, 2, 3, 1], "Undirected: each edge adds 1 to BOTH of its ends."
    got = degrees(3, [(0, 1), (0, 2), (2, 0)], directed=True)
    assert tuple(got) == ([1, 1, 1], [2, 0, 1]), (
        f"Directed: return (indeg, outdeg). The edge (u, v) leaves u (outdeg[u] += 1) and arrives at v (indeg[v] += 1). Got {got}.")
    assert degrees(2, [(0, 0)]) == [2, 0], "An undirected self loop adds 2: both ends touch the vertex."


def test_isolated_and_empty():
    assert degrees(3, []) == [0, 0, 0], "No edges: every degree is 0, and the list still has n entries."
    assert degrees(0, []) == [], "n = 0: an empty list."
    assert tuple(degrees(2, [], directed=True)) == ([0, 0], [0, 0]), "Directed without edges: two lists of zeros."


def test_parallel_edges_count():
    assert degrees(2, [(0, 1), (1, 0)]) == [2, 2], "Parallel edges count every time."
    assert tuple(degrees(1, [(0, 0)], directed=True)) == ([1], [1]), "A directed self loop: in 1 and out 1."


def test_handshake_on_random_graphs():
    rng = random.Random(1202)
    for _ in range(300):
        n = rng.randint(1, 15)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 30))]
        deg = degrees(n, edges)
        assert len(deg) == n, f"Expected {n} degrees, got {len(deg)}."
        assert sum(deg) == 2 * len(edges), (
            f"Handshake lemma: the degrees must add up to 2 * {len(edges)} = {2 * len(edges)}, yours add up to {sum(deg)}. "
            "Does a self loop add 2? Does every edge count at both ends?")
        for u in range(n):
            want = sum((a == u) + (b == u) for a, b in edges)
            assert deg[u] == want, f"Vertex {u} in {edges}: degree {want}, got {deg[u]}."
        indeg, outdeg = degrees(n, edges, directed=True)
        assert sum(indeg) == len(edges) == sum(outdeg), "Directed: in-degrees and out-degrees each add up to the number of edges."
        for u in range(n):
            assert outdeg[u] == sum(a == u for a, b in edges), f"Out-degree of {u} in {edges} is wrong (edges that LEAVE u)."
            assert indeg[u] == sum(b == u for a, b in edges), f"In-degree of {u} in {edges} is wrong (edges that ARRIVE at u)."
