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

import pytest


def test_example():
    assert run("3\nAB-1234\nab-1234\nAB1234\n") == [
        "AB-1234: valid", "ab-1234: invalid (letters)", "AB1234: invalid (length)", "Valid: 1 of 3"], (
        "Check length, then letters, then dash, then digits. Report only the first problem.")


@pytest.mark.parametrize("code, reason", [
    ("A", "length"), ("AB-12345", "length"), ("", "length"),
    ("A1-1234", "letters"), ("Ab-1234", "letters"), ("ÉB-1234", "letters"),
    ("AB_1234", "dash"), ("ABC1234", "dash"),
    ("AB-12a4", "digits"), ("AB-12 4", "digits"), ("AB-12²4", "digits"),
    ("a_-xyz!", "letters"),
])
def test_reasons(code, reason):
    got = run(f"1\n{code}\n")
    assert got == [f"{code}: invalid ({reason})", "Valid: 0 of 1"], (
        f"{code!r} should be invalid ({reason}); got {got}. Rules are checked in order and only A-Z / 0-9 count "
        "(isupper() and isdigit() accept letters and digits from other alphabets).")


def test_strip_and_count():
    assert run("2\n  ZZ-0000  \nQQ-9999\n") == ["ZZ-0000: valid", "QQ-9999: valid", "Valid: 2 of 2"], (
        "Strip each code before checking.")


def test_zero_codes():
    assert run("0\n") == ["Valid: 0 of 0"], "N can be 0."
