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

VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}


def value(s):
    t = 0
    for i, c in enumerate(s):
        if i + 1 < len(s) and VAL[c] < VAL[s[i + 1]]:
            t -= VAL[c]
        else:
            t += VAL[c]
    return t


def test_example():
    assert run("3\nxiv\nMCMXCIV\n12\n") == ["XIV = 14", "MCMXCIV = 1994", "12 is not a Roman numeral"], (
        "Subtract a symbol when the NEXT one is bigger; otherwise add it.")


@pytest.mark.parametrize("s", ["I", "II", "III", "IV", "V", "IX", "XL", "XC", "CD", "CM", "LVIII",
                               "MMXXVI", "MMMCMXCIX", "DCCCXC", "IIII", "VX", "MDCLXVI"])
def test_numerals(s):
    got = run(f"1\n{s}\n")
    assert got == [f"{s} = {value(s)}"], (
        f"{s} should be {value(s)}, got {got}. Is the last symbol counted? Do equal neighbours add (II = 2)?")


@pytest.mark.parametrize("bad, shown", [("", ""), ("ABC", "ABC"), ("X I", "X I"), ("x1", "X1"), ("  ", "")])
def test_invalid(bad, shown):
    got = run(f"1\n{bad}\n")
    assert got == [f"{shown} is not a Roman numeral".strip()], (
        f"{bad!r} is not a Roman numeral; expected the 'is not a Roman numeral' message, got {got}. "
        "Reject empty lines and any character outside IVXLCDM.")


def test_zero_lines():
    assert run("0\n") == [], "N = 0: print nothing."
