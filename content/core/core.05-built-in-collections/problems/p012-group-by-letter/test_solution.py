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
    assert run("apple Banana avocado cherry bean Apricot\n") == [
        "a: apple avocado Apricot", "b: Banana bean", "c: cherry"]


def test_empty():
    assert run("\n") == [], "No words, no groups, no output."


def test_get_does_not_store():
    assert run("x1 x2 x3\n") == ["x: x1 x2 x3"], (
        "All three words belong in one group. If only one shows, you may be using get(), which "
        "does not store the new list. Use setdefault().")


def test_order_of_groups():
    assert run("zoo Ant zebra ant\n") == ["z: zoo zebra", "a: Ant ant"], (
        "Groups follow first-seen order, not alphabetical order. Words keep their spelling.")
