import pandas as pd

from solution import candidate_keys


def lines():
    # one row per line item; the numbers are chosen so that exactly three pairs are unique
    return pd.DataFrame({
        "job_id":  [1, 1, 2, 2, 3],
        "line_no": [1, 2, 1, 2, 1],
        "item":    ["labour", "parts", "labour", "parts", "labour"],
        "amount":  [500, 300, 700, 300, 500],
    })


def test_finds_the_three_pairs():
    got = candidate_keys(lines())
    want = [("job_id", "line_no"), ("job_id", "item"), ("job_id", "amount")]
    assert got == want, ("expected the unique pairs in column order %s, got %s. Try every pair of columns and "
                         "keep those with no repeated pair of values." % (want, got))


def test_single_column_key_hides_its_supersets():
    df = pd.DataFrame({"payment_id": [9, 8, 7, 6], "job_id": [1, 1, 2, 2],
                       "kind": ["deposit", "balance", "deposit", "balance"]})
    got = candidate_keys(df)
    assert ("payment_id",) in got, "payment_id alone is unique, so ('payment_id',) must be listed."
    assert not any(len(k) == 2 and "payment_id" in k for k in got), (
        "('payment_id', 'job_id') contains a smaller key, so it is not minimal and must not be listed. Got %s." % got)
    assert ("job_id", "kind") in got, "job_id and kind together are unique and contain no smaller key, so list the pair."


def test_max_cols_limits_the_search():
    assert candidate_keys(lines(), max_cols=1) == [], "no single column of the line table is unique, so max_cols=1 finds nothing."
    three = candidate_keys(pd.DataFrame({"a": [1, 1, 1, 2], "b": [1, 1, 2, 2], "c": [1, 2, 1, 1]}), max_cols=3)
    assert three == [("a", "b", "c")], "only the three columns together are unique here, got %s. Allow sizes up to max_cols." % three


def test_missing_values_disqualify_a_column_set():
    df = pd.DataFrame({"a": [1, 2, None], "b": [1, 1, 2]})
    got = candidate_keys(df)
    assert ("a",) not in got, "column a is distinct but has a missing value; a missing key is no identity, so it is not a key."
    assert got == [], "a pair that contains a missing cell cannot be a key either, and b alone repeats. Got %s." % got


def test_nothing_unique_returns_empty_list():
    df = pd.DataFrame({"a": [1, 1], "b": [2, 2]})
    assert candidate_keys(df) == [], "two identical rows have no key; return an empty list."


def test_frame_is_not_changed():
    df = lines()
    before = df.copy()
    candidate_keys(df)
    pd.testing.assert_frame_equal(df, before)
