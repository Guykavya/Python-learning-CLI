import numpy as np
import pandas as pd
import pytest

from datetime import date, datetime

from openpyxl.utils.datetime import from_excel, to_excel

from solution import from_serial, to_serial

DATES = [datetime(1900, 3, 1), datetime(1999, 12, 31), datetime(2000, 2, 29), datetime(2024, 3, 15), datetime(2024, 12, 31), datetime(2100, 1, 1)]


@pytest.mark.parametrize("d", DATES)
def test_matches_openpyxl(d):
    assert to_serial(d) == pytest.approx(to_excel(d)), (
        f"{d:%Y-%m-%d}: expected {to_excel(d)}, got {to_serial(d)}. Excel counts 1900-01-01 as day 1 and keeps a fake 29 Feb 1900, so use 1899-12-30 as the day 0.")


def test_hand_values():
    assert to_serial(datetime(2024, 3, 15)) == 45366.0, "15 March 2024 is serial 45366."
    assert to_serial(date(2024, 3, 15)) == 45366.0, "a date (no time) is midnight."
    assert to_serial(datetime(2024, 3, 15, 12, 0)) == 45366.5, "noon is half a day."


@pytest.mark.parametrize("n", [61, 45366, 45366.25, 45366.75, 47483.5])
def test_from_serial_matches_openpyxl(n):
    got, ref = from_serial(n), from_excel(n)
    assert abs((got - ref).total_seconds()) < 1e-3, f"serial {n}: expected {ref}, got {got}."


def test_round_trip_and_types():
    d = datetime(2024, 7, 4, 18, 30)
    assert from_serial(to_serial(d)) == d, "from_serial(to_serial(d)) must give d back."
    assert isinstance(to_serial(d), float) and isinstance(from_serial(45000), datetime), "a float serial and a datetime."
    assert from_serial(45366.25) == datetime(2024, 3, 15, 6, 0), "0.25 of a day is 06:00."
