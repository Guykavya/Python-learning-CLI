import numpy as np
import pandas as pd
import pytest

from solution import FOREVER, lookup_key, scd2_apply

DIM = pd.DataFrame({"SurrogateKey": [1, 2], "CustomerID": ["C1", "C2"], "Region": ["North", "East"],
                    "ValidFrom": pd.to_datetime(["2020-01-01", "2021-05-01"]), "ValidTo": [FOREVER, FOREVER], "IsCurrent": [True, True]})
CHANGES = pd.DataFrame({"CustomerID": ["C1", "C2", "C3"], "Region": ["South", "East", "West"]})
AS_OF = "2024-07-01"


def test_old_row_closed_and_new_row_added():
    out = scd2_apply(DIM, CHANGES, AS_OF)
    assert out["SurrogateKey"].tolist() == [1, 2, 3, 4], f"C1 moves (new key 3), C2 unchanged, C3 is new (key 4); got {out['SurrogateKey'].tolist()}"
    old = out.iloc[0]
    assert old["Region"] == "North" and old["ValidTo"] == pd.Timestamp("2024-06-30") and not bool(old["IsCurrent"]), f"the old version is closed the day before; got {old.to_dict()}"
    new = out[out["SurrogateKey"] == 3].iloc[0]
    assert (new["CustomerID"], new["Region"], new["ValidFrom"], new["ValidTo"]) == ("C1", "South", pd.Timestamp(AS_OF), FOREVER) and bool(new["IsCurrent"]), f"new current row; got {new.to_dict()}"
    c3 = out[out["CustomerID"] == "C3"].iloc[0]
    assert c3["ValidFrom"] == pd.Timestamp(AS_OF) and bool(c3["IsCurrent"]), "a customer not in the dimension gets a new current row."


def test_unchanged_customers_and_the_input_are_not_touched():
    before = DIM.copy()
    out = scd2_apply(DIM, CHANGES, AS_OF)
    pd.testing.assert_frame_equal(DIM, before)
    c2 = out[out["CustomerID"] == "C2"]
    assert len(c2) == 1 and bool(c2["IsCurrent"].iloc[0]) and c2["ValidTo"].iloc[0] == FOREVER, "C2's region did not change: no new version."


def test_history_is_kept_and_lookup_by_date():
    out = scd2_apply(DIM, CHANGES, AS_OF)
    assert lookup_key(out, "C1", "2024-03-01") == 1, "an order from March still belongs to the North version."
    assert lookup_key(out, "C1", "2024-06-30") == 1 and lookup_key(out, "C1", "2024-07-01") == 3, "the day of the move belongs to the new version."
    assert lookup_key(out, "C2", "2030-01-01") == 2
    with pytest.raises(ValueError, match="no version valid on that date"):
        lookup_key(out, "C1", "2019-12-31")
    assert out["IsCurrent"].astype(bool).groupby(out["CustomerID"]).sum().eq(1).all(), "exactly one current row per customer."


def test_two_moves_in_a_row():
    once = scd2_apply(DIM, CHANGES, AS_OF)
    twice = scd2_apply(once, pd.DataFrame({"CustomerID": ["C1"], "Region": ["West"]}), "2025-01-01")
    assert twice["SurrogateKey"].tolist() == [1, 2, 3, 4, 5] and lookup_key(twice, "C1", "2024-12-31") == 3 and lookup_key(twice, "C1", "2025-01-01") == 5
