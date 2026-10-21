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
            f"Your program took longer than {timeout} seconds. Look for an infinite loop, "
            "or an input() call waiting for a line that never comes.") from None
    assert r.returncode == 0, f"Your program crashed.\n{r.stderr}"
    return [line.rstrip() for line in r.stdout.strip().splitlines()]

def test_example():
    assert run("12.50\n3\n40.25\ndone\n") == ["Items: 3", "Total: 55.75"], (
        "Add up every price before 'done' and count them.")


def test_no_items():
    assert run("done\n") == ["Items: 0", "Total: 0.00"], (
        "When 'done' is first, the loop body never runs. Start the count and total at 0.")


def test_sentinel_any_case_and_spaces():
    assert run("5\n  DONE  \n") == ["Items: 1", "Total: 5.00"], (
        "Strip spaces and compare in lower case: '  DONE  ' is the stop word.")


def test_stops_at_sentinel():
    assert run("1\ndone\n99\n") == ["Items: 1", "Total: 1.00"], (
        "Nothing after 'done' should be read or counted. break leaves the loop at once.")


def test_many_items():
    prices = [0.1] * 10 + [100]
    stdin = "".join(f"{p}\n" for p in prices) + "done\n"
    assert run(stdin) == ["Items: 11", "Total: 101.00"], "Eleven prices: ten of 0.1 and one of 100."
