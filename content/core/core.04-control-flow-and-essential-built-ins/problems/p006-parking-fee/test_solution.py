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


def fee(v, h, d):
    return run(f"{v}\n{h}\n{d}\n")


@pytest.mark.parametrize("h, expected", [(1, 10), (4, 40), (5, 50), (6, 50), (24, 50)])
def test_bike_weekday_cap(h, expected):
    assert fee("bike", h, "weekday") == [f"Fee: {expected}"], (
        f"A bike for {h} hours on a weekday costs {expected}: 10 per hour, never more than 50.")


@pytest.mark.parametrize("h, expected", [(1, 40), (2, 40), (3, 65), (5, 115)])
def test_car_weekday(h, expected):
    assert fee("car", h, "weekday") == [f"Fee: {expected}"], (
        f"A car for {h} hours costs {expected}: 40 covers the first 2 hours, then 25 per extra hour.")


def test_truck():
    assert fee("truck", 3, "weekday") == ["Fee: 300"], "A truck pays 100 per hour."


def test_weekend_rules():
    assert fee("bike", 3, "weekend") == ["Fee: 0"], "Bikes park free at weekends."
    assert fee("car", 3, "weekend") == ["Fee: 85"], "A car at the weekend pays its normal fee + 20."
    assert fee("truck", 2, "weekend") == ["Fee: 220"], "A truck at the weekend pays its normal fee + 20."


@pytest.mark.parametrize("v", ["bike", "car", "truck"])
@pytest.mark.parametrize("d", ["weekday", "weekend"])
def test_zero_hours_is_free(v, d):
    assert fee(v, 0, d) == ["Fee: 0"], (
        f"0 hours costs nothing, even for a {v} at the {d}. Did you add the weekend extra anyway?")


def test_capitals_allowed():
    assert fee("CAR", 5, "Weekday") == ["Fee: 115"], "Normalise the text with .strip().lower() before comparing."
    assert fee("Truck", 2, "WEEKEND") == ["Fee: 220"], "The day may also have capitals."


def test_unknown_vehicle():
    assert fee("bus", 1, "weekday") == ["Unknown vehicle"], (
        "An unknown type prints only 'Unknown vehicle', with no Fee line.")
