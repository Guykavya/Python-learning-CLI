import pathlib
import random
import subprocess
import sys
from itertools import permutations

from solution import find_order

HERE = pathlib.Path(__file__).parent


def possible(n, prereqs):
    return any(all(p.index(b) < p.index(a) for a, b in prereqs) for p in permutations(range(n)))


def check(n, prereqs, got, label):
    assert isinstance(got, list), f"{label}: return a list, got {type(got).__name__}."
    assert got != [] or n == 0, f"{label}: you returned [] but a plan exists."
    assert sorted(got) == list(range(n)), f"{label}: the plan must list every course exactly once, got {got}."
    pos = {c: i for i, c in enumerate(got)}
    for a, b in prereqs:
        assert pos[b] < pos[a], (
            f"{label}: [{a}, {b}] means take {b} BEFORE {a}, but your plan {got} has {a} first. "
            f"The edge goes {b} -> {a}; check its direction.")


def test_examples():
    check(2, [[1, 0]], find_order(2, [[1, 0]]), "[[1, 0]]")
    check(4, [[1, 0], [2, 0], [3, 1], [3, 2]], find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]]), "diamond")
    assert find_order(2, [[1, 0], [0, 1]]) == [], "A cycle: return [] (not None, not a partial plan)."
    check(3, [], find_order(3, []), "no prerequisites")


def test_direction_matters():
    pre = [[2, 0], [1, 2]]
    got = find_order(3, pre)
    check(3, pre, got, "[[2, 0], [1, 2]]: 0 before 2, 2 before 1")
    assert got == [0, 2, 1], "Only one plan exists here: [0, 2, 1]."


def test_cycle_behind_free_courses():
    assert find_order(5, [[1, 0], [2, 1], [3, 2], [2, 3], [4, 3]]) == [], (
        "Courses 2 and 3 need each other (and 4 needs 3): no plan, return [] even though 0 and 1 can be taken.")


def test_random_against_brute_force():
    rng = random.Random(34)
    for _ in range(400):
        n = rng.randint(1, 6)
        pre = [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(0, 7))]
        if rng.random() < 0.6:
            perm = list(range(n))
            rng.shuffle(perm)
            pre = [[perm[max(a, b)], perm[min(a, b)]] for a, b in pre if a != b]
        got = find_order(n, pre)
        if possible(n, pre):
            check(n, pre, got, f"n={n}, prerequisites={pre}")
        else:
            assert got == [], f"n={n}, prerequisites={pre}: impossible, expected [], got {got}."


def test_long_chain():
    code = (
        "from solution import find_order\n"
        "n = 100000\n"
        "pre = [[i + 1, i] for i in range(n - 1)]\n"
        "print(find_order(n, pre) == list(range(n)), find_order(n, pre + [[0, n - 1]]) == [])\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (10 s) on a chain of 100,000 courses."
    assert "RecursionError" not in r.stderr, "RecursionError on a chain of 100,000 courses: use Kahn or an explicit stack."
    assert r.returncode == 0, "Your code crashed on the long chain:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "True"], (
        f"Chain of 100,000 courses: expected the plan 0, 1, 2, ... and then [] after adding a cycle; got {r.stdout.split()}.")
