import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import min_steps

HERE = pathlib.Path(__file__).parent


def bfs(n):
    """Breadth-first search over the numbers: an independent way to find the fewest moves."""
    dist = {n: 0}
    queue = deque([n])
    while queue:
        x = queue.popleft()
        if x == 1:
            return dist[x]
        nexts = [x - 1]
        if x % 2 == 0:
            nexts.append(x // 2)
        if x % 3 == 0:
            nexts.append(x // 3)
        for y in nexts:
            if y >= 1 and y not in dist:
                dist[y] = dist[x] + 1
                queue.append(y)


def run_big(code, limit):
    try:
        return subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                              timeout=limit, encoding="utf-8")
    except subprocess.TimeoutExpired:
        return None


def test_small():
    assert min_steps(1) == 0, "Already at 1: 0 moves. Base case f(1) = 0."
    assert min_steps(2) == 1, "2 -> 1: one move."
    assert min_steps(3) == 1, "3 -> 1 (divide by 3): one move."
    assert min_steps(10) == 3, (
        "10 -> 9 -> 3 -> 1 is 3 moves. Greedy (always divide when possible) does 10 -> 5 -> 4 -> 2 -> 1 = 4: "
        "try all three moves and take the best.")


def test_against_bfs():
    rng = random.Random(909)
    for n in list(range(1, 200)) + [rng.randint(200, 600) for _ in range(40)]:
        want = bfs(n)
        got = min_steps(n)
        assert got == want, (
            f"min_steps({n}) = {got}, but a search over all move sequences finds {want}. "
            "f(i) = 1 + min(f(i - 1), f(i // 2) if even, f(i // 3) if divisible by 3).")


def test_large_n_with_normal_recursion_limit():
    code = (
        "import sys\n"
        "limit = sys.getrecursionlimit()\n"
        "from solution import min_steps\n"
        "print(min_steps(10**4), min_steps(123456), min_steps(2 * 10**5))\n"
        "print(sys.getrecursionlimit() == limit)\n"
    )
    r = run_big(code, 15)
    assert r is not None, (
        "Time limit (15 s) for n = 2 * 10**5: exponential: add a memo. With a table each number is done once.")
    if "RecursionError" in r.stderr:
        assert False, (
            "RecursionError for large n: the recursion is about n frames deep, because f(n) asks f(n - 1) "
            "first. Fill a table from 2 up to n instead (or warm the cache from the bottom).")
    assert r.returncode == 0, (
        "Python crashed or failed on large n (a very deep recursion can crash the interpreter):\n"
        + r.stderr[-800:])
    lines = r.stdout.split("\n")
    assert lines[0].split() == ["14", "15", "18"], (
        f"Expected 14, 15, 18 for n = 10**4, 123456, 2 * 10**5; got {lines[0]}.")
    assert lines[1] == "True", (
        "Your solution changed the recursion limit. Solve it without recursion instead: a table cannot "
        "crash the interpreter.")
