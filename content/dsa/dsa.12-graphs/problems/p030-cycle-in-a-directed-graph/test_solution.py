import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import has_cycle_directed

HERE = pathlib.Path(__file__).parent


def model(n, edges):
    """Kahn: a cycle exists exactly when not every vertex can be removed."""
    indeg = [0] * n
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    done = 0
    while ready:
        u = ready.popleft()
        done += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return done < n


def test_examples():
    assert has_cycle_directed(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) is False, (
        "A diamond has NO directed cycle: vertex 3 is reached twice, but you can never get back. One 'visited' set "
        "is not enough; a cycle is an edge to a GREY vertex (on the current path), not to any seen vertex.")
    assert has_cycle_directed(3, [(0, 1), (1, 2), (2, 0)]) is True, "0 -> 1 -> 2 -> 0 is a cycle."
    assert has_cycle_directed(2, [(1, 1)]) is True, "A self loop (1, 1) is a cycle of length 1."
    assert has_cycle_directed(3, [(0, 1), (1, 0)]) is True, (
        "0 -> 1 -> 0 is a cycle in a directed graph. The undirected 'skip the parent' trick hides it.")


def test_cross_edges_to_finished_vertices():
    edges = [(0, 1), (1, 2), (0, 3), (3, 2), (3, 1), (4, 0), (4, 3)]
    assert has_cycle_directed(5, edges) is False, (
        "Many edges lead to vertices that are already finished (BLACK); none of them closes a cycle.")


def test_cycle_not_reachable_from_zero():
    assert has_cycle_directed(5, [(0, 1), (2, 3), (3, 4), (4, 2)]) is True, (
        "The cycle 2 -> 3 -> 4 -> 2 cannot be reached from 0: start a DFS from every WHITE vertex.")
    assert has_cycle_directed(4, [(1, 0), (2, 1), (3, 2)]) is False, "Edges pointing 'backwards' in numbering are not a cycle."


def test_no_edges():
    assert has_cycle_directed(3, []) is False, "No edges: no cycle."


def test_random_against_kahn():
    rng = random.Random(30)
    for _ in range(800):
        n = rng.randint(1, 8)
        m = rng.randint(0, 12)
        if rng.random() < 0.5:                                   # mostly DAGs: edges go from smaller to bigger
            pairs = [tuple(sorted(rng.sample(range(n), 2))) for _ in range(m)] if n > 1 else []
            pairs += [(rng.randrange(n), rng.randrange(n))] if rng.random() < 0.3 else []
        else:
            pairs = [(rng.randrange(n), rng.randrange(n)) for _ in range(m)]
        expected = model(n, pairs)
        assert has_cycle_directed(n, pairs) is expected, (
            f"n={n}, edges={pairs}: expected {expected}. A cycle is an edge to a GREY vertex; BLACK (finished) "
            "vertices are safe; search from every vertex.")


def run_limited(code, timeout):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=timeout, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_long_chain_iterative():
    code = (
        "from solution import has_cycle_directed\n"
        "n = 100000\n"
        "edges = [(i, i + 1) for i in range(n - 1)]\n"
        "print(has_cycle_directed(n, edges), has_cycle_directed(n, edges + [(n - 1, 0)]))\n"
    )
    r = run_limited(code, 10)
    assert r is not None, (
        "Time limit (10 s) on a chain of 100,000 vertices. Each vertex must be explored once: a finished vertex "
        "becomes BLACK and is never entered again (resetting it to WHITE makes the outer loop re-walk the chain).")
    assert "RecursionError" not in r.stderr, (
        "RecursionError on a chain of 100,000 vertices: use an explicit stack (an iterator per vertex).")
    assert r.returncode == 0, "Your code crashed on the long chain:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True"], (
        f"Chain of 100,000 vertices: expected False (no cycle), then True after closing it; got {r.stdout.split()}.")


def test_many_shared_descendants_time_limit():
    code = (
        "from solution import has_cycle_directed\n"
        "layers, width = 60, 30\n"
        "edges = []\n"
        "for L in range(layers - 1):\n"
        "    for a in range(width):\n"
        "        for b in range(width):\n"
        "            edges.append((L * width + a, (L + 1) * width + b))\n"
        "print(has_cycle_directed(layers * width, edges))\n"
    )
    r = run_limited(code, 10)
    assert r is not None, (
        "Time limit (10 s) on a layered DAG (60 layers of 30 vertices, every vertex points to the whole next "
        "layer). A finished vertex must stay BLACK: do not explore it again.")
    assert r.returncode == 0, "Your code crashed on the layered DAG:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False"], f"The layered DAG has no cycle; you printed {r.stdout.strip()!r}."
