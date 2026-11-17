import pathlib
import random
import subprocess
import sys

from solution import count_paths, longest_from

HERE = pathlib.Path(__file__).parent
MOD = 10**9 + 7


def all_paths(n, edges, source):
    """Enumerate every path from source (small DAGs only): yields (end vertex, total weight)."""
    out = [[] for _ in range(n)]
    for u, v, w in edges:
        out[u].append((v, w))
    stack = [(source, 0)]
    while stack:
        u, total = stack.pop()
        yield u, total
        for v, w in out[u]:
            stack.append((v, total + w))


def brute_longest(n, edges, source):
    best = [None] * n
    for v, total in all_paths(n, edges, source):
        if best[v] is None or total > best[v]:
            best[v] = total
    return best


def brute_count(n, edges, source, target):
    return sum(1 for v, _ in all_paths(n, edges, source) if v == target) % MOD


def random_dag(rng, n, m):
    perm = list(range(n))
    rng.shuffle(perm)
    edges = []
    for _ in range(m):
        a, b = sorted(rng.sample(range(n), 2))
        edges.append((perm[a], perm[b], rng.randint(-5, 9)))
    return edges


EX = [(0, 1, 2), (0, 2, 5), (1, 2, 4), (2, 3, 1), (1, 3, 1), (4, 3, 10)]


def test_examples():
    assert longest_from(5, EX, 0) == [0, 2, 6, 7, None], (
        "best should be [0, 2, 6, 7, None]: 0->1->2 (6) beats the direct 5, and vertex 4 is not reachable from 0, "
        "so it is None and its edge into 3 must not count (start every vertex at None, not 0).")
    assert count_paths(5, EX, 0, 3) == 3, "From 0 to 3 there are 3 paths: 0-1-2-3, 0-2-3, 0-1-3."
    assert count_paths(3, [(0, 1, 1), (0, 1, 7), (1, 2, 0)], 0, 2) == 2, (
        "Two parallel edges 0 -> 1 give two different paths to 2. Do not remove repeated edges.")


def test_source_and_unreachable():
    assert count_paths(3, [(0, 1, 1)], 2, 2) == 1, "source == target: the empty path counts, 1."
    assert count_paths(3, [(0, 1, 1)], 1, 0) == 0, "No path from 1 to 0: 0."
    assert longest_from(3, [(1, 0, 4), (2, 0, 1)], 2) == [1, None, 0], (
        "From 2: only the edge 2 -> 0 (weight 1) is usable; 1 is unreachable.")


def test_topological_order_needed():
    edges = [(3, 1, 1), (1, 0, 1), (2, 3, 1), (2, 1, 1)]
    assert longest_from(4, edges, 2) == [3, 2, 0, 1], (
        "Here the edges go from big to small numbers (2 -> 3 -> 1 -> 0). Looping over vertices 0, 1, 2, 3 uses "
        "best[1] before it is final; use a topological order.")
    assert count_paths(4, edges, 2, 0) == 2, "From 2 to 0: 2-3-1-0 and 2-1-0."


def test_negative_weights():
    edges = [(0, 1, -5), (1, 2, -1), (0, 2, -7)]
    assert longest_from(3, edges, 0) == [0, -5, -6], "Negative weights: 0->1->2 = -6 beats the direct -7 (largest total)."


def test_random_against_brute_force():
    rng = random.Random(39)
    for _ in range(300):
        n = rng.randint(1, 7)
        edges = random_dag(rng, n, rng.randint(0, 10)) if n > 1 else []
        s = rng.randrange(n)
        assert longest_from(n, edges, s) == brute_longest(n, edges, s), (
            f"longest_from({n}, {edges}, {s}): expected {brute_longest(n, edges, s)}. Use max, a topological order, "
            "and None for unreachable vertices.")
        t = rng.randrange(n)
        assert count_paths(n, edges, s, t) == brute_count(n, edges, s, t), (
            f"count_paths({n}, {edges}, {s}, {t}): expected {brute_count(n, edges, s, t)}.")


def test_big_dag_with_modulo():
    code = (
        "from solution import longest_from, count_paths\n"
        "n = 100000\n"
        "edges = []\n"
        "for i in range(n - 1):\n"
        "    edges.append((i + 1, i, 3))\n"
        "    edges.append((i + 1, i, -1))\n"
        "best = longest_from(n, edges, n - 1)\n"
        "print(best[0], best[n - 1], count_paths(n, edges, n - 1, 0))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (15 s) on a DAG of 100,000 vertices: one pass in topological order, O(n + E)."
    assert "RecursionError" not in r.stderr, "RecursionError on a path of 100,000 vertices: no recursion."
    assert r.returncode == 0, (
        "Your code crashed on the big DAG (a ValueError about 4300 digits means the count was not taken modulo "
        "10**9 + 7):\n" + r.stderr[-800:])
    expected = [str(3 * (100000 - 1)), "0", str(pow(2, 100000 - 1, MOD))]
    assert r.stdout.split() == expected, (
        f"Big DAG (doubled edges going down from 99999 to 0): expected {expected}, got {r.stdout.split()}. "
        "Take every count modulo 10**9 + 7.")
