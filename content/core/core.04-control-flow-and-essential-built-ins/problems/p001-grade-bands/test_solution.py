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


@pytest.mark.parametrize("mark, grade", [
    (100, "A"), (95, "A"), (90, "A"),
    (89, "B"), (75, "B"),
    (74, "C"), (60, "C"),
    (59, "D"), (40, "D"),
    (39, "F"), (0, "F"),
])
def test_bands_and_boundaries(mark, grade):
    got = run(f"{mark}\n")
    assert got == [grade], (
        f"Mark {mark} should give {grade}, got {got}. Boundary marks belong to the higher band, "
        "so use >=. Also check the order of your branches: the first true one wins.")


@pytest.mark.parametrize("mark", [101, 150, -1, -40])
def test_invalid(mark):
    got = run(f"{mark}\n")
    assert got == ["invalid"], (
        f"Mark {mark} is outside 0 to 100, expected ['invalid'], got {got}. Check this before the bands.")
