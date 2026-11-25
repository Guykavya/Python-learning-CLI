import numpy as np
import pandas as pd
import pytest

from solution import check_kpi

GOOD = {"name": "Monthly churn", "numerator": "opening actives whose last week is in the month",
        "denominator": "customers active in the first week", "grain": "month", "owner": "Head of Retention",
        "direction": "down", "type": "lagging", "unit": "%"}


def test_complete_definition():
    assert check_kpi(GOOD) == [], f"a complete definition has no problems, got {check_kpi(GOOD)}"


def test_missing_and_empty_fields_in_order():
    d = dict(GOOD)
    del d["grain"]
    d["owner"] = ""
    assert check_kpi(d) == ["missing field: grain", "missing field: owner"], "a missing key and an empty value are both missing, in the order of REQUIRED."


def test_vanity_metric():
    d = {"name": "Sign-ups ever", "numerator": "sign-ups", "grain": "all time", "owner": "", "direction": "up", "type": "vanity", "unit": "count"}
    assert check_kpi(d) == ["missing field: owner", "vanity metric: no decision depends on it"], f"got {check_kpi(d)}"


def test_unknown_type_and_direction():
    d = dict(GOOD, type="important", direction="higher")
    assert check_kpi(d) == ["unknown type: important", "direction must be 'up' or 'down'"], f"got {check_kpi(d)}"


def test_percentage_needs_denominator_but_count_does_not():
    d = dict(GOOD)
    d.pop("denominator")
    assert check_kpi(d) == ["a percentage needs a denominator"], "a % KPI without a denominator is not defined."
    count = dict(d, unit="count")
    assert check_kpi(count) == [], "a count needs no denominator."


def test_missing_type_is_reported_once():
    d = dict(GOOD)
    d.pop("type")
    assert check_kpi(d) == ["missing field: type"], "do not also report 'unknown type: None'."
