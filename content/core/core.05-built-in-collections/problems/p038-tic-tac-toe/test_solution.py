import subprocess
import sys
from pathlib import Path

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program did not finish within {timeout} seconds. Look for an infinite loop, "
            "an input() that waits for more lines than the test gives, or a slow step such as "
            "`in` on a long list inside a loop (use a set or dict instead).") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]


def test_example_diagonal():
    assert run("XO.\nOX.\n..X\n") == ["X wins"]


def test_anti_diagonal():
    assert run("X.O\nXO.\nO.X\n") == ["O wins"], "Check the diagonal from top right to bottom left."


def test_column():
    assert run("OX.\nOX.\n.X.\n") == ["X wins"], "Columns count: build them with board[r][c] for r in range(3)."


def test_row():
    assert run("...\nOOO\nXX.\n") == ["O wins"]


def test_draw():
    assert run("XOX\nXOO\nOXX\n") == ["Draw"]


def test_game_on():
    assert run("X..\n...\n...\n") == ["Game on"]


def test_full_board_with_winner():
    assert run("XXX\nOOX\nXOO\n") == ["X wins"], "Check for a winner before deciding it is a draw."
