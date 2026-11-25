import pandas as pd

from solution import filter_products


def frame():
    return pd.DataFrame({
        "name": ["Green Tea", "tea bags", None, "Coffee", "TEA cup", "C++ guide", "Tea (x)", "Iced tea"],
        "category": ["food", "food", "food", "food", "home", "books", "food", "food"],
        "price": [120.0, 80.0, 90.0, 200.0, 150.0, 300.0, 200.0, 79.99],
    }, index=[5, 6, 7, 8, 9, 10, 11, 12])


def slow(df, categories, lo, hi, word):
    out = []
    for label, row in zip(df.index, df.itertuples(index=False)):
        if row.category in categories and lo <= row.price <= hi and not pd.isna(row.name) and word.lower() in str(row.name).lower():
            out.append(label)
    return out


def test_example():
    out = filter_products(frame(), ["food"], 80, 200, "tea")
    assert out.index.tolist() == [5, 6, 11], "got %s; expected labels [5, 6, 11]. Both ends of the price range count." % out.index.tolist()


def test_between_includes_both_ends():
    out = filter_products(frame(), ["food"], 80.0, 200.0, "tea")
    assert 6 in out.index.tolist(), "price 80.0 equals lo: between() includes the lower end."
    assert 11 in out.index.tolist(), "price 200.0 equals hi: between() includes the upper end."
    assert 12 not in out.index.tolist(), "79.99 is below the range."


def test_case_insensitive():
    out = filter_products(frame(), ["home"], 0, 1000, "tea")
    assert out.index.tolist() == [9], "'TEA cup' contains 'tea' when case is ignored (case=False)."


def test_missing_name_does_not_match_or_crash():
    out = filter_products(frame(), ["food"], 0, 1000, "")
    assert 7 not in out.index.tolist(), "a missing name must not match, even for an empty word: na=False."


def test_word_is_plain_text():
    df = frame()
    assert filter_products(df, ["books"], 0, 1000, "c++").index.tolist() == [10], "'c++' is a regex error unless you pass regex=False."
    assert filter_products(df, ["food"], 0, 1000, "(x)").index.tolist() == [11], "'(x)' must be searched as plain text (regex=False)."


def test_matches_a_plain_loop():
    df = frame()
    for cats in (["food"], ["food", "home"], ["books"], []):
        for word in ("tea", "COFFEE", "zzz", "a"):
            assert filter_products(df, cats, 80, 250, word).index.tolist() == slow(df, cats, 80, 250, word), (
                "categories=%s word=%r differs from the loop version." % (cats, word))


def test_input_not_changed():
    df = frame()
    before = df.copy()
    filter_products(df, ["food"], 0, 500, "tea")
    pd.testing.assert_frame_equal(df, before, obj="the input frame")
