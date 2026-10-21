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

HEADER = "No  Subject     Marks  Result"


def test_example():
    assert run("Maths Physics\n91 38\n") == [
        HEADER,
        "1   Maths          91  PASS",
        "2   Physics        38  FAIL",
        "Passed 1 of 2",
        "Overall: FAIL",
    ], "Check the widths: No in 4 (left), Subject in 12 (left), Marks in 5 (right), then two spaces."


def test_all_pass_and_boundary():
    out = run("English Hindi Chemistry\n40 100 75\n")
    assert out[1] == "1   English        40  PASS", "Exactly 40 is a pass."
    assert out[-2:] == ["Passed 3 of 3", "Overall: PASS"], "Every subject passed."


def test_many_rows_numbering():
    subs = " ".join(f"S{i}" for i in range(1, 12))
    marks = " ".join(["50"] * 10 + ["0"])
    out = run(f"{subs}\n{marks}\n")
    assert out[10] == "10  S10            50  PASS", "Row 10: the number still fits in 4 characters."
    assert out[11] == "11  S11             0  FAIL"
    assert out[-2:] == ["Passed 10 of 11", "Overall: FAIL"]


def test_mismatch():
    assert run("A B\n1\n") == ["Mismatch"], "Different counts: print only Mismatch."


def test_empty():
    assert run("\n\n") == [HEADER, "Passed 0 of 0", "Overall: PASS"], (
        "No subjects: all() of nothing is True, so the overall result is PASS.")
