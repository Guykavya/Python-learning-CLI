import random

from solution import dfs_order


def recursive_model(n, edges, start):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        if u != v:
            adj[v].append(u)
    visited, order = set(), []

    def visit(u):
        visited.add(u)
        order.append(u)
        for v in adj[u]:
            if v not in visited:
                visit(v)

    visit(start)
    return order


def test_the_examples():
    got = dfs_order(5, [(0, 1), (0, 2), (1, 3), (3, 2), (1, 4)], 0)
    if got == [0, 2, 3, 1, 4]:
        why = "You pushed the neighbours in order: the last pushed is popped first. Push them reversed."
    else:
        why = ("Mark a vertex when you POP it (skip it if it is already visited), not when you push it: "
               "a vertex pushed earlier may be reached deeper first, as recursion does.")
    assert got == [0, 1, 3, 2, 4], f"Expected [0, 1, 3, 2, 4], got {got}. " + why
    got = dfs_order(4, [(0, 1), (0, 2), (1, 2), (2, 3)], 0)
    assert got == [0, 1, 2, 3], (
        f"Expected [0, 1, 2, 3], got {got}. The recursive DFS reaches 2 through 1. "
        "If 2 came after 3 or the order differs, you probably mark vertices when you PUSH them; mark them when you POP them, "
        "and skip a popped vertex that is already visited.")


def test_no_duplicates():
    got = dfs_order(3, [(0, 1), (0, 2), (1, 2), (2, 0)], 0)
    assert len(got) == len(set(got)), f"A vertex appears twice in {got}: skip a popped vertex that is already visited."


def test_random_graphs_match_the_recursive_order():
    rng = random.Random(1213)
    for _ in range(500):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 20))]
        s = rng.randrange(n)
        want = recursive_model(n, edges, s)
        got = dfs_order(n, edges, s)
        assert got == want, f"dfs_order({n}, {edges}, {s}) should be {want} (the recursive DFS order), got {got}."


def test_long_chain_without_recursion():
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    try:
        got = dfs_order(n, edges, 0)
    except RecursionError:
        raise AssertionError("RecursionError on a chain of 100,000 vertices: use an iterative DFS (an explicit stack).") from None
    assert got == list(range(n)), "On the chain 0-1-2-...-99999 the DFS order is 0, 1, 2, ..., 99999."


def test_big_random_graph():
    rng = random.Random(1214)
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    edges += [(rng.randrange(n), rng.randrange(n)) for _ in range(100_000)]
    rng.shuffle(edges)
    got = dfs_order(n, edges, 0)
    assert len(got) == n and len(set(got)) == n, "A connected graph with 100,000 vertices: every vertex exactly once."
    assert got == iterative_model(n, edges, 0), "Wrong DFS order on a random graph with 100,000 vertices (it must equal the recursive order)."

def iterative_model(n, edges, start):
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
