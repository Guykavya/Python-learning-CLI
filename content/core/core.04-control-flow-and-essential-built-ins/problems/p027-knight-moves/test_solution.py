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

FILES = "abcdefgh"


def moves(sq):
    f0, r0 = FILES.index(sq[0]), int(sq[1])
    out = [f"{FILES[f]}{r}" for f in range(8) for r in range(1, 9)
           if (abs(f - f0), abs(r - r0)) in ((1, 2), (2, 1))]
    return [" ".join(out), f"Moves: {len(out)}"]


def test_centre():
    assert run("d4\n") == ["b3 b5 c2 c6 e2 e6 f3 f5", "Moves: 8"], (
        "From d4 there are 8 moves, listed by file a..h and then rank 1..8.")


def test_corner_and_capitals():
    assert run("A1\n") == ["b3 c2", "Moves: 2"], "A corner square has 2 moves. Accept capital letters."


@pytest.mark.parametrize("sq", ["h8", "a8", "h1", "b1", "g7", "e5", "a4", "h5"])
def test_squares(sq):
    got = run(f"  {sq}  \n")
    assert got == moves(sq), (
        f"From {sq} expected {moves(sq)}, got {got}. Check the board edges and the output order.")


@pytest.mark.parametrize("bad", ["i1", "a0", "a9", "a", "", "a10", "11", "dd"])
def test_invalid(bad):
    got = run(f"{bad}\n")
    assert got == ["invalid square"], (
        f"{bad!r} is not a square on the board; expected ['invalid square'], got {got}. "
        "Check the length before indexing.")
