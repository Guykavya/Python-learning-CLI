import pandas as pd

from solution import tidy_names


def plain(name):
    """The obvious Python version of the rule."""
    if pd.isna(name):
        return None
    return " ".join(name.split()).title()


def test_the_example():
    names = pd.Series(["  asha   rao ", "BEN kumar", None, "zoë  çelik"])
    got = tidy_names(names)
    assert isinstance(got, pd.Series), f"return a Series, not a {type(got).__name__}."
    assert got.tolist()[:2] == ["Asha Rao", "Ben Kumar"], f"expected ['Asha Rao', 'Ben Kumar'], got {got.tolist()[:2]}."
    assert pd.isna(got.iloc[2]), f"a missing name must stay missing, got {got.iloc[2]!r} (do not turn it into the text 'nan' with astype(str))."
    assert got.iloc[3] == "Zoë Çelik", f"non-ASCII letters must be kept and capitalised: expected 'Zoë Çelik', got {got.iloc[3]!r}."


def test_whitespace_kinds():
    got = tidy_names(pd.Series(["a\tb", "  x  ", "p   q   r", "\nlee\n"]))
    assert got.tolist() == ["A B", "X", "P Q R", "Lee"], (
        f"tabs and newlines count as whitespace too; use the pattern r'\\s+', not just ' '. Got {got.tolist()}.")


def test_compares_with_plain_python_and_keeps_the_index():
    raw = ["  d'souza  priya", "VAN  der  berg", "o  NEIL", None, "", "  "]
    s = pd.Series(raw, index=[10, 11, 12, 13, 14, 15])
    got = tidy_names(s)
    assert got.index.tolist() == [10, 11, 12, 13, 14, 15], "keep the original index; do not reset it or drop rows."
    for i, value in enumerate(raw):
        want = plain(value)
        have = got.iloc[i]
        if want is None:
            assert pd.isna(have), f"row {i}: missing must stay missing, got {have!r}."
        else:
            assert have == want, f"row {i}: {value!r} should become {want!r}, got {have!r}."


def test_cleaning_merges_duplicates_in_a_count():
    s = pd.Series(["Asha", "asha ", " ASHA", "Ben"])
    assert tidy_names(s).nunique() == 2, "after tidying, 'Asha', 'asha ' and ' ASHA' are one name: nunique should be 2."


def test_input_is_not_changed():
    s = pd.Series([" a  b "])
    tidy_names(s)
    assert s.tolist() == [" a  b "], "do not change the input Series."
