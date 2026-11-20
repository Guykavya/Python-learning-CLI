import pathlib
import random
import subprocess
import sys

from solution import max_independent_set

HERE = pathlib.Path(__file__).parent


def brute(n, edges):
    """Every subset of nodes; keep those with no edge inside."""
    best = 0
    for mask in range(1 << n):
        if all(not (mask >> a & 1 and mask >> b & 1) for a, b in edges):
            best = max(best, bin(mask).count("1"))
    return best


def random_tree_edges(rng, n):
    edges = [(rng.randint(0, v - 1), v) for v in range(1, n)]
    rng.shuffle(edges)
    return [(b, a) if rng.random() < 0.5 else (a, b) for a, b in edges]


def test_chapter_examples():
    assert max_independent_set(5, [(0, 1), (1, 2), (2, 3), (3, 4)]) == 3, "A path of 5: nodes 0, 2, 4."
    assert max_independent_set(5, [(2, 0), (2, 1), (2, 3), (2, 4)]) == 4, "A star: the four leaves."


def test_tiny_trees():
    assert max_independent_set(1, []) == 1, "One node, no edges: the set {0}. take starts at 1."
    assert max_independent_set(2, [(1, 0)]) == 1, "Two linked nodes: only one of them."


def test_not_two_colours():
    edges = [(0, 1), (1, 2), (2, 3), (1, 4), (2, 5)]
    assert max_independent_set(6, edges) == 4, (
        "Expected 4 ({0, 3, 4, 5}). 'All even depths or all odd depths' gives only 3. "
        "skip(v) = sum of max(take(child), skip(child)).")


def test_edges_in_any_direction():
    assert max_independent_set(4, [(3, 2), (2, 1), (1, 0)]) == 2, (
        "Edges may be listed child-first: build an undirected adjacency list and let the BFS from 0 find parents.")


def test_random_against_brute():
    rng = random.Random(74)
    for _ in range(300):
        n = rng.randint(1, 12)
        edges = random_tree_edges(rng, n)
        want = brute(n, edges)
        got = max_independent_set(n, list(edges))
        assert got == want, (
            f"n={n}, edges={edges}: expected {want} (every subset tried), got {got}. "
            "take(v) = 1 + sum skip(child); skip(v) = sum max(take(child), skip(child)).")


def test_large_trees_iterative():
    code = (
        "import random\n"
        "import sys\n"
        "from solution import max_independent_set\n"
        "sys.setrecursionlimit(1000)\n"
        "n = 10**5\n"
        "path = [(v, v + 1) for v in range(n - 1)]\n"
        "star = [(0, v) for v in range(1, n)]\n"
        "rng = random.Random(7400)\n"
        "edges = [(rng.randint(0, v - 1), v) for v in range(1, n)]\n"
        "rng.shuffle(edges)\n"
        "edges = [(b, a) if rng.random() < 0.5 else (a, b) for a, b in edges]\n"
        "print(max_independent_set(n, path), max_independent_set(n, star), max_independent_set(n, edges))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=15, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (15 s) on trees of 100,000 nodes: the walk must be O(n)."
    assert "RecursionError" not in r.stderr, (
        "RecursionError on a path of 100,000 nodes: a recursive walk is 100,000 calls deep. Walk the BFS order "
        "backwards instead (children before parents), with no recursion. (This test puts the recursion limit back "
        "to the default 1000 after importing your file, so raising it does not help.)")
    assert r.returncode == 0, (
        "Your code crashed on the large trees:\n" + r.stderr[-800:])
    assert r.stdout.split() == ["50000", "99999", "59639"], (
        "Expected 50000 (path: every other node), 99999 (star: all leaves) and 59639 (random tree); "
        f"got {r.stdout.split()}.")
