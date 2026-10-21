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
    assert run("a b c d e f g\n3\n") == ["1: a b c", "2: d e f", "3: g"], (
        "The last chunk may be shorter. range(0, n, k) gives every start position.")


def test_exact_fit():
    assert run("1 2 3 4\n2\n") == ["1: 1 2", "2: 3 4"]


def test_k_bigger_than_list():
    assert run("x y\n5\n") == ["1: x y"]


def test_k_one():
    assert run("p q\n1\n") == ["1: p", "2: q"]


def test_empty():
    assert run("\n3\n") == ["No chunks"]
