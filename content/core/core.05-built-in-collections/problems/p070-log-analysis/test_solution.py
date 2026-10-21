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
    data = "6\n1 asha home\n1 ravi cart\n2 asha home\n2 meena home\n3 asha about\n3 ravi home\n"
    assert run(data) == [
        "Events: 6", "Distinct users: 3", "Top pages:", "  home 4", "  about 1", "  cart 1",
        "Loyal users: asha", "Busiest day: 1 (2)"]


def test_empty():
    assert run("0\n") == ["Events: 0"]


def test_no_loyal_users():
    out = run("2\n1 a x\n2 b x\n")
    assert out[-2] == "Loyal users: none"


def test_busiest_tie_smaller_day():
    out = run("4\n5 a p\n5 b p\n2 a q\n2 c q\n")
    assert out[-1] == "Busiest day: 2 (2)", "Days 2 and 5 both have 2 visits; choose the smaller day."


def test_single_day_everyone_loyal():
    out = run("3\n7 z p\n7 y p\n7 z q\n")
    assert out[1] == "Distinct users: 2" and out[-2] == "Loyal users: y z"


def test_large_is_fast():
    n = 200000
    lines = [str(n)] + [f"{i % 7} u{i % 50000} page{i % 13}" for i in range(n)]
    out = run("\n".join(lines) + "\n")
    assert out[1] == "Distinct users: 50000", (
        "Use a set for distinct users; checking a list for each of 200,000 lines is O(n^2).")
    assert out[-1].startswith("Busiest day: 0 (")
