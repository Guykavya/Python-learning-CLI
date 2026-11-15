import copy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

def run_code(code, timeout, what):
    try:
        r = subprocess.run([sys.executable, "-c", code], cwd=HERE, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{what} took more than {timeout} seconds.") from None
    assert r.returncode == 0, f"Your code crashed:\n{r.stderr[-800:]}"
    return r.stdout.strip()


def units_ok(board):
    """Return None if no row/column/box repeats a digit, else a message naming the unit."""
    for r in range(9):
        ds = [d for d in board[r] if d]
        if len(ds) != len(set(ds)):
            return f"row {r} repeats a digit"
    for c in range(9):
        ds = [board[r][c] for r in range(9) if board[r][c]]
        if len(ds) != len(set(ds)):
            return f"column {c} repeats a digit"
    for b in range(9):
        ds = [board[r][c] for r in range(b // 3 * 3, b // 3 * 3 + 3) for c in range(b % 3 * 3, b % 3 * 3 + 3) if board[r][c]]
        if len(ds) != len(set(ds)):
            return f"box {b} repeats a digit"
    return None


EASY = "530070000600195000098000060800060003400803001700020006060000280000419005000080079"
EASY_SOLVED = "534678912672195348198342567859761423426853791713924856961537284287419635345286179"
MEDIUM = "000000907000420180000705026100904000050000040000507009920108000034059000507000000"


def parse(text):
    return [[int(ch) for ch in text[r * 9:(r + 1) * 9]] for r in range(9)]


def check_solution(puzzle_text, solved):
    puzzle = parse(puzzle_text)
    assert solved is not None, "This puzzle has a solution, but you returned None."
    assert isinstance(solved, list) and len(solved) == 9 and all(len(row) == 9 for row in solved), \
        "Return the solved board as 9 lists of 9 ints."
    assert all(1 <= d <= 9 for row in solved for d in row), \
        "The solved board still has empty cells (0). Did you undo the digits after the search succeeded?"
    problem = units_ok(solved)
    assert problem is None, f"Your solved board is not valid: {problem}."
    for r in range(9):
        for c in range(9):
            if puzzle[r][c]:
                assert solved[r][c] == puzzle[r][c], f"You changed the given digit at ({r}, {c})."


def solve_in_subprocess(text, timeout=20):
    code = ("from solution import solve_sudoku\n"
            f"t = {text!r}\n"
            "b = [[int(ch) for ch in t[r * 9:(r + 1) * 9]] for r in range(9)]\n"
            "s = solve_sudoku(b)\n"
            "print('None' if s is None else ''.join(str(d) for row in s for d in row))\n")
    out = run_code(code, timeout, "Solving the puzzle (use the row/column/box sets and stop at the first solution)")
    return None if out == "None" else parse(out)


def test_easy_exact():
    from solution import solve_sudoku
    solved = solve_sudoku(parse(EASY))
    check_solution(EASY, solved)
    assert solved == parse(EASY_SOLVED), "The easy puzzle has exactly one solution (shown in chapter section 12)."


def test_medium():
    solved = solve_in_subprocess(MEDIUM)
    check_solution(MEDIUM, solved)


def test_cell_without_options():
    # Only 10 empty cells, so any cell order finishes quickly. The givens do not clash.
    text = "123456780459871230876239140617548300394612570582703619748125960965387420231964850"
    assert solve_in_subprocess(text) is None, (
        "Cell (0, 8) can hold no digit: row 0 has 1..8 and column 8 already has a 9 (row 5). "
        "Return None when the search fails.")


def test_clashing_givens():
    from solution import solve_sudoku
    board = parse(EASY)
    board[0][2] = 5                     # a second 5 in row 0
    assert solve_sudoku(copy.deepcopy(board)) is None, (
        "The givens already have two 5s in row 0, so there is no solution. Check the givens while building the sets.")


def test_already_solved():
    from solution import solve_sudoku
    solved = solve_sudoku(parse(EASY_SOLVED))
    assert solved == parse(EASY_SOLVED), "A full, valid board is its own solution."
