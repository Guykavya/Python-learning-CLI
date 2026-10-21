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

def test_first_try():
    assert run("4321\n4321\n") == ["Welcome"], (
        "A correct first attempt prints only Welcome. Did you read more lines than needed?")


def test_second_try():
    assert run("4321\n1234\n4321\n") == ["Wrong PIN. 2 tries left", "Welcome"], "One wrong, then right."


def test_third_try():
    assert run("4321\n1\n2\n4321\n") == ["Wrong PIN. 2 tries left", "Wrong PIN. 1 try left", "Welcome"], (
        "After two wrong attempts, the message uses the singular 'try'.")


def test_blocked():
    assert run("4321\n1\n2\n3\n") == ["Wrong PIN. 2 tries left", "Wrong PIN. 1 try left", "Wrong PIN. Card blocked"], (
        "Three wrong attempts block the card. The last message is not '0 tries left'.")


def test_no_fourth_attempt_read():
    assert run("4321\n1\n2\n3\n4321\n") == ["Wrong PIN. 2 tries left", "Wrong PIN. 1 try left", "Wrong PIN. Card blocked"], (
        "Only 3 attempts are allowed. A correct fourth line must not be accepted.")


def test_pin_is_text():
    assert run("0042\n42\n 0042 \n") == ["Wrong PIN. 2 tries left", "Welcome"], (
        "Compare PINs as stripped text. '42' is not '0042'.")
