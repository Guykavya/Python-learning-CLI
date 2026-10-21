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
    assert run("3\nAsha 82\nRavi 91\nMeena 77\n") == [
        "Names: Asha Ravi Meena", "Scores: 82 91 77", "Total: 250", "Best: Ravi (91)"]


def test_best_is_by_score_not_name():
    out = run("2\nZed 10\nAmy 50\n")
    assert out[3] == "Best: Amy (50)", "max(d) compares names. Use max(d, key=d.get) to compare scores."


def test_tie_first_wins():
    assert run("3\nA 5\nB 9\nC 9\n")[3] == "Best: B (9)", "On a tie, use the first name in the dict."


def test_repeated_name():
    assert run("3\nA 1\nB 2\nA 10\n") == [
        "Names: A B", "Scores: 10 2", "Total: 12", "Best: A (10)"], (
        "A repeated name replaces the score but keeps its first position.")


def test_negative_scores():
    assert run("2\nX -5\nY -2\n")[3] == "Best: Y (-2)"
