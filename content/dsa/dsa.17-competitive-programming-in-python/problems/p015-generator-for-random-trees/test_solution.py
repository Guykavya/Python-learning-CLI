import random
from collections import deque

import pytest

from solution import random_tree


def check_tree(n, edges):
    assert len(edges) == n - 1, f"A tree on {n} vertices has {n - 1} edges, got {len(edges)}."
    seen = set()
    parent = list(range(n + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        assert 1 <= u <= n and 1 <= v <= n, f"Edge {(u, v)} uses a label outside 1..{n}."
        assert u != v, f"Edge {(u, v)} is a loop."
        key = (min(u, v), max(u, v))
        assert key not in seen, f"Edge {key} appears twice."
        seen.add(key)
        ru, rv = find(u), find(v)
        assert ru != rv, f"Edge {(u, v)} closes a cycle."
        parent[ru] = rv


@pytest.mark.parametrize("shape", ["random", "path", "star"])
def test_valid_trees(shape):
    for n in (1, 2, 3, 10, 200):
        for seed in range(5):
            check_tree(n, random_tree(n, random.Random(seed), shape))


def test_default_shape_is_random():
    assert random_tree(30, random.Random(3)) == random_tree(30, random.Random(3), "random")


def test_same_seed_same_tree():
    assert random_tree(50, random.Random(9)) == random_tree(50, random.Random(9)), (
        "Use only the rng you receive for all randomness; then the same seed gives the same tree.")


def test_shapes():
    n = 50
    for seed in range(5):
        deg = [0] * (n + 1)
        for u, v in random_tree(n, random.Random(seed), "path"):
            deg[u] += 1
            deg[v] += 1
        assert max(deg) == 2 and deg.count(1) == 2, "A path has two leaves and every other vertex of degree 2."
        deg = [0] * (n + 1)
        for u, v in random_tree(n, random.Random(seed), "star"):
            deg[u] += 1
            deg[v] += 1
        assert max(deg) == n - 1 and deg.count(1) == n - 1, "A star has one vertex of degree n-1."


def test_variety():
    trees = set()
    for seed in range(100):
        trees.add(frozenset((min(u, v), max(u, v)) for u, v in random_tree(8, random.Random(seed))))
    assert len(trees) >= 80, f"Only {len(trees)} different trees out of 100 seeds: the generator is not random enough."


def test_labels_are_shuffled():
    count = 0
    for seed in range(100):
        edges = random_tree(10, random.Random(seed))
        adj = {i: [] for i in range(1, 11)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        depth = {1: 0}
        q = deque([1])
        parent = {1: 0}
        bad = False
        while q:
            x = q.popleft()
            for y in adj[x]:
                if y not in depth:
                    depth[y] = depth[x] + 1
                    parent[y] = x
                    if y < x:
                        bad = True
                    q.append(y)
        count += bad
    assert count >= 80, (
        "Rooted at vertex 1, a child almost always has a smaller label than its parent somewhere in a shuffled tree. "
        "Relabel the vertices with a random permutation.")


def test_orientation_and_order_are_random():
    firsts = []
    for seed in range(40):
        edges = random_tree(12, random.Random(seed))
        firsts.append(edges[0])
        assert any(u > v for u, v in edges) and any(u < v for u, v in edges), (
            "The two ends of an edge must be swapped at random: some edges (big, small), some (small, big).")
    assert len(set(firsts)) > 20, "Shuffle the order of the edges."


def test_unknown_shape():
    with pytest.raises(ValueError):
        random_tree(5, random.Random(0), "cactus")
