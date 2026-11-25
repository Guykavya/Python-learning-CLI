import pandas as pd

from solution import as_category


def frame(n=2000):
    cities = ["Pune", "Agra", "Delhi", "Surat", "Jaipur"]
    return pd.DataFrame({
        "city": [cities[i % 5] for i in range(n)],
        "name": ["customer-%05d" % i for i in range(n)],
        "status": ["paid" if i % 3 else None for i in range(n)],
        "qty": list(range(n)),
        "price": [i / 4 for i in range(n)],
    })


def kinds(df):
    return {c: str(t) for c, t in df.dtypes.items()}


def test_low_cardinality_text_becomes_category():
    out = as_category(frame(), max_unique=50)
    k = kinds(out)
    assert k["city"] == "category", "city has 5 distinct values (<= 50): make it a category; got %s." % k["city"]
    assert k["status"] == "category", "status has 1 distinct value plus gaps: missing values do not count, so it is a category."


def test_high_cardinality_and_numbers_untouched():
    out = as_category(frame(), max_unique=50)
    k = kinds(out)
    assert k["name"] != "category", "name has 2000 distinct values: a category would not save memory, leave it."
    assert k["qty"] == "int64" and k["price"] == "float64", "numeric columns must keep their dtype, got %s / %s." % (k["qty"], k["price"])


def test_values_are_equal_including_missing():
    df = frame()
    out = as_category(df, max_unique=50)
    for col in df.columns:
        a, b = df[col], out[col]
        assert a.isna().tolist() == b.isna().tolist(), "column %s: the missing values moved." % col
        assert a.dropna().tolist() == b.dropna().tolist(), "column %s: values changed." % col


def test_max_unique_is_inclusive_and_changes_the_decision():
    df = frame()
    assert kinds(as_category(df, max_unique=5))["city"] == "category", "exactly max_unique distinct values still converts (<=)."
    assert kinds(as_category(df, max_unique=4))["city"] != "category", "5 distinct values are more than max_unique=4."
    assert kinds(as_category(df, max_unique=5000))["name"] == "category", "with a large limit name converts too."


def test_memory_is_smaller():
    df = frame()
    out = as_category(df, max_unique=50)
    before = df.memory_usage(deep=True)
    after = out.memory_usage(deep=True)
    assert after["city"] < before["city"], "the city column should take less memory as a category (deep=True)."
    assert after.sum() < before.sum(), "the whole table should use less memory."


def test_input_not_changed():
    df = frame()
    before = df.copy()
    as_category(df, max_unique=50)
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
    assert kinds(df)["city"] != "category"
