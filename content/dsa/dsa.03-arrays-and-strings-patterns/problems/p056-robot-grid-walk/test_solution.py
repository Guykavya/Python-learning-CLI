import subprocess
import sys
from pathlib import Path

import pytest

SOLUTION = Path(__file__).with_name("solution.py")


def run(stdin: str, timeout: float = 10) -> list[str]:
    """Run your program with the given keyboard input and return its printed lines."""
    try:
        r = subprocess.run([sys.executable, str(SOLUTION)], input=stdin,
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or a loop that does far more work than needed.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

import random


def ask(rows, start, commands, timeout=10):
    text = f"{len(rows)} {len(rows[0])}\n" + "\n".join(rows) + f"\n{start[0]} {start[1]}\n{commands}\n"
    return run(text, timeout=timeout)


def simulate(rows, start, commands):
    """Independent check: positions as complex numbers (real = row, imag = column); turning = multiplying by 1j."""
    r, c = len(rows), len(rows[0])
    pos = complex(start[0] - 1, start[1] - 1)
    step = complex(-1, 0)                  # North
    seen = {pos}
    for ch in commands:
        if ch == "R":
            step *= -1j                    # N(-1,0) -> E(0,1) -> S(1,0) -> W(0,-1)
        elif ch == "L":
            step *= 1j
        else:
            nxt = pos + step
            i, j = int(nxt.real), int(nxt.imag)
            if 0 <= i < r and 0 <= j < c and rows[i][j] == ".":
                pos = nxt
                seen.add(pos)
    name = {complex(-1, 0): "N", complex(0, 1): "E", complex(1, 0): "S", complex(0, -1): "W"}[step]
    return [f"{int(pos.real) + 1} {int(pos.imag) + 1} {name}", str(len(seen))]


EXAMPLE = ["..#..", ".....", ".##..", ".....", "#...."]


def test_example():
    got = ask(EXAMPLE, (5, 2), "FFLFRFFRFFFFRFFFF")
    assert got == ["5 5 S", "12"], (
        f"Expected ['5 5 S', '12'], got {got}. Follow the step-by-step walk in problem.md: the second F is "
        "blocked by the wall at (3, 2), and the last F would leave the grid.")


def test_longer_walk_with_revisits():
    got = ask(EXAMPLE, (5, 2), "FFLFRFFRFFFFRFFFFRRFFFLFFFFLFFF")
    assert got == ["4 1 S", "12"], (
        f"Expected ['4 1 S', '12'], got {got}. After the example the robot turns around (R R), walks back up "
        "column 5, along row 2 to the West, then down column 1 until the wall at (5, 1). Every cell on the way "
        "back was already visited, so the count stays 12: use a set, not a counter of moves.")


def test_no_commands():
    got = ask(["...", "..."], (1, 1), "")
    assert got == ["1 1 N", "1"], (
        f"An empty command line: the robot stays at the start facing N and has visited 1 cell; got {got}.")


def test_turns_only():
    assert ask(["."], (1, 1), "RRRR") == ["1 1 N", "1"], "Four right turns bring the robot back to N."
    assert ask(["."], (1, 1), "LLL") == ["1 1 E", "1"], "Three left turns from N: W, S, E."
    assert ask(["."], (1, 1), "L") == ["1 1 W", "1"], "One left turn from N faces W, not E."
    assert ask(["."], (1, 1), "RRL") == ["1 1 E", "1"], "R, R, L from N: E, S, then E."


def test_one_cell_grid():
    got = ask(["."], (1, 1), "FLFRFRRF")
    assert got == ["1 1 S", "1"], (
        f"In a 1 x 1 grid every F is skipped; only the turns count (L to W, R to N, R to E, R to S). Got {got}.")


def test_top_edge_does_not_wrap():
    got = ask(["..", ".."], (1, 1), "FLF")
    assert got == ["1 1 W", "1"], (
        f"Expected ['1 1 W', '1'], got {got}. Moving N from row 1 or W from column 1 leaves the grid and must be "
        "skipped. Check 0 <= row < r and 0 <= col < c BEFORE reading the grid: in Python grid[-1] is the last row.")


def test_surrounded_by_walls():
    got = ask([".#.", "#.#", ".#."], (2, 2), "FRFRFRFRF")
    assert got == ["2 2 N", "1"], (
        f"Every move is blocked by a wall, but the four turns still happen. Expected ['2 2 N', '1'], got {got}.")


def test_square_loop():
    got = ask(["...", "...", "..."], (2, 2), "FRFRFRFRF")
    assert got == ["1 2 N", "4"], (
        f"Expected ['1 2 N', '4'], got {got}. The robot visits (1, 2), (1, 3), (2, 3), then comes back to (2, 2) "
        "and (1, 2): only 4 different cells.")


def test_edge_blocks_then_turns():
    rows = [".....", ".#...", ".....", "...#."]
    got = ask(rows, (4, 1), "FFFFRFFFFFRFFL")
    assert got == ["3 5 E", "10"], (
        f"Expected ['3 5 E', '10'], got {got}. The fourth F in a row would go above row 1 and the sixth step East "
        "would go past column 5: both are skipped, and the next commands still run.")


def test_wall_on_the_next_cell_only():
    rows = ["....", ".#..", "...."]
    got = ask(rows, (3, 2), "FFRFLFF")
    assert got == ["1 3 N", "4"], (
        f"Expected ['1 3 N', '4'], got {got}. From (3, 2) facing N the wall at (2, 2) blocks both F. Turn right, "
        "step to (3, 3), turn left and go up to (2, 3) and (1, 3).")


def test_random_grids():
    rng = random.Random(56)
    for _ in range(15):
        r, c = rng.randint(1, 8), rng.randint(1, 8)
        rows = ["".join("#" if rng.random() < 0.25 else "." for _ in range(c)) for _ in range(r)]
        i, j = rng.randrange(r), rng.randrange(c)
        rows[i] = rows[i][:j] + "." + rows[i][j + 1:]
        cmds = "".join(rng.choice("FFFLR") for _ in range(rng.randint(0, 40)))
        got = ask(rows, (i + 1, j + 1), cmds)
        want = simulate(rows, (i + 1, j + 1), cmds)
        assert got == want, f"Grid {rows}, start {(i + 1, j + 1)}, commands {cmds!r}: expected {want}, got {got}."


def test_long_corridor_speed():
    n = 200000
    rows = ["." * n]
    cmds = "R" + "F" * (n + 5)
    got = ask(rows, (1, 1), cmds, timeout=8)
    assert got == [f"1 {n} E", str(n)], (
        f"A 1 x {n} corridor walked to the end: expected ['1 {n} E', '{n}'], got {got}. If it timed out, you keep "
        "the visited cells in a list (`in` on a list is O(n) per check); use a set.")


def test_big_grid_random_walk():
    rng = random.Random(5600)
    r, c = 500, 500
    rows = ["".join("#" if rng.random() < 0.2 else "." for _ in range(c)) for _ in range(r)]
    rows[250] = rows[250][:250] + "." + rows[250][251:]
    cmds = "".join(rng.choice("FFFFLR") for _ in range(200000))
    got = ask(rows, (251, 251), cmds, timeout=8)
    assert got == simulate(rows, (251, 251), cmds), "A 500 x 500 grid with 200000 random commands gives a different result."
