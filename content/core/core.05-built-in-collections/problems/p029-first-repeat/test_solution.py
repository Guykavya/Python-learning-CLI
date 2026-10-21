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
    assert run("red blue green blue red\n") == ["blue at 2 and 4"], (
        "blue's second occurrence (4) comes before red's (5).")


def test_no_repeats():
    assert run("a b c\n") == ["No repeats"]


def test_empty():
    assert run("\n") == ["No repeats"]


def test_adjacent():
    assert run("x y y x\n") == ["y at 2 and 3"]


def test_large_is_fast():
    words = [f"w{i}" for i in range(100000)] + ["w5"]
    out = run(" ".join(words) + "\n")
    assert out == ["w5 at 6 and 100001"], (
        "Only the last word repeats. A list or slice search for each word is O(n^2) and too slow; "
        "a dict lookup is O(1).")
