import pytest

from solution import solve_n_queens

KNOWN = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}


def check_board(n, board):
    assert isinstance(board, list) and len(board) == n, f"A board for n = {n} must be a list of {n} strings, got {board!r}."
    queens = []
    for r, row in enumerate(board):
        assert isinstance(row, str), f"Each row must be a string like '.Q..', got {row!r}."
        assert len(row) == n and set(row) <= {".", "Q"}, f"Row {r} of {board} must have {n} characters, only '.' and 'Q'."
        assert row.count("Q") == 1, f"Row {r} of {board} must hold exactly one queen."
        queens.append((r, row.index("Q")))
    for i in range(n):
        for j in range(i + 1, n):
            (r1, c1), (r2, c2) = queens[i], queens[j]
            assert c1 != c2, f"In {board} the queens in rows {r1} and {r2} share column {c1}."
            assert abs(r1 - r2) != abs(c1 - c2), f"In {board} the queens at {queens[i]} and {queens[j]} are on one diagonal."


@pytest.mark.parametrize("n", range(1, 9))
def test_all_boards_valid_and_complete(n):
    boards = solve_n_queens(n)
    assert isinstance(boards, list), "Return a list of boards."
    for b in boards:
        check_board(n, b)
    keys = {tuple(b) for b in boards}
    assert len(keys) == len(boards), f"Some boards for n = {n} appear twice."
    assert len(boards) == KNOWN[n], f"n = {n} has {KNOWN[n]} solutions, you returned {len(boards)}."


def test_example_four():
    got = sorted(solve_n_queens(4))
    want = sorted([[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]])
    assert got == want, f"solve_n_queens(4) should be {want}, got {got}."


def test_one_and_none():
    assert solve_n_queens(1) == [["Q"]], "n = 1: one board with one row 'Q'."
    assert solve_n_queens(3) == [], "n = 3 has no solution: return []."
