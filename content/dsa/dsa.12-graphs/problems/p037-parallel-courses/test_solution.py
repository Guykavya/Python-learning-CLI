import pathlib
import random
import subprocess
import sys

from solution import min_semesters

HERE = pathlib.Path(__file__).parent


def brute(n, relations):
    """Longest chain by relaxing n + 1 times; still changing after n rounds means a cycle."""
    level = [1] * n
    for _ in range(n + 1):
        changed = False
        for u, v in relations:
            if level[u] + 1 > level[v]:
                level[v] = level[u] + 1
                changed = True
        if not changed:
            return max(level)
    return -1


def test_examples():
    assert min_semesters(3, [(0, 2), (1, 2)]) == 2, "0 and 1 together in semester 1, then 2: 2 semesters."
    assert min_semesters(3, [(0, 1), (1, 2), (0, 2)]) == 3, (
        "0 -> 1 -> 2 is a chain of 3 courses: 3 semesters. If you got 2, you used the SHORTEST way to course 2 "
        "(BFS distance); a course waits for its LONGEST chain of prerequisites.")
    assert min_semesters(3, [(0, 1), (1, 2), (2, 0)]) == -1, "A cycle: impossible, -1."
    assert min_semesters(4, []) == 1, "No relations: all 4 courses in one semester. If you got 4, you counted courses, not rounds."


def test_rounds_not_courses():
    assert min_semesters(6, [(0, 3), (1, 3), (2, 4), (3, 5), (4, 5)]) == 3, (
        "Semester 1: 0, 1, 2; semester 2: 3, 4; semester 3: 5. Count rounds, not courses.")
    assert min_semesters(5, [(0, 1), (0, 1), (1, 2)]) == 3, "A relation listed twice still means the same thing: 3 semesters."


def test_cycle_after_free_courses():
    assert min_semesters(5, [(0, 1), (1, 2), (2, 3), (3, 2), (3, 4)]) == -1, (
        "Courses 2 and 3 wait for each other: -1, even though 0 and 1 can be taken.")
    assert min_semesters(2, [(1, 1)]) == -1, "A course that needs itself: -1."


def test_random_against_brute_force():
    rng = random.Random(37)
    for _ in range(500):
        n = rng.randint(1, 8)
        rel = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 10))]
        if rng.random() < 0.7:
            perm = list(range(n))
            rng.shuffle(perm)
            rel = [(perm[min(u, v)], perm[max(u, v)]) for u, v in rel if u != v]
        expected = brute(n, rel)
        assert min_semesters(n, rel) == expected, (
            f"n={n}, relations={rel}: expected {expected}. Count Kahn ROUNDS (the longest chain), and -1 for a cycle.")


def test_long_chain():
    code = (
        "from solution import min_semesters\n"
        "n = 100000\n"
        "rel = [(i, i + 1) for i in range(n - 1)] + [(0, n - 1), (5, 70000)]\n"
        "print(min_semesters(n, rel), min_semesters(n, rel + [(n - 1, 3)]))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (10 s) on 100,000 courses: O(n + E)."
    assert "RecursionError" not in r.stderr, "RecursionError on a chain of 100,000 courses: no recursion."
    assert r.returncode == 0, "Your code crashed on the long chain:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["100000", "-1"], (
        f"A chain of 100,000 courses (plus shortcuts) needs 100000 semesters; with a cycle -1. Got {r.stdout.split()}.")
