import random

from solution import capture


def model(board):
    rows = len(board)
    cols = len(board[0]) if rows else 0
    out = [list(row) for row in board]
    seen = set()
    for r in range(rows):
        for c in range(cols):
            if board[r][c] != "O" or (r, c) in seen:
                continue
            region, todo, touches = [], [(r, c)], False
            seen.add((r, c))
            while todo:
                a, b = todo.pop()
                region.append((a, b))
                if a in (0, rows - 1) or b in (0, cols - 1):
                    touches = True
                for x, y in ((a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)):
                    if 0 <= x < rows and 0 <= y < cols and board[x][y] == "O" and (x, y) not in seen:
                        seen.add((x, y))
                        todo.append((x, y))
            if not touches:
                for a, b in region:
                    out[a][b] = "X"
    return ["".join(row) for row in out]


def test_the_example():
    board = ["XXXX", "XOOX", "XXOX", "XOXX"]
    got = capture(board)
    assert list(got) == ["XXXX", "XXXX", "XXXX", "XOXX"], (
        f"Expected ['XXXX', 'XXXX', 'XXXX', 'XOXX'], got {got}. The inner region is captured; the O on the bottom border survives.")


def test_inner_cell_joined_to_the_border_survives():
    board = ["XXXXX", "XOOOO", "XOXXX", "XXXXX"]
    got = list(capture(board))
    assert got == board, (
        f"Every O here is joined to the O at (1, 4) on the right border, so nothing is captured. Got {got}. "
        "An O that is not on the border can still be safe through its neighbours.")


def test_columns_count_as_border():
    board = ["XXX", "OOX", "XXX"]
    assert list(capture(board)) == board, "(1, 0) is on the LEFT border: the region survives. Check the first and last column too."
    board = ["XXX", "XOO", "XXX"]
    assert list(capture(board)) == board, "(1, 2) is on the RIGHT border: the region survives."


def test_diagonal_does_not_save():
    board = ["XXXX", "XOXX", "XXOX", "XXXO"]
    want = ["XXXX", "XXXX", "XXXX", "XXXO"]
    got = list(capture(board))
    assert got == want, f"O cells joined only diagonally are separate regions: expected {want}, got {got}."


def test_caller_board_is_not_changed_and_small_cases():
    board = ["XXX", "XOX", "XXX"]
    before = list(board)
    got = list(capture(board))
    assert got == ["XXX", "XXX", "XXX"], "A single O in the middle is captured."
    assert board == before, "capture changed the caller's list: return a new list."
    assert list(capture([])) == [], "An empty board gives []."
    assert list(capture(["O"])) == ["O"], "A 1x1 board: the cell is on the border."


def test_random_boards():
    rng = random.Random(1221)
    for _ in range(400):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        board = ["".join(rng.choice("XXO") for _ in range(cols)) for _ in range(rows)]
        want = model(board)
        got = list(capture(board))
        assert got == want, f"capture({board}) should be {want}, got {got}."


def test_large_open_board():
    board = ["O" * 300] * 300
    try:
        got = list(capture(board))
    except RecursionError:
        raise AssertionError("RecursionError on a 300 x 300 board of O: use an explicit stack or a queue.") from None
    assert got == board, "A board full of O touches the border everywhere: nothing is captured."
