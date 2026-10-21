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
    assert run("a a b c c c a\n") == ["a*2 b c*3 a", "Runs: 4"], (
        "The final 'a' is a separate run. A dict would merge it with the first run.")


def test_empty():
    assert run("\n") == ["(empty)", "Runs: 0"]


def test_single():
    assert run("x\n") == ["x", "Runs: 1"], "A run of one is written without *1."


def test_all_same():
    assert run("7 7 7 7\n") == ["7*4", "Runs: 1"]


def test_no_repeats():
    assert run("a b a b\n") == ["a b a b", "Runs: 4"]
