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
    cmds = "2 3\nbook 0 0\nsave\nbook 1 2\nbook 0 0\nundo\nbook 0 1\ndone\n"
    assert run(cmds) == [
        "Booked 0 0", "Saved", "Booked 1 2", "Seat 0 0 is taken", "Undid 1 2", "Booked 0 1",
        "Seats:", "XX.", "...", "Free: 4", "Snapshot:", "X..", "..."]


def test_rows_are_separate():
    out = run("2 2\nbook 0 0\nbook 1 0\ndone\n")
    assert out[:2] == ["Booked 0 0", "Booked 1 0"], (
        "Booking (0, 0) must not book (1, 0). [['.'] * cols] * rows repeats ONE row object; "
        "build each row separately with a comprehension.")


def test_free_count():
    out = run("2 2\nbook 1 1\ndone\n")
    assert "Free: 3" in out, (
        "seats.count('.') counts items of the outer list, which are rows, so it is always 0. "
        "Count the '.' in every row.")


def test_undo_most_recent():
    out = run("1 3\nbook 0 0\nbook 0 2\nundo\ndone\n")
    assert out[2] == "Undid 0 2", "undo cancels the LATEST booking: pop() from the end, not pop(0)."
    assert out[4] == "X..", "After undoing (0, 2), only (0, 0) stays booked."


def test_nothing_to_undo():
    assert run("1 1\nundo\ndone\n") == ["Nothing to undo", "Seats:", ".", "Free: 1", "Snapshot:", "."]


def test_start_snapshot_is_not_an_alias():
    out = run("1 2\nbook 0 1\ndone\n")
    assert out[-1] == "..", (
        "Without save, the snapshot is the starting layout. snapshot = seats is an alias, so it "
        "shows later bookings. Copy every row.")


def test_saved_snapshot_is_deep():
    out = run("2 2\nsave\nbook 0 0\ndone\n")
    assert out[-2:] == ["..", ".."], (
        "The snapshot was saved before the booking, so it must stay empty. seats.copy() is "
        "shallow: the rows are shared. Use [row[:] for row in seats].")
