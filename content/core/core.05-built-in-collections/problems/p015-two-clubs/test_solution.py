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
    assert run("asha ravi meena kiran\nravi kiran john ravi\n") == [
        "Both: kiran ravi", "Only Python: asha meena", "Only Chess: john",
        "Either: asha john kiran meena ravi"], "Each line is one set operation, printed sorted."


def test_both_empty():
    assert run("\n\n") == ["Both: -", "Only Python: -", "Only Chess: -", "Either: -"], (
        "Empty lines give empty sets. Print '-' for an empty result.")


def test_repeats_count_once():
    out = run("a a a\na\n")
    assert out == ["Both: a", "Only Python: -", "Only Chess: -", "Either: a"], (
        "Repeated names count once. A set removes repeats automatically.")


def test_disjoint():
    out = run("b a\nd c\n")
    assert out == ["Both: -", "Only Python: a b", "Only Chess: c d", "Either: a b c d"]
