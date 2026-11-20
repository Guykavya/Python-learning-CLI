import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import has_cycle

HERE = pathlib.Path(__file__).parent


def model(graph):
    indeg = {u: 0 for u in graph}
    for u in graph:
        for v in graph[u]:
            indeg[v] += 1
    ready = deque(u for u in graph if indeg[u] == 0)
    removed = 0
    while ready:
        u = ready.popleft()
        removed += 1
        for v in graph[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    return removed < len(graph)


def test_teammates_tests_still_pass():
    assert has_cycle({"a": ["b"], "b": ["c"], "c": ["a"]}) is True, "a -> b -> c -> a is a cycle."
    assert has_cycle({"a": ["b"], "b": [], "c": []}) is False, "No circle here."


def test_the_complaint_diamond():
    g = {"app": ["db", "web"], "db": ["util"], "web": ["util"], "util": []}
    assert has_cycle(g) is False, (
        "The complaint: util is imported by db AND by web, but nothing leads back from util. Meeting a FINISHED "
        "module again is not a cycle; only an edge to a module on the CURRENT path (GREY) is.")


def test_self_import_and_two_cycle():
    assert has_cycle({"x": ["x"]}) is True, "A module that imports itself is a cycle."
    assert has_cycle({"a": ["b"], "b": ["a"]}) is True, "a -> b -> a is a cycle (do not skip the module you came from)."


def test_cycle_not_reachable_from_first_module():
    g = {"main": ["lib"], "lib": [], "x": ["y"], "y": ["z"], "z": ["x"]}
    assert has_cycle(g) is True, "The circle x -> y -> z -> x is not reachable from 'main': start from every unvisited module."


def test_cross_edges_to_finished_modules():
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d", "b"], "d": [], "e": ["a", "d"]}
    assert has_cycle(g) is False, "Many edges lead to finished modules (b, d); none of them is a cycle."


def test_random_against_kahn():
    rng = random.Random(41)
    for _ in range(500):
        n = rng.randint(1, 8)
        names = [f"m{i}" for i in range(n)]
        g = {name: [] for name in names}
        acyclic = rng.random() < 0.6
        for _ in range(rng.randint(0, 12)):
            i, j = rng.randrange(n), rng.randrange(n)
            if acyclic and i >= j:
                continue
            g[names[i]].append(names[j])
        expected = model(g)
        assert has_cycle(g) is expected, f"{g}: expected {expected}."


def test_layered_project_is_fast():
    code = (
        "import sys\n"
        "sys.setrecursionlimit(10000)\n"
        "from solution import has_cycle\n"
        "layers, width = 40, 4\n"
        "g = {}\n"
        "for L in range(layers):\n"
        "    for a in range(width):\n"
        "        g[(L, a)] = [(L + 1, b) for b in range(width)] if L + 1 < layers else []\n"
        "print(has_cycle(g))\n"
        "g[(layers - 1, 0)] = [(0, 3)]\n"
        "print(has_cycle(g))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on a layered project (40 layers of 4 modules, more than 10**23 paths, no cycle). "
        "A finished module must be marked BLACK and never explored again; removing it from the path when you "
        "leave makes it explorable from every path.")
    assert r.returncode == 0, "Your code crashed on the layered project:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["False", "True"], (
        f"Layered project: expected False, then True after adding an edge from the last layer back to the first; "
        f"got {r.stdout.split()}.")
