import random

from solution import count_components


def model(n, edges):
    label = list(range(n))
    changed = True
    while changed:
        changed = False
        for u, v in edges:
            m = min(label[u], label[v])
            if label[u] != m or label[v] != m:
                label[u] = label[v] = m
                changed = True
    return len(set(label))


def test_the_examples():
    assert count_components(5, [(0, 1), (1, 2), (3, 4)]) == 2, "{0, 1, 2} and {3, 4}: two components."
    assert count_components(5, [(0, 1)]) == 4, "{0, 1}, {2}, {3}, {4}: isolated vertices are components too."
    assert count_components(3, [(0, 1), (1, 2), (2, 0)]) == 1, (
        "A triangle is ONE component. If you got 0, you computed n - len(edges): an edge that closes a cycle joins nothing new.")


def test_small_cases():
    assert count_components(1, []) == 1, "One vertex is one component."
    assert count_components(4, []) == 4, "No edges: every vertex is its own component."
    assert count_components(2, [(0, 0), (1, 1)]) == 2, "Self loops join nothing."
    assert count_components(2, [(0, 1), (1, 0), (0, 1)]) == 1, "Parallel edges count once."
    assert count_components(3, [(2, 1), (1, 0)]) == 1, "Edges given as (2, 1): store both directions."


def test_random_graphs():
    rng = random.Random(1216)
    for _ in range(400):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 12))]
        want = model(n, edges)
        got = count_components(n, edges)
        assert got == want, f"count_components({n}, {edges}) should be {want}, got {got}."


def test_long_chain_and_many_pieces():
    n = 100_000
    edges = [(i + 1, i) for i in range(n - 1)]
    try:
        assert count_components(n, edges) == 1, "A chain of 100,000 vertices is one component."
    except RecursionError:
        raise AssertionError("RecursionError on a chain of 100,000 vertices: use an iterative DFS (a stack) or BFS.") from None
    edges = [(2 * i, 2 * i + 1) for i in range(n // 2)]
    assert count_components(n, edges) == n // 2, "50,000 separate pairs: 50,000 components."
