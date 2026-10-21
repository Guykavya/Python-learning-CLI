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
    assert run("ten\n0\n 7\n") == ["Invalid: ten", "Invalid: 0", "Accepted 7 after 3 attempts"], (
        "Each bad line prints 'Invalid: ...'. 0 is outside 1..10. ' 7' is valid after strip().")


def test_first_try_singular():
    assert run("10\n") == ["Accepted 10 after 1 attempt"], "One attempt: use the singular word 'attempt'."


def test_boundaries():
    assert run("11\n1\n") == ["Invalid: 11", "Accepted 1 after 2 attempts"], "11 is too big, 1 is allowed."


def test_text_that_is_not_digits_does_not_crash():
    out = run("-3\n4.5\nfive\n\n05\n")
    assert out == ["Invalid: -3", "Invalid: 4.5", "Invalid: five", "Invalid:", "Accepted 5 after 5 attempts"], (
        "Check isdigit() before calling int(). '-3', '4.5' and an empty line are all invalid; "
        "'05' is valid and is printed as 5.")


def test_stops_reading_after_valid():
    assert run("3\nnot read\n") == ["Accepted 3 after 1 attempt"], "Leave the loop as soon as a valid line arrives."
