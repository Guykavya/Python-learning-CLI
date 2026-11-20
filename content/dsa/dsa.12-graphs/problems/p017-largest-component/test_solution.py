import random

from solution import largest_component


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
    groups = {}
    for v in range(n):
        groups.setdefault(label[v], []).append(v)
    return max(sorted(groups.values()), key=len)


def test_the_examples():
    got = largest_component(7, [(0, 1), (2, 3), (3, 4), (5, 6), (6, 2)])
    assert got == [2, 3, 4, 5, 6], f"The component {{2, 3, 4, 5, 6}} has 5 vertices; return them sorted. Got {got}."
    got = largest_component(4, [(2, 3), (0, 1)])
    assert got == [0, 1], f"A tie between {{0, 1}} and {{2, 3}}: return the one with the smallest vertex, [0, 1]. Got {got}. Use > not >=."
    assert largest_component(3, []) == [0], "No edges: every component has size 1; the one with the smallest vertex is [0]."


def test_returns_a_sorted_list():
    got = largest_component(4, [(3, 1), (1, 2)])
    assert isinstance(got, list), f"Return the list of vertices, not its size; got {got!r}."
    assert got == [1, 2, 3], f"Return the vertices sorted: [1, 2, 3], got {got}."


def test_random_graphs():
    rng = random.Random(1217)
    for _ in range(400):
        n = rng.randint(1, 12)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 10))]
        want = model(n, edges)
        got = largest_component(n, edges)
        assert got == want, f"largest_component({n}, {edges}) should be {want}, got {got}."


def test_long_chain():
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 2)]
    try:
        got = largest_component(n, edges)
    except RecursionError:
        raise AssertionError("RecursionError on a chain of 99,999 vertices: use an iterative DFS (a stack) or BFS.") from None
    assert len(got) == n - 1 and got[0] == 0 and got[-1] == n - 2, "The chain 0 .. 99998 is the largest component (99999 is alone)."
