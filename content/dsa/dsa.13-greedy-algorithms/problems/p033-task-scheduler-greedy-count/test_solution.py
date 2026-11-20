import random
from collections import Counter, deque

from solution import least_interval


def bfs_optimum(tasks, n):
    """Shortest schedule by BFS over states: for each letter (copies left, units until allowed)."""
    start = tuple(sorted((c, 0) for c in Counter(tasks).values()))
    if not start:
        return 0
    dist = {start: 0}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        if not state:
            return dist[state]
        choices = [None] + [i for i, (c, wait) in enumerate(state) if wait == 0]
        for pick in choices:                         # None = stay idle
            nxt = []
            for i, (c, wait) in enumerate(state):
                if i == pick:
                    if c - 1 > 0:
                        nxt.append((c - 1, n))
                else:
                    nxt.append((c, max(0, wait - 1)))
            key = tuple(sorted(nxt))
            if key not in dist:
                dist[key] = dist[state] + 1
                queue.append(key)
    return None


def test_examples():
    assert least_interval(["A", "A", "A", "B", "B", "B"], 2) == 8, (
        "Expected 8 (A B idle A B idle A B). Two letters share the top count 3, so the last row holds both: "
        "(3 - 1) * (2 + 1) + 2.")
    assert least_interval(["A", "A", "A", "B", "B", "B"], 0) == 6, "No cooldown: one task per unit, 6. The formula alone gives 4 here; the answer is never below len(tasks)."
    assert least_interval(["A"] * 6 + list("BCDEFG"), 2) == 16, (
        "Expected 16: six A's need (6 - 1) * 3 + 1 units; the other letters fit into the gaps.")


def test_no_idle_needed():
    assert least_interval(list("ABCDABCD"), 1) == 8, (
        "Expected 8: there are enough different letters to fill every gap, so the answer is len(tasks). "
        "Take the max of len(tasks) and the formula.")


def test_single_letter():
    assert least_interval(["A", "A", "A"], 3) == 9, "Three A's with cooldown 3: A . . . A . . . A = 9 units."
    assert least_interval(["A"], 5) == 1, "One task: 1 unit (no cooldown after the last task)."


def test_empty():
    assert least_interval([], 4) == 0, "No tasks: 0 units."


def test_most_copies_first():
    assert least_interval(["A", "B", "B", "B"], 1) == 5, (
        "Expected 5 (B A B idle B). Starting with A (alphabetical) wastes a unit: run the letter with the most "
        "copies left.")


def test_random_against_bfs():
    rng = random.Random(33)
    for _ in range(250):
        kinds = rng.randint(1, 4)
        tasks = []
        for letter in "ABCD"[:kinds]:
            tasks += [letter] * rng.randint(1, 4)
        rng.shuffle(tasks)
        n = rng.randint(0, 3)
        want = bfs_optimum(tasks, n)
        got = least_interval(list(tasks), n)
        assert got == want, (
            f"tasks={tasks}, n={n}: expected {want} (shortest schedule found by BFS), got {got}. "
            "Use max(len(tasks), (f - 1) * (n + 1) + m), where f is the top count and m how many letters reach it.")


def test_large_input():
    tasks = ["A"] * 50000 + ["B"] * 50000
    assert least_interval(tasks, 100) == 49999 * 101 + 2, "100,000 tasks: (f - 1) * (n + 1) + m."
    tasks = [chr(ord("A") + i % 26) for i in range(10**5)]
    assert least_interval(tasks, 25) == 10**5, "26 letters in rotation with cooldown 25: no idle, 100,000 units."
