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
    assert run("Asha Ravi Meena\nPPPA\nPAAA\npppp\n") == [
        "1. Asha: 3/4 (75%)", "2. Ravi: 1/4 (25%) LOW", "3. Meena: 4/4 (100%)", "Low attendance: 1"], (
        "Compare with the example in problem.md line by line.")


def test_first_student_included():
    out = run("Zara\nPP\n")
    assert out[0].startswith("1. Zara:"), (
        f"Got {out}. The first student is missing or numbered wrongly. range(1, len(names)) starts at "
        "position 1; use enumerate(names, start=1).")


def test_absent_is_not_present():
    out = run("Kiran\nAAAP\n")
    assert out[0].startswith("1. Kiran: 1/4"), (
        f"Got {out}. Absent marks are being counted as present. mark == 'P' or 'p' is always true, "
        "because 'p' on its own is truthy.")


def test_percent_not_floored():
    out = run("Dev\nPPA\n")
    assert out[0] == "1. Dev: 2/3 (67%) LOW", (
        f"Got {out}. 2 out of 3 is 66.67%, shown as 67%. Floor division // gives 0 here.")


def test_exactly_75_is_not_low():
    out = run("Ira\nPPPA\n")
    assert out == ["1. Ira: 3/4 (75%)", "All students at 75% or above"], (
        f"Got {out}. 75% is not below 75, so it is not LOW (use < 75).")


def test_summary_only_once_and_right():
    out = run("A B\nA\nP\n")
    assert out == ["1. A: 0/1 (0%) LOW", "2. B: 1/1 (100%)", "Low attendance: 1"], (
        f"Got {out}. 'All students at 75% or above' must not print when someone is low. A loop else runs "
        "whenever the loop has no break, so it always ran here.")


def test_lowercase_and_many():
    out = run("P1 P2 P3 P4\npapa\nPPPPPPPA\nppppA\naaaaaaaaaP\n")
    assert out == ["1. P1: 2/4 (50%) LOW", "2. P2: 7/8 (88%)", "3. P3: 4/5 (80%)", "4. P4: 1/10 (10%) LOW",
                   "Low attendance: 2"], f"Got {out}"
