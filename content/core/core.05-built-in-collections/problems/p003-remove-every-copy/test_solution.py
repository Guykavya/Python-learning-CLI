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
    assert run("to be or not to be\nto\n") == ["be or not be", "Removed: 2"]


def test_adjacent_copies():
    assert run("a a a b a\na\n") == ["b", "Removed: 4"], (
        "Adjacent copies are skipped if you remove items while looping over the same list. "
        "Build a new list instead.")


def test_target_missing():
    assert run("x y z\nq\n") == ["x y z", "Removed: 0"], (
        "When the target is not there, nothing changes. remove() would raise ValueError here.")


def test_everything_removed():
    assert run("go go go\ngo\n") == ["(empty)", "Removed: 3"], (
        "When nothing is left, print (empty).")


def test_empty_line():
    assert run("\nword\n") == ["(empty)", "Removed: 0"], "An empty line has no words."


def test_case_sensitive():
    assert run("Be be BE\nbe\n") == ["Be BE", "Removed: 1"], "Only exact matches are removed."
