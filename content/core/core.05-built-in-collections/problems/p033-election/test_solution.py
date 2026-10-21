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
    assert run("5\nravi\nasha\nravi\nasha\nmeena\n") == [
        "asha: 2", "ravi: 2", "meena: 1", "Tie: asha, ravi"]


def test_winner():
    assert run("3\nb\na\nb\n") == ["b: 2", "a: 1", "Winner: b"]


def test_no_votes():
    assert run("0\n") == ["No votes"], "With no votes, max() of an empty collection would crash."


def test_three_way_tie():
    assert run("3\nz\ny\nx\n")[-1] == "Tie: x, y, z"


def test_large_is_fast():
    n = 200000
    names = [f"c{i % 1000}" for i in range(n)]
    out = run(f"{n}\n" + "\n".join(names) + "\n")
    assert out[0] == "c0: 200" and len(out) == 1001, (
        "Count with a dict in one pass. Calling votes.count(name) for each name is O(n^2).")
