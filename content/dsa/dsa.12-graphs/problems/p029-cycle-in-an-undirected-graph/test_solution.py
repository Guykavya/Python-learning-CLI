import random

from solution import has_cycle


def model(n, edges):
    """A cycle exists exactly when there are more edges than n minus the number of pieces."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pieces = n
    for u, v in edges:
        a, b = find(u), find(v)
        if a != b:
            parent[a] = b
            pieces -= 1
    return len(edges) > n - pieces


def test_examples():
    assert has_cycle(4, [(0, 1), (1, 2), (2, 3)]) is False, (
        "A path has no cycle. If you said True, the edge back to the vertex you came from was counted as a cycle: "
        "skip the parent.")
    assert has_cycle(4, [(0, 1), (1, 2), (2, 0), (3, 3)]) is True, "A triangle is a cycle."
    assert has_cycle(2, [(0, 1), (0, 1)]) is True, (
        "Two parallel edges 0-1 form a cycle of length 2. Mark a vertex when you PUSH it: then 0, handling its own "
        "list, finds the second copy of 1 already seen.")
    assert has_cycle(6, [(0, 1), (2, 3), (3, 4), (4, 2)]) is True, (
        "The cycle 2-3-4 is not in the piece of vertex 0: start a search from every unseen vertex.")


def test_small_special_cases():
    assert has_cycle(1, []) is False, "One vertex, no edges: no cycle."
    assert has_cycle(1, [(0, 0)]) is True, "A self loop (0, 0) is a cycle."
    assert has_cycle(3, [(1, 1)]) is True, "A self loop on vertex 1 (not reachable from 0) is a cycle."
    assert has_cycle(5, [(0, 1), (0, 2), (0, 3), (0, 4)]) is False, "A star is a tree: no cycle."
    assert has_cycle(4, [(0, 1), (2, 3)]) is False, "Two separate edges: no cycle. Many pieces have fewer edges than n - 1."
    assert has_cycle(3, [(1, 0), (2, 1), (0, 1)]) is True, "Edges 1-0 and 0-1 are parallel (written in both directions): a cycle."


def test_forest_with_many_pieces():
    edges = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9)]
    assert has_cycle(10, edges) is False, "Five separate edges on 10 vertices: no cycle (5 edges, 5 pieces)."


def test_random_against_model():
    rng = random.Random(29)
    for _ in range(600):
        n = rng.randint(1, 9)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, n + 1))]
        if rng.random() < 0.5:
            edges = [(u, v) for u, v in edges if u != v]
        expected = model(n, edges)
        assert has_cycle(n, edges) is expected, (
            f"n={n}, edges={edges}: expected {expected}. Skip the parent, mark when you push, count self loops and parallel "
            "edges, and search every piece.")


def test_long_path_no_recursion():
    n = 100000
    edges = [(i, i + 1) for i in range(n - 1)]
    crashed = False
    try:
        open_path = has_cycle(n, edges)
        ring = has_cycle(n, edges + [(n - 1, 0)])
    except RecursionError:
        crashed = True
    assert not crashed, "RecursionError on a path of 100,000 vertices: use an explicit stack."
    assert open_path is False, "A path of 100,000 vertices has no cycle."
    assert ring is True, "Closing the long path into a ring makes a cycle."
