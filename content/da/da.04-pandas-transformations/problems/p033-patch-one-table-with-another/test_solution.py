import pandas as pd

from solution import patch_customers


def old():
    return pd.DataFrame({
        "customer_id": ["C4", "C1", "C2", "C3", "C5"],
        "city": ["Surat", "Pune", None, "Agra", "Jaipur"],
        "segment": ["retail", "retail", "retail", "premium", None],
    })


def fixes():
    return pd.DataFrame({
        "customer_id": ["C2", "C3", "C9", "C5"],
        "city": ["Delhi", None, "Mumbai", None],
        "segment": [None, "business", "retail", "business"],
    })


def test_shape_rows_and_order():
    out = patch_customers(old(), fixes())
    assert len(out) == 5, "the result has exactly the rows of old (5); a fix for an unknown id (C9) must not add a row"
    assert out["customer_id"].tolist() == ["C4", "C1", "C2", "C3", "C5"], "keep old's row order (did you sort, as combine_first does?)"
    assert list(out.columns) == ["customer_id", "city", "segment"], "keep old's columns, in old's order"
    assert out.index.tolist() == list(range(5)), "return a fresh index 0..4 (reset_index)"


def test_fix_wins():
    out = patch_customers(old(), fixes()).set_index("customer_id")
    assert out.loc["C2", "city"] == "Delhi", "C2's missing city must come from the fix (Delhi)"
    assert out.loc["C3", "segment"] == "business", "C3's segment: the fix (business) must WIN over the old value (premium)"
    assert out.loc["C5", "segment"] == "business", "C5's missing segment must come from the fix"


def test_missing_fix_does_not_erase():
    out = patch_customers(old(), fixes()).set_index("customer_id")
    assert out.loc["C3", "city"] == "Agra", "the fix for C3 has no city: a missing fix must NOT erase Agra"
    assert out.loc["C2", "segment"] == "retail", "the fix for C2 has no segment: keep retail"
    assert out.loc["C5", "city"] == "Jaipur", "the fix for C5 has no city: keep Jaipur"


def test_untouched_customers():
    out = patch_customers(old(), fixes()).set_index("customer_id")
    assert out.loc["C1"].tolist() == ["Pune", "retail"] and out.loc["C4"].tolist() == ["Surat", "retail"], (
        "customers without a fix keep every value (did you patch by row position instead of by customer_id?)")


def test_extra_column_in_fixes_is_ignored():
    f = fixes().assign(phone=["1", "2", "3", "4"])
    out = patch_customers(old(), f)
    assert list(out.columns) == ["customer_id", "city", "segment"], "a column old does not have (phone) must not be added"


def test_inputs_unchanged():
    o, f = old(), fixes()
    o0, f0 = o.copy(), f.copy()
    patch_customers(o, f)
    pd.testing.assert_frame_equal(o, o0, obj="old (update works in place: call it on a NEW frame, not on old)")
    pd.testing.assert_frame_equal(f, f0, obj="fixes")
