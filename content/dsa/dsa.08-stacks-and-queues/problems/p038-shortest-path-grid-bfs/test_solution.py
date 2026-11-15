import collections
import random
from collections import deque

import pytest

import solution
from solution import shortest_path

class LimitedDeque(deque):
    """Stops a search that never marks cells as seen before it eats all the memory."""

    def append(self, x):
        if len(self) > 500_000:
            raise AssertionError("Your queue grew past 500,000 entries: cells are enqueued again and again. "
                                 "Keep a `seen` set and add each cell to it when you enqueue it.")
        super().append(x)


@pytest.fixture(autouse=True)
def limited_queue(monkeypatch):
    monkeypatch.setattr(solution, "deque", LimitedDeque, raising=False)


MAZE = ["..#....",
        ".##.##.",
        "....#..",
        ".##...#",
        "...#..."]


def bfs_dist(grid, start):
    """Reference distances from start (Bellman-Ford style relaxation, no queue)."""
    rows, cols = len(grid), len(grid[0])
    inf = float("inf")
    dist = [[inf] * cols for _ in range(rows)]
    if grid[start[0]][start[1]] == "#":
        return dist
    dist[start[0]][start[1]] = 0
    changed = True
    while changed:
        changed = False
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == "#":
                    continue
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] + 1 < dist[r][c]:
                        dist[r][c] = dist[nr][nc] + 1
                        changed = True
    return dist


@pytest.mark.parametrize("grid, start, goal, want, why", [
    (MAZE, (0, 0), (4, 6), 10, "the chapter maze"),
    (MAZE, (0, 0), (0, 3), 7, "the goal is close in a straight line but a wall forces a detour"),
    (["..#.", "..#.", "..#."], (0, 0), (0, 3), -1, "a wall splits the grid: return -1"),
    (["..", ".."], (1, 1), (1, 1), 0, "start == goal: zero steps"),
    ([".#", ".."], (0, 0), (0, 1), -1, "the goal is a wall"),
    (["#.", ".."], (0, 0), (1, 1), -1, "the start is a wall"),
    (["....."], (0, 0), (0, 4), 4, "a single row"),
    ([".", ".", "."], (2, 0), (0, 0), 2, "a single column, moving up"),
    ([".#.", ".#.", "..."], (0, 0), (0, 2), 6, "around the wall"),
])
def test_cases(grid, start, goal, want, why):
    got = shortest_path(list(grid), start, goal)
    assert got == want, f"shortest_path({grid}, {start}, {goal}) should be {want}, got {got}: {why}."


def test_random_mazes():
    rng = random.Random(38)
    for _ in range(150):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        grid = ["".join("#" if rng.random() < 0.3 else "." for _ in range(cols)) for _ in range(rows)]
        start = (rng.randrange(rows), rng.randrange(cols))
        goal = (rng.randrange(rows), rng.randrange(cols))
        d = bfs_dist(grid, start)[goal[0]][goal[1]]
        want = -1 if d == float("inf") or grid[goal[0]][goal[1]] == "#" else d
        got = shortest_path(grid, start, goal)
        assert got == want, f"shortest_path({grid}, {start}, {goal}) should be {want}, got {got}."


class CountingDeque(LimitedDeque):
    appends = 0

    def append(self, x):
        CountingDeque.appends += 1
        super().append(x)


def test_mark_when_enqueued(monkeypatch):
    monkeypatch.setattr(solution, "deque", CountingDeque, raising=False)
    monkeypatch.setattr(collections, "deque", CountingDeque)
    CountingDeque.appends = 0
    grid = ["." * 30] * 30
    got = shortest_path(grid, (0, 0), (29, 29))
    assert got == 58, f"On an open 30 x 30 grid the corner-to-corner distance is 58, got {got}."
    assert CountingDeque.appends > 0, (
        "The test could not see your queue. Use `from collections import deque` and a deque as the BFS queue.")
    assert CountingDeque.appends <= 900, (
        f"Your queue received {CountingDeque.appends} appends on a grid of only 900 cells: some cells were "
        "enqueued more than once (duplicates). Add a cell to `seen` at the moment you ENQUEUE it, not when you dequeue it.")


def test_big_grid():
    grid = ["." * 300 for _ in range(300)]
    grid[150] = "#" * 299 + "."
    assert shortest_path(grid, (0, 0), (299, 0)) == 897, (
        "300 x 300 grid with a wall that has one gap at the far right: go right (299), down through the gap (299) and back left (299): 897 steps.")
