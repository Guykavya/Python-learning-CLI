import numpy as np
import pandas as pd
import pytest

from solution import evidence_table


def r(h, est, lo, hi, null=0.0, direction="up", margin=0.1):
    return {"hypothesis": h, "estimate": est, "ci_low": lo, "ci_high": hi, "null": null, "direction": direction, "margin": margin}


RESULTS = [
    r("H1 late deliveries", 2.90, 2.71, 3.09, null=1.0, margin=0.05),
    r("H2 customer mix", 0.02, -0.03, 0.05),
    r("H3 price change", 3.89, 0.59, 7.20),
    r("H4 season", -0.88, -1.4, -0.3),
    r("H5 new menu", 0.40, -0.20, 1.00),
]


def test_columns_and_order():
    t = evidence_table(RESULTS)
    assert list(t.columns) == ["hypothesis", "estimate", "CI", "verdict"], f"columns, got {list(t.columns)}"
    assert list(t["hypothesis"]) == [x["hypothesis"] for x in RESULTS], "one row per result, in the input order."


def test_verdicts():
    got = list(evidence_table(RESULTS)["verdict"])
    assert got == ["supported", "not supported", "supported", "not supported", "inconclusive"], (
        f"expected supported (CI above 1), not supported (within the margin), supported, not supported (opposite side), inconclusive; got {got}")


def test_ci_text():
    t = evidence_table(RESULTS)
    assert t.loc[0, "CI"] == "2.71 to 3.09" and t.loc[3, "CI"] == "-1.40 to -0.30", f"CI as 'lo to hi' with two decimals, got {list(t['CI'])}"


def test_direction_down():
    t = evidence_table([r("fewer returns", -2.0, -3.0, -1.0, direction="down"), r("fewer returns", 2.0, 1.0, 3.0, direction="down")])
    assert list(t["verdict"]) == ["supported", "not supported"], "for direction down, an interval below the null supports the hypothesis."


def test_touching_the_null_is_not_supported():
    t = evidence_table([r("edge", 1.0, 0.0, 2.0, margin=0.1)])
    assert t.loc[0, "verdict"] == "inconclusive", "ci_low == null is not 'above the null': the rule is strict."
