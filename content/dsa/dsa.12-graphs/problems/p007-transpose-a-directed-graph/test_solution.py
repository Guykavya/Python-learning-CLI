import copy
import random

from solution import can_reach, transpose


def reaches(adj, s, t):
    seen, stack = {s}, [s]
    while stack:
        u = stack.pop()
        if u == t:
            return True
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return False


def test_the_examples():
    adj = [[1, 2], [2], [], [2]]
    assert transpose(adj) == [[], [0], [0, 1, 3], []], "Every edge u -> v becomes v -> u: rev[v] gets u, in the order of u and of adj[u]."
    assert can_reach(adj, 2) == [0, 1, 2, 3], "Everyone reaches 2 (2 itself with zero edges)."
    assert can_reach(adj, 1) == [0, 1], "Only 0 reaches 1 (and 1 itself). If you got [1, 2] you searched forwards from 1."


def test_input_is_not_changed():
    adj = [[1], [2], [0]]
    before = copy.deepcopy(adj)
    transpose(adj)
    can_reach(adj, 0)
    assert adj == before, "transpose/can_reach changed the input lists: build new lists."


def test_order_parallel_edges_and_loops():
    adj = [[2, 2], [2, 1], [0]]
    assert transpose(adj) == [[2], [1], [0, 0, 1]], "Keep parallel edges (0 -> 2 twice) and self loops (1 -> 1); rev[2] lists 0, 0, 1 in order of u."


def test_random_against_brute_force():
    rng = random.Random(1207)
    for _ in range(200):
        n = rng.randint(1, 9)
        adj = [[rng.randrange(n) for _ in range(rng.randint(0, 3))] for _ in range(n)]
        rev = transpose(adj)
        want_rev = [[] for _ in range(n)]
        for u in range(n):
            for v in adj[u]:
                want_rev[v].append(u)
        assert rev == want_rev, f"transpose({adj}) should be {want_rev}, got {rev}."
        t = rng.randrange(n)
        want = [u for u in range(n) if reaches(adj, u, t)]
        got = can_reach(adj, t)
        assert got == want, f"can_reach({adj}, {t}) should be {want} (sorted), got {got}."


def test_long_chain():
    n = 100_000
    adj = [[i + 1] for i in range(n - 1)] + [[]]
    try:
        got = can_reach(adj, n - 1)
    except RecursionError:
        raise AssertionError("RecursionError on a chain of 100,000 vertices: use a BFS or an iterative DFS (an explicit stack).") from None
    assert len(got) == n and got[0] == 0 and got[-1] == n - 1, "On the chain 0 -> 1 -> ... -> 99999 every vertex reaches the last one."
    assert can_reach(adj, 0) == [0], "On the chain only 0 itself reaches 0."
