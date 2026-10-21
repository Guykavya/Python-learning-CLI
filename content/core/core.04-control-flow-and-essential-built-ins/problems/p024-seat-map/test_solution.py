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

def test_example():
    assert run("3\nAB CD\n1A 2D 3B 9Z\n") == [
        "Row  1: XB CD", "Row  2: AB CX", "Row  3: AX CD", "Free: 9 of 12"], (
        "Booked seats show X, the aisle stays a space, and 9Z does not exist so it is ignored.")


def test_nothing_booked():
    assert run("2\nABC\n\n") == ["Row  1: ABC", "Row  2: ABC", "Free: 6 of 6"], (
        "An empty booking line means every seat is free.")


def test_two_digit_rows():
    out = run("12\nA B\n10A 12B 1B\n")
    assert out[0] == "Row  1: A X", "Row 1, seat B is booked."
    assert out[9] == "Row 10: X B", "Row numbers use 2 characters: 'Row 10:' and 'Row  1:'."
    assert out[11] == "Row 12: A X"
    assert out[12] == "Free: 21 of 24", "24 seats, 3 booked. The aisle is not a seat."


def test_row_number_must_match_exactly():
    out = run("11\nA\n11A\n")
    assert out[0] == "Row  1: A", (
        "Seat 1A is not booked; only 11A is. Compare the whole seat name, not just part of it.")
    assert out[10] == "Row 11: X"
