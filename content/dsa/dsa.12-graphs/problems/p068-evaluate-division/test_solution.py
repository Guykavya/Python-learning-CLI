import math
import random
import subprocess
import sys
from pathlib import Path

from solution import evaluate

HERE = Path(__file__).parent


def close(got, want):
    return len(got) == len(want) and all(
        (w == -1.0 and g == -1.0) or (w != -1.0 and math.isclose(g, w, rel_tol=1e-9)) for g, w in zip(got, want))


def test_the_example():
    got = evaluate([("a", "b"), ("b", "c")], [2.0, 3.0],
                   [("a", "c"), ("c", "a"), ("b", "a"), ("a", "x"), ("x", "x"), ("a", "a")])
    want = [6.0, 1 / 6, 0.5, -1.0, -1.0, 1.0]
    assert close(got, want), f"expected {want}, got {got}. a / c = (a / b) * (b / c) = 2 * 3."


def test_backwards_needs_the_reverse_edge():
    got = evaluate([("a", "b")], [4.0], [("b", "a")])
    assert close(got, [0.25]), f"a / b = 4 means b / a = 1 / 4 = 0.25; got {got}. Add the edge b -> a with weight 1 / k."


def test_multiply_not_add():
    got = evaluate([("a", "b"), ("b", "c")], [2.0, 5.0], [("a", "c")])
    assert close(got, [10.0]), f"a / c = (a / b) * (b / c) = 2 * 5 = 10; got {got}. Multiply along the path."


def test_unknown_variables():
    got = evaluate([("a", "b")], [2.0], [("x", "x"), ("a", "x"), ("x", "a"), ("b", "b")])
    assert close(got, [-1.0, -1.0, -1.0, 1.0]), (
        f"x appears in no equation: every query with x is -1.0, even x / x; but b is known, so b / b = 1.0. Got {got}.")


def test_unknown_stays_unknown_after_another_query():
    got = evaluate([("a", "b")], [2.0], [("a", "q"), ("q", "q")])
    assert close(got, [-1.0, -1.0]), (
        f"q is unknown in both queries; got {got}. If the second answer was 1.0, the first query added q to your "
        "graph (reading adj[q] on a defaultdict creates it). Check `q in adj` before looking it up.")


def test_different_groups():
    got = evaluate([("a", "b"), ("c", "d")], [2.0, 3.0], [("a", "d"), ("c", "d")])
    assert close(got, [-1.0, 3.0]), f"a and d are in different groups: -1.0; c / d = 3. Got {got}."


def test_a_cycle_of_equations_finishes():
    eqs = [("a", "b"), ("b", "c"), ("c", "a")]
    vals = [2.0, 3.0, 1 / 6]
    code = (
        "from solution import evaluate\n"
        f"print(evaluate({eqs!r}, {vals!r}, [('a', 'z'), ('a', 'c'), ('c', 'b')]))\n")
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "the equations a / b, b / c, c / a form a cycle and your search never stopped: remember the variables "
            "you have reached (the product dictionary can be the seen set).") from None
    assert r.returncode == 0, "your code crashed on a cycle of equations:\n" + r.stderr[-600:]
    got = eval(r.stdout.strip())
    assert close(got, [-1.0, 6.0, 1 / 3]), f"with a cycle of equations: expected [-1.0, 6.0, 0.333...], got {got}."


def test_random_hidden_values():
    rng = random.Random(68)
    for _ in range(150):
        names = [f"v{i}" for i in range(rng.randint(2, 15))]
        hidden = {x: rng.uniform(0.5, 20) for x in names}
        groups = {x: i % rng.randint(1, 3) for i, x in enumerate(names)}
        eqs, vals = [], []
        for _ in range(rng.randint(1, 25)):
            a, b = rng.choice(names), rng.choice(names)
            if groups[a] == groups[b]:
                eqs.append((a, b))
                vals.append(hidden[a] / hidden[b])
        known = {x for e in eqs for x in e}
        queries = [(rng.choice(names + ["zz"]), rng.choice(names + ["zz"])) for _ in range(20)]
        adj = {x: set() for x in known}
        for a, b in eqs:
            adj[a].add(b)
            adj[b].add(a)

        def linked(x, y):
            if x not in known or y not in known:
                return False
            seen, stack = {x}, [x]
            while stack:
                u = stack.pop()
                for v in adj[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            return y in seen

        want = [hidden[x] / hidden[y] if linked(x, y) else -1.0 for x, y in queries]
        got = evaluate(eqs, vals, queries)
        assert close(got, want), f"evaluate({eqs}, {vals}, {queries}):\nexpected {want}\ngot      {got}"


def test_many_equations_and_queries():
    rng = random.Random(680)
    names = [f"x{i}" for i in range(1500)]
    hidden = {x: rng.uniform(0.5, 2.0) for x in names}
    eqs = [(names[i], names[i + 1]) for i in range(len(names) - 1)]
    vals = [hidden[a] / hidden[b] for a, b in eqs]
    queries = [(rng.choice(names), rng.choice(names)) for _ in range(300)]
    got = evaluate(eqs, vals, queries)
    want = [hidden[x] / hidden[y] for x, y in queries]
    assert all(math.isclose(g, w, rel_tol=1e-6) for g, w in zip(got, want)), "wrong answers on a chain of 1,500 variables."
