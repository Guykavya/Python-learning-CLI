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
    assert run("Hello, World!\n") == ["l: 3", "o: 2", "d: 1"], (
        "Ties are alphabetical: d, e, h, r and w all have 1, so d wins third place.")


def test_no_letters():
    assert run("123 !?\n") == ["No letters"]


def test_case_ignored():
    assert run("AaBb a\n") == ["a: 3", "b: 2"], "Lowercase first so A and a count together."


def test_fewer_than_three():
    assert run("zz\n") == ["z: 2"]
