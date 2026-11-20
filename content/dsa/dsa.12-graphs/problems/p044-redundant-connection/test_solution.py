import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import redundant_edge

HERE = pathlib.Path(__file__).parent


def is_tree(n, edges):
    if len(edges) != n - 1:
        return False
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {0}
    queue = deque([0])
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)
    return len(seen) == n


def brute(n, edges):
    for i in range(len(edges) - 1, -1, -1):
        if is_tree(n, edges[:i] + edges[i + 1:]):
            return tuple(edges[i])


def random_case(rng, n):
    edges = [(rng.randrange(v), v) for v in range(1, n)]          # a random tree
    edges = [(v, u) if rng.random() < 0.5 else (u, v) for u, v in edges]
    present = {frozenset(e) for e in edges}
    while True:
        u, v = rng.sample(range(n), 2)
        if frozenset((u, v)) not in present:
            break
    edges.append((u, v))
    rng.shuffle(edges)
    perm = list(range(n))
    rng.shuffle(perm)
    return [(perm[u], perm[v]) for u, v in edges]


def test_examples():
    got = redundant_edge(3, [(0, 1), (0, 2), (1, 2)])
    assert isinstance(got, tuple), f"Return the edge as a tuple (u, v), not {type(got).__name__}."
    assert got == (1, 2), "The triangle's last edge in the list is (1, 2)."
    assert redundant_edge(5, [(0, 1), (1, 2), (2, 3), (1, 3), (0, 4)]) == (1, 3), (
        "The cycle is 1-2-3; its edges appear as (1,2), (2,3), (1,3): return the LAST one, (1, 3). The edge (0, 4) "
        "after it is not on the cycle.")
    assert redundant_edge(4, [(2, 1), (3, 1), (2, 3), (0, 3)]) == (2, 3), "Return (2, 3) exactly as written."


def test_edge_returned_as_written():
    got = redundant_edge(4, [(1, 0), (2, 1), (2, 0), (3, 2)])
    assert got == (2, 0), f"The cycle edge listed last is (2, 0); return it as a tuple exactly as written, got {got!r}."


def test_extra_edge_not_last_in_list():
    got = redundant_edge(6, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5)])
    assert got == (2, 0), f"The cycle 0-1-2 closes at (2, 0); the later edges are tree edges. Got {got!r}."


def test_random_against_brute_force():
    rng = random.Random(44)
    for _ in range(300):
        n = rng.randint(3, 12)
        edges = random_case(rng, n)
        expected = brute(n, edges)
        assert redundant_edge(n, edges) == expected, (
            f"n={n}, edges={edges}: expected {expected} (the cycle edge that appears LAST, as written).")


def test_big_input_time_limit():
    code = (
        "import random\n"
        "from solution import redundant_edge\n"
        "n = 100000\n"
        "edges = [(i, i + 1) for i in range(n - 1)]\n"
        "edges.insert(50000, (n - 1, 0))\n"
        "print(redundant_edge(n, edges))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (10 s) on 100,000 edges: use Union-Find, not a graph search per edge."
    assert "RecursionError" not in r.stderr, "RecursionError: write find with loops."
    assert r.returncode == 0, "Your code crashed on the big input:\n" + r.stderr[-800:]
    assert r.stdout.strip() == "(99998, 99999)", (
        f"Big ring: the cycle closes with the last edge in the list, (99998, 99999); got {r.stdout.strip()}.")
