import pathlib
import random
import subprocess
import sys
from collections import deque

from solution import min_jumps

HERE = pathlib.Path(__file__).parent


def bfs(nums):
    """Fewest jumps by breadth-first search over indices; None if the last index is unreachable."""
    n = len(nums)
    dist = [None] * n
    dist[0] = 0
    queue = deque([0])
    while queue:
        i = queue.popleft()
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            if dist[j] is None:
                dist[j] = dist[i] + 1
                queue.append(j)
    return dist[-1]


def test_chapter_examples():
    assert min_jumps([2, 3, 1, 1, 4]) == 2, (
        "Expected 2 (0 -> 1 -> 4). Jumping as far as possible from index 0 lands on index 2 and needs 3; "
        "jump when the current layer ends, to the layer that reaches farthest.")
    assert min_jumps([2, 3, 0, 1, 4]) == 2, "Expected 2 (0 -> 1 -> 4)."
    assert min_jumps([1, 1, 1, 1]) == 3, "Steps of one: 3 jumps for 4 indices."


def test_single_and_two():
    assert min_jumps([0]) == 0, "One element: you are already on the last index, 0 jumps."
    assert min_jumps([1, 1]) == 1, (
        "Expected 1. If the loop also runs on the last index, it counts a jump from there: loop to len(nums) - 1.")
    assert min_jumps([5, 0]) == 1, "One jump of length 1 (any length up to 5 is allowed)."


def test_one_big_jump():
    assert min_jumps([10, 1, 1, 1, 1, 1]) == 1, "Index 0 reaches the end directly: 1 jump."


def test_random_against_bfs():
    rng = random.Random(23)
    tested = 0
    while tested < 600:
        nums = [rng.randint(0, 4) for _ in range(rng.randint(1, 10))]
        want = bfs(nums)
        if want is None:
            continue                     # the problem promises a reachable last index
        tested += 1
        got = min_jumps(list(nums))
        assert got == want, (
            f"nums={nums}: expected {want} jumps (found by BFS), got {got}. Count a jump only when i reaches the "
            "end of the current layer, and stop the loop before the last index.")


def test_large_input_is_linear():
    code = (
        "from solution import min_jumps\n"
        "n = 10**5\n"
        "print(min_jumps([n] * n), min_jumps([1] * n), min_jumps([2] * n))\n"
    )
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True,
                           timeout=10, encoding="utf-8")
    except subprocess.TimeoutExpired:
        r = None
    assert r is not None, (
        "Time limit (10 s) on 100,000 elements. A BFS that looks at every index each jump covers is "
        "O(n * jump); the layer scan is one pass.")
    assert r.returncode == 0, "Your code crashed on the large input:\n" + r.stderr[-800:]
    assert r.stdout.split() == ["1", "99999", "50000"], (
        f"Large inputs: expected 1, 99999 and 50000 jumps; got {r.stdout.split()}.")
