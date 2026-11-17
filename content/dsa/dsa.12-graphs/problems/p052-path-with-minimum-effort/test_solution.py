import copy
import random
from collections import deque

from solution import minimum_effort


def reachable(h, limit):
    rows, cols = len(h), len(h[0])
    seen = {(0, 0)}
    q = deque([(0, 0)])
    while q:
        r, c = q.popleft()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and abs(h[r][c] - h[nr][nc]) <= limit:
                seen.add((nr, nc))
                q.append((nr, nc))
    return (rows - 1, cols - 1) in seen


def slow(h):
    """The smallest limit on the step that still connects the corners (BFS for a fixed limit, binary search on it)."""
    diffs = {0}
    rows, cols = len(h), len(h[0])
    for r in range(rows):
        for c in range(cols):
            if r + 1 < rows:
                diffs.add(abs(h[r][c] - h[r + 1][c]))
            if c + 1 < cols:
                diffs.add(abs(h[r][c] - h[r][c + 1]))
    diffs = sorted(diffs)
    lo, hi = 0, len(diffs) - 1          # binary search over the sorted differences (dsa.06)
    while lo < hi:
        mid = (lo + hi) // 2
        if reachable(h, diffs[mid]):
            hi = mid
        else:
            lo = mid + 1
    return diffs[lo]


def test_the_example():
    got = minimum_effort([[1, 2, 2], [3, 8, 2], [5, 3, 5]])
    assert got == 2, f"down the left column and along the bottom every step is 2: effort 2. Got {got}."


def test_effort_is_the_largest_step_not_the_sum():
    got = minimum_effort([[1, 2, 3, 4, 5]])
    assert got == 1, f"one row 1..5: every step is 1, so the effort is 1 (the largest step), not 4 (the sum). Got {got}."


def test_a_long_flat_detour_beats_a_short_steep_route():
    h = [[1, 1, 1],
         [9, 9, 1],
         [1, 1, 1]]
    got = minimum_effort(h)
    assert got == 0, (
        f"the snake 1-1-1 along the top, down the right, back along the bottom never changes height: effort 0. Got {got}. "
        "BFS on the number of steps would go through a 9.")


def test_no_diagonal_moves():
    h = [[1, 100],
         [100, 1]]
    got = minimum_effort(h)
    assert got == 99, f"there is no diagonal move: any route must step onto a 100. Got {got}."


def test_one_cell_and_one_column():
    assert minimum_effort([[7]]) == 0, "a 1x1 grid: the start is the target, effort 0."
    assert minimum_effort([[1], [4], [2]]) == 3, "one column 1, 4, 2: the steps are 3 and 2, effort 3."


def test_the_target_must_be_popped_not_pushed():
    # The target is first reached through a step of 5, later through steps of at most 2.
    h = [[1, 3, 5],
         [10, 10, 5],
         [10, 10, 4],
         [10, 10, 9]]
    got = minimum_effort(h)
    assert got == slow(h), f"expected {slow(h)}, got {got}. Do you stop when the target is pushed? Stop when it is popped."


def test_input_not_changed():
    h = [[1, 2, 2], [3, 8, 2], [5, 3, 5]]
    keep = copy.deepcopy(h)
    minimum_effort(h)
    assert h == keep, "do not change the heights grid."


def test_random_grids():
    rng = random.Random(52)
    for _ in range(250):
        rows, cols = rng.randint(1, 6), rng.randint(1, 6)
        h = [[rng.randint(1, 20) for _ in range(cols)] for _ in range(rows)]
        want = slow(h)
        got = minimum_effort(h)
        assert got == want, f"minimum_effort({h}) should be {want}, got {got}."


def test_100_by_100():
    rng = random.Random(520)
    h = [[rng.randint(1, 10 ** 6) for _ in range(100)] for _ in range(100)]
    got = minimum_effort(h)
    assert got == slow(h), "wrong effort on a random 100x100 grid."
