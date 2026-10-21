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
    assert run("5\npune tea 3\ndelhi rice 10\npune rice 2\npune tea 4\ndelhi dal 1\n") == [
        "delhi: 11", "  dal 1", "  rice 10", "pune: 9", "  rice 2", "  tea 7"]


def test_empty():
    assert run("0\n") == []


def test_cities_do_not_share_items():
    out = run("2\na x 1\nb y 2\n")
    assert out == ["a: 1", "  x 1", "b: 2", "  y 2"], (
        "Each city needs its own inner dict. If both cities show both items, they share one dict.")


def test_get_does_not_store():
    out = run("2\nc z 1\nc z 1\n")
    assert out == ["c: 2", "  z 2"], (
        "Use setdefault so the inner dict is stored in the outer dict.")
