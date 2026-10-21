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
    stdin = "# settings\nwidth = 10\n\n  # indented comment\nheight = 4\nEND\n"
    assert run(stdin) == ["1: width = 10", "2: height = 4", "Kept 2 of 5 lines"], (
        "Blank lines and lines starting with # (after spaces) are skipped but still counted in N.")


def test_nothing_before_end():
    assert run("END\n") == ["Kept 0 of 0 lines"], "No lines at all: the final summary still prints."


def test_all_skipped():
    assert run("#a\n   \n\t# b\nEND\n") == ["Kept 0 of 3 lines"], "All three lines are blank or comments."


def test_hash_later_is_kept():
    assert run("x = 1  # note\nEND\n") == ["1: x = 1  # note", "Kept 1 of 1 lines"], (
        "Only lines whose FIRST non-space character is # are comments.")


def test_stops_at_end():
    assert run("a\nEND\nb\n") == ["1: a", "Kept 1 of 1 lines"], "Lines after END must not be read."


def test_end_must_be_exact():
    assert run("end\nEND\n") == ["1: end", "Kept 1 of 1 lines"], "Only the exact line END stops the loop."
