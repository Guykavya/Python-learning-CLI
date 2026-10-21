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
    assert run("6\nravi\nasha\nravi\nmeena\nasha\nravi\n") == [
        "Unique: 3", "ravi", "asha", "meena"], "Keep the order of each name's first visit."


def test_zero():
    assert run("0\n") == ["Unique: 0"], "With no visits, print only the count."


def test_all_same():
    assert run("3\nx\nx\nx\n") == ["Unique: 1", "x"]


def test_case_matters():
    assert run("2\nAsha\nasha\n") == ["Unique: 2", "Asha", "asha"], "Names are case-sensitive."


def test_large_is_fast():
    n = 100000
    names = [f"user{i}" for i in range(n)]
    out = run(f"{n}\n" + "\n".join(names + []) + "\n")
    assert out[0] == f"Unique: {n}" and out[-1] == f"user{n - 1}", (
        "All 100,000 names are distinct. A list membership check is O(n) per name, so the whole "
        "program becomes O(n^2). Use a set for 'seen'.")
