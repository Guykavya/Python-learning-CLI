import math
import warnings

import pandas as pd

from solution import sort_by_size


def shirts():
    return pd.DataFrame({
        "product_id": ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"],
        "size": ["M", "XL", "S", "xl", "L", None, "M", "S", "XXL"],
        "list_price": [499.0, 599.0, 449.0, 599.0, 549.0, 499.0, 499.0, 449.0, 649.0],
    })


def test_dtype_is_ordered_categorical():
    out, _ = sort_by_size(shirts())
    dt = out["size"].dtype
    assert isinstance(dt, pd.CategoricalDtype), "size must become a categorical column (CategoricalDtype), not text"
    assert dt.ordered, "the categorical must be ORDERED (ordered=True) so that S < M < L < XL"
    assert dt.categories.tolist() == ["S", "M", "L", "XL"], "categories in size order S, M, L, XL; got %s" % dt.categories.tolist()


def test_sorted_by_real_size_stable():
    out, _ = sort_by_size(shirts())
    assert out["product_id"].tolist() == ["P3", "P8", "P1", "P7", "P5", "P2", "P4", "P6", "P9"], (
        "S (P3, P8), M (P1, P7), L (P5), XL (P2), then invalid/missing in original order (P4, P6, P9); got %s"
        % out["product_id"].tolist())
    assert out.index.tolist() == list(range(9)), "fresh index"


def test_invalid_values_become_missing():
    out, _ = sort_by_size(shirts())
    tail = out["size"].tolist()[-3:]
    assert all(isinstance(v, float) and math.isnan(v) for v in tail), (
        "'xl' (lower case), None and 'XXL' are not valid sizes: they must be missing and sorted last; got %s" % tail)


def test_unknown_count():
    _, n = sort_by_size(shirts())
    assert n == 2, "two sizes were present but invalid ('xl' and 'XXL'); the missing size of P6 does not count (got %s)" % n


def test_no_conversion_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sort_by_size(shirts())
    bad = [str(w.message) for w in caught if "categories" in str(w.message)]
    assert not bad, ("pandas warned: %s. Make invalid sizes missing BEFORE converting (where + isin), "
                     "a future pandas will raise here" % bad[0][:120])


def test_other_columns_follow():
    out, _ = sort_by_size(shirts())
    assert dict(zip(out["product_id"], out["list_price"])) == dict(zip(shirts()["product_id"], shirts()["list_price"])), (
        "each row must keep its own price after sorting")


def test_input_unchanged():
    df = shirts()
    before = df.copy()
    sort_by_size(df)
    pd.testing.assert_frame_equal(df, before, obj="df")
