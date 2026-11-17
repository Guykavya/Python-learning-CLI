import random
from collections import deque

from solution import knight_moves

MOVES = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))


def all_distances(n, start):
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                queue.append((nr, nc))
    return dist


def test_examples():
    assert knight_moves(8, (0, 0), (1, 2)) == 1, "(0,0) -> (1,2) is one L-shaped move."
    assert knight_moves(8, (0, 0), (7, 7)) == 6, "Corner to corner on a chess board takes 6 moves (BFS gives the minimum)."
    assert knight_moves(8, (0, 0), (1, 1)) == 4, (
        "(0,0) -> (1,1) takes 4 moves on a real board. If you got 2, your knight left the board "
        "(check 0 <= row < n and 0 <= col < n before using a square).")
    assert knight_moves(3, (0, 0), (1, 1)) == -1, "The centre of a 3x3 board cannot be reached: return -1."
    assert knight_moves(5, (2, 2), (2, 2)) == 0, "start == target needs 0 moves."


def test_tiny_boards():
    assert knight_moves(1, (0, 0), (0, 0)) == 0, "1x1 board, same square: 0."
    assert knight_moves(2, (0, 0), (1, 1)) == -1, "On a 2x2 board the knight cannot move at all: -1."
    assert knight_moves(3, (0, 0), (2, 1)) == 1, "(0,0) -> (2,1) on 3x3 is one move."
    assert knight_moves(3, (0, 0), (0, 1)) == 3, "On 3x3, (0,0) -> (0,1) needs 3 moves: (0,0) -> (1,2) -> (2,0) -> (0,1)."


def test_all_targets_on_small_boards():
    for n in (4, 5, 6, 8):
        rng = random.Random(28 + n)
        for _ in range(4):
            start = (rng.randrange(n), rng.randrange(n))
            dist = all_distances(n, start)
            for r in range(n):
                for c in range(n):
                    expected = dist.get((r, c), -1)
                    got = knight_moves(n, start, (r, c))
                    assert got == expected, (
                        f"n={n}, {start} -> {(r, c)}: expected {expected}, got {got}. Use BFS (not DFS), all 8 moves, "
                        "and stay on the board.")


def test_big_board():
    assert knight_moves(300, (0, 0), (299, 299)) == all_distances(300, (0, 0))[(299, 299)], (
        "Corner to corner on a 300x300 board: BFS distance.")
