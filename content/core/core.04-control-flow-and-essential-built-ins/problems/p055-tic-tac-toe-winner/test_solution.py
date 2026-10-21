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
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import pytest


def judge(*rows):
    out = run("".join(r + "\n" for r in rows))
    assert len(out) == 1, f"Print exactly one verdict line, got {out}"
    return out[0]


@pytest.mark.parametrize("rows, want", [
    (("XO.", "XO.", "X.."), "X wins"),
    (("XXX", "OO.", "..."), "X wins"),
    (("X.O", ".XO", "..X"), "X wins"),
    (("..X", ".XO", "XO."), "X wins"),
    (("OX.", "OX.", "O.X"), "O wins"),
    (("XXO", ".O.", "OX."), "O wins"),
])
def test_winners(rows, want):
    assert judge(*rows) == want, f"{rows}: expected {want}. Check rows, columns and both diagonals."


@pytest.mark.parametrize("rows, want", [
    (("XOX", "XOO", "OXX"), "Draw"),
    (("...", "...", "..."), "In progress"),
    (("X..", "...", "..."), "In progress"),
    (("XO.", "...", "..."), "In progress"),
])
def test_draw_and_progress(rows, want):
    assert judge(*rows) == want, f"{rows}: expected {want}. A full board with no winner is a Draw."


@pytest.mark.parametrize("rows, why", [
    (("XXX", "...", "..."), "X has 3 moves and O none: counts are impossible"),
    (("O..", "...", "..."), "O cannot move first"),
    (("XXX", "OOO", "..."), "both players cannot win"),
    (("XXX", "OO.", "O.."), "X won but O has as many moves, so X did not make the last move"),
    (("OOO", "XX.", "X.X"), "O won but X has more moves"),
    (("XO", "...", "..."), "a line with 2 characters"),
    (("XO..", "...", "..."), "a line with 4 characters"),
    (("XOA", "...", "..."), "A is not a valid character"),
    (("xo.", "...", "..."), "small x and o are not valid"),
])
def test_invalid(rows, why):
    assert judge(*rows) == "Invalid board", f"{rows} is invalid: {why}."
