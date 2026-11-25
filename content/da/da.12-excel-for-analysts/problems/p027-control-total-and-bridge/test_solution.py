import numpy as np
import pandas as pd
import pytest

from solution import bridge

REGIONS = ["East", "North", "South"]
VALID = {"P01", "P02", "P03"}

DF = pd.DataFrame([
    # region, units, price, discount, code                      revenue
    ("North", 2, 50.0, 0.0, "P01"),        # 100   fine
    ("south", "3", 20.0, 0.0, "p02"),      # 60    fine (case differences are matched, text units are numbers)
    ("North ", 1, 50.0, 0.0, "P03"),       # 50    region not matched (trailing space)
    ("East", 4, 25.0, 0.0, "P07 "),        # 100   code not found (trailing space)
    ("West", 1, 80.0, 0.5, "PO5"),         # 40    both faults: counted once, under the code
    ("East", 2, 10.0, 0.5, "P01"),         # 10    fine
    ("Nort", 5, 4.0, 0.0, "P02"),          # 20    region not matched (misspelled)
], columns=["region", "units", "unit_price", "discount", "product_code"])


def test_totals_and_causes():
    b = bridge(DF, REGIONS, VALID)
    assert b["control_total"] == pytest.approx(380.0), f"the revenue of all lines is 380, got {b['control_total']}"
    assert b["grid_total"] == pytest.approx(170.0), f"lines with a found code and a matched region: 100 + 60 + 10 = 170, got {b['grid_total']}"
    assert b["gap"] == pytest.approx(210.0)
    assert b["causes"] == {"product code not found": pytest.approx(140.0), "region not matched": pytest.approx(70.0)}, f"code: 100 + 40, region: 50 + 20; got {b['causes']}"


def test_the_bridge_adds_up_exactly():
    b = bridge(DF, REGIONS, VALID)
    assert abs(b["unexplained"]) < 1e-9, f"every line is in exactly one group: nothing is left unexplained, got {b['unexplained']}"
    assert abs(sum(b["causes"].values()) - b["gap"]) < 1e-9, "the causes add up to the gap."
    assert b["grid_total"] + sum(b["causes"].values()) == pytest.approx(b["control_total"]), "grid total + causes = control total."


def test_clean_data_has_no_gap():
    clean = DF.iloc[[0, 1, 5]].assign(region=["North", "South", "East"], product_code=["P01", "P02", "P01"])
    b = bridge(clean, REGIONS, VALID)
    assert b["gap"] == 0 and b["causes"] == {"product code not found": 0.0, "region not matched": 0.0}, "no faults, no gap."


def test_unexplained_shows_what_the_rules_miss():
    odd = pd.DataFrame([("North", 1, 10.0, 0.0, "P01")], columns=DF.columns)
    assert bridge(odd, REGIONS, VALID)["unexplained"] == 0
