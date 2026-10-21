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
    assert run("rice\nmilk\ndal\nmilk\ndone\n") == [
        "Items: 4", "1. rice", "2. milk", "3. dal", "4. milk"], (
        "Store every item with append, keep duplicates, and number from 1.")


def test_empty():
    assert run("done\n") == ["Items: 0", "The list is empty."], (
        "When the first line is 'done', there are no items. Print the special message.")


def test_done_is_not_an_item():
    out = run("tea\ndone\n")
    assert out == ["Items: 1", "1. tea"], (
        "'done' only ends the input. Check for it before appending, so it is not stored.")


def test_lines_after_done_are_ignored():
    out = run("a\ndone\nb\n")
    assert out == ["Items: 1", "1. a"], "Stop reading as soon as you see 'done'."


def test_many_items():
    names = [f"item{i}" for i in range(50)]
    out = run("\n".join(names) + "\ndone\n")
    assert out[0] == "Items: 50", "Count with len() after the loop."
    assert out[-1] == "50. item49", "The last line should be numbered 50."
