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


def test_example():
    cmds = "set 5 7 10\nset 5 900000000 -3\nset 2 7 4\nget 5 7\nget 1 1\nrow 5\ncol 7\nset 5 7 0\ncount\ncol 7\nend\n"
    assert run(cmds) == ["10", "0", "7", "14", "2", "4"]


def test_overwrite_updates_sums():
    out = run("set 1 1 5\nset 1 1 2\nrow 1\ncol 1\ncount\nend\n")
    assert out == ["2", "2", "1"], "Overwriting must subtract the old value from the row and column sums."


def test_clear_missing_cell():
    assert run("set 3 3 0\ncount\nrow 3\nend\n") == ["0", "0"], "Setting 0 on an empty cell changes nothing."


def test_empty_queries():
    assert run("row 999999999\ncol 0\nget 0 0\nend\n") == ["0", "0", "0"]


def test_many_commands_fast():
    lines = []
    for i in range(50000):
        lines.append(f"set 1 {i} 1")
    for i in range(50000):
        lines.append("row 1")
    lines.append("end")
    out = run("\n".join(lines) + "\n")
    assert len(out) == 50000 and out[-1] == "50000", (
        "row must be O(1). Looping over all cells for every query is too slow; keep running sums.")
