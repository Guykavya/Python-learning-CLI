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
    assert run("5\nravi IT 50000\nasha HR 45000\nmeena IT 65000\njohn HR 45000\nzoe IT 50000\n") == [
        "HR asha 45000", "HR john 45000", "IT meena 65000", "IT ravi 50000", "IT zoe 50000"]


def test_salary_numeric():
    assert run("2\na X 9000\nb X 10000\n") == ["X b 10000", "X a 9000"], (
        "Compare salaries as numbers. As text, '9000' > '10000'.")


def test_reverse_only_salary():
    out = run("3\nb B 1\na A 1\nc A 2\n")
    assert out == ["A c 2", "A a 1", "B b 1"], (
        "Only salary is descending. reverse=True on everything would also flip departments.")


def test_empty():
    assert run("0\n") == []
