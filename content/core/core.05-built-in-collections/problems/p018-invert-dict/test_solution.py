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
    assert run("4\napple red\nbanana yellow\ncherry red\nlime green\n") == [
        "red -> cherry", "yellow -> banana", "green -> lime"], (
        "cherry overwrites apple for 'red', but 'red' keeps its first position.")


def test_repeated_key():
    out = run("3\na 1\nb 2\na 3\n")
    assert out == ["3 -> a", "2 -> b"], (
        "Key 'a' repeats: its value becomes 3, but 'a' stays first in the dict. "
        "So the inverted dict is {'3': 'a', '2': 'b'}.")


def test_all_unique():
    assert run("2\nx 1\ny 2\n") == ["1 -> x", "2 -> y"]


def test_empty():
    assert run("0\n") == [], "With no pairs, print nothing."
