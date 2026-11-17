import pathlib
import random
import subprocess
import sys
from itertools import permutations

from solution import can_finish

HERE = pathlib.Path(__file__).parent


def brute(n, prereqs):
    return any(all(p.index(b) < p.index(a) for a, b in prereqs) for p in permutations(range(n)))


def test_examples():
    assert can_finish(2, [[1, 0]]) is True, "[[1, 0]]: take 0, then 1."
    assert can_finish(2, [[1, 0], [0, 1]]) is False, "1 needs 0 and 0 needs 1: impossible."
    assert can_finish(4, [[1, 0], [2, 0], [3, 1], [3, 2]]) is True, (
        "Course 3 needs 1 and 2, which both need 0: a diamond, not a cycle. A single 'visited' set in a DFS "
        "wrongly calls this a cycle.")
    assert can_finish(1, [[0, 0]]) is False, "A course that is its own prerequisite can never be taken."


def test_no_prerequisites_and_repeats():
    assert can_finish(5, []) is True, "No prerequisites: every order works."
    assert can_finish(3, [[1, 0], [1, 0], [2, 1]]) is True, (
        "The pair [1, 0] is listed twice; that is still possible. Count each listed pair in the in-degree.")


def test_random_against_brute_force():
    rng = random.Random(33)
    for _ in range(400):
        n = rng.randint(1, 6)
        prereqs = [[rng.randrange(n), rng.randrange(n)] for _ in range(rng.randint(0, 7))]
        if rng.random() < 0.6:
            prereqs = [[max(a, b), min(a, b)] for a, b in prereqs if a != b]
        expected = brute(n, prereqs)
        assert can_finish(n, prereqs) is expected, f"n={n}, prerequisites={prereqs}: expected {expected}."


def test_long_chain():
    code = (
        "from solution import can_finish\n"
        "n = 100000\n"
        "pre = [[i + 1, i] for i in range(n - 1)]\n"
        "print(can_finish(n, pre), can_finish(n, pre + [[0, n - 1]]))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, "Time limit (10 s) on a chain of 100,000 courses: O(V + E), no repeated scans."
    assert "RecursionError" not in r.stderr, "RecursionError on a chain of 100,000 courses: use Kahn or an explicit stack."
    assert r.returncode == 0, "Your code crashed on the long chain:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["True", "False"], (
        f"Chain of 100,000 courses: expected True, then False after adding [0, n-1]; got {r.stdout.split()}.")
