import random

from solution import dfs_order

def model(n, edges, start):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if u != v:
            adj[v].append(u)
    visited, order = set(), []
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for v in reversed(adj[u]):
            if v not in visited:
                stack.append(v)
    return order


def test_the_example():
    got = dfs_order(5, [(0, 1), (0, 2), (1, 3), (3, 2), (1, 4)], 0)
    assert got == [0, 1, 3, 2, 4], (
        f"Expected [0, 1, 3, 2, 4], got {got}. DFS goes 0 -> 1 -> 3 -> 2 before it backs up to 1 and tries 4. "
        "[0, 1, 2, 3, 4] is the BFS order.")


def test_does_not_mark_all_neighbours_early():
    edges = [(0, 1), (0, 2), (1, 2)]
    assert dfs_order(3, edges, 0) == [0, 1, 2], "From 0 go to 1, and from 1 to 2 (visited through 1, not as 0's second neighbour)."
    edges = [(0, 1), (0, 2), (1, 3), (3, 2)]
    got = dfs_order(4, edges, 0)
    assert got == [0, 1, 3, 2], (
        f"Expected [0, 1, 3, 2], got {got}. If you got [0, 1, 3] or a different order, do you mark every neighbour of u "
        "as visited before you go deep? Only mark a vertex when you actually visit it.")


def test_small_cases():
    assert dfs_order(1, [], 0) == [0], "One vertex."
    assert dfs_order(3, [(0, 0), (1, 2)], 0) == [0], "Only 0 is reachable from 0 (a self loop does not add it twice)."
    assert dfs_order(3, [(2, 1), (1, 0)], 0) == [0, 1, 2], "Undirected: (1, 0) also means 0 -> 1."


def test_two_calls_do_not_share_state():
    a = dfs_order(3, [(0, 1)], 0)
    b = dfs_order(3, [(0, 1)], 0)
    assert a == b == [0, 1], "Calling dfs_order twice gave different results: is `visited` a default argument or a global?"


def test_random_graphs():
    rng = random.Random(1212)
    for _ in range(400):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 18))]
        s = rng.randrange(n)
        want = model(n, edges, s)
        got = dfs_order(n, edges, s)
        assert got == want, f"dfs_order({n}, {edges}, {s}) should be {want}, got {got}."


def test_medium_graph():
    rng = random.Random(1213)
    n = 300
    edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(600)]
    assert dfs_order(n, edges, 0) == model(n, edges, 0), "Wrong order on a random graph with 300 vertices and 600 edges."
