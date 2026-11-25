import numpy as np
import pandas as pd
import pytest

import json

from solution import fingerprint, provenance


def panel():
    return pd.DataFrame({"customer_id": [1, 1, 2, 3], "week": pd.to_datetime(["2024-01-01", "2024-01-08", "2024-01-08", "2024-03-04"]),
                         "price": [599, 599, 849, 599]})


def customers():
    return pd.DataFrame({"customer_id": [1, 2, 3], "last_week": pd.to_datetime(["2024-01-08", pd.NaT, pd.NaT])})


def test_fingerprint_shape_and_stability():
    fp = fingerprint(panel())
    assert isinstance(fp, str) and len(fp) == 10 and all(c in "0123456789abcdef" for c in fp), f"10 lowercase hex characters, got {fp!r}"
    assert fingerprint(panel()) == fp, "the same data must give the same fingerprint."
    assert fingerprint(customers()) == fingerprint(customers()), "NaT values must hash consistently too."


def test_fingerprint_detects_changes():
    p = panel()
    changed = p.copy()
    changed.loc[0, "price"] += 1
    assert fingerprint(changed) != fingerprint(p), "one changed cell must change the fingerprint."
    assert fingerprint(p.iloc[::-1]) != fingerprint(p), "a different row order is a different table: the fingerprint changes."


def test_index_is_ignored():
    p = panel()
    assert fingerprint(p.set_axis([10, 11, 12, 13])) == fingerprint(p), "use index=False: relabelling the rows is not a change of data."


def test_provenance_dict():
    prov = provenance({"panel": panel(), "customers": customers()}, "2025-01-06")
    assert prov["rows"] == {"panel": 4, "customers": 3}, f"row counts, got {prov['rows']}"
    assert prov["fingerprints"] == {"panel": fingerprint(panel()), "customers": fingerprint(customers())}
    assert (prov["date_from"], prov["date_to"]) == ("2024-01-01", "2024-03-04"), "date range of the 'week' column, as YYYY-MM-DD."
    assert prov["analysis_date"] == "2025-01-06"
    json.dumps(prov)


def test_no_date_column():
    prov = provenance({"customers": customers()}, "2025-01-06")
    assert prov["date_from"] is None and prov["date_to"] is None, "no frame has the date column: None."
