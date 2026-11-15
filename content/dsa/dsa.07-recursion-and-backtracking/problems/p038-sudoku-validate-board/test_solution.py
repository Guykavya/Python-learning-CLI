import copy

from solution import is_valid_sudoku

SOLVED = ("534678912672195348198342567859761423426853791713924856961537284287419635345286179")
PUZZLE = ("530070000600195000098000060800060003400803001700020006060000280000419005000080079")


def parse(text):
    return [[int(ch) for ch in text[r * 9:(r + 1) * 9]] for r in range(9)]


def empty():
    return [[0] * 9 for _ in range(9)]


def test_empty_board():
    assert is_valid_sudoku(empty()) is True, "An empty board (all zeros) is valid: zeros are ignored, not repeated digits."


def test_solved_board():
    assert is_valid_sudoku(parse(SOLVED)) is True, "A correctly solved board is valid."


def test_partial_board():
    assert is_valid_sudoku(parse(PUZZLE)) is True, "The puzzle from chapter section 12 (partly filled) is valid."


def test_row_repeat():
    b = empty()
    b[4][0] = b[4][8] = 7
    assert is_valid_sudoku(b) is False, "Row 4 has two 7s (columns 0 and 8, different boxes): your row check missed it."


def test_column_repeat():
    b = empty()
    b[0][6] = b[8][6] = 2
    assert is_valid_sudoku(b) is False, "Column 6 has two 2s (rows 0 and 8, different boxes): your column check missed it."


def test_box_repeat_only():
    b = empty()
    b[3][3] = b[5][5] = 9
    assert is_valid_sudoku(b) is False, (
        "Box 4 (the centre) has two 9s at (3, 3) and (5, 5), in different rows and columns: your box check missed it. "
        "box = (r // 3) * 3 + c // 3.")


def test_box_index_not_mixed_up():
    b = empty()
    b[0][3] = 1
    b[3][0] = 1
    b[1][7] = 4
    b[7][1] = 4
    assert is_valid_sudoku(b) is True, (
        "(0, 3) and (3, 0) are in boxes 1 and 3, which are different boxes; (1, 7) and (7, 1) are in boxes 2 and 6. "
        "If you said False, your box index mixes rows and columns (e.g. r // 3 + c // 3).")


def test_change_in_solved_board():
    b = parse(SOLVED)
    b[0][0], b[0][1] = b[0][1], b[0][0]
    assert is_valid_sudoku(b) is False, "Swapping two cells of row 0 in a solved board breaks two columns: the result is invalid."


def test_board_not_changed():
    b = parse(PUZZLE)
    before = copy.deepcopy(b)
    is_valid_sudoku(b)
    assert b == before, "is_valid_sudoku must not change the board."
