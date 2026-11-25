import pandas as pd

from solution import split_full_name


def expected(name):
    if pd.isna(name):
        return None, None
    words = name.split(None, 1)
    return words[0], (words[1].strip() if len(words) > 1 else "")


def check(df, what):
    before = df.copy()
    got = split_full_name(df)
    pd.testing.assert_frame_equal(df, before, obj="the input frame (it must not change)")
    assert isinstance(got, pd.DataFrame), f"{what}: return a DataFrame, not a {type(got).__name__}."
    assert got.columns.tolist() == df.columns.tolist() + ["first", "last"], (
        f"{what}: columns should be the old ones plus 'first', 'last' at the end, got {got.columns.tolist()}.")
    assert got.index.tolist() == df.index.tolist(), f"{what}: keep the index."
    for i, name in enumerate(df["name"]):
        f, l = expected(name)
        for col, want in (("first", f), ("last", l)):
            have = got[col].iloc[i]
            if want is None:
                assert pd.isna(have), f"{what}: row {i} ({name!r}): '{col}' should be missing, got {have!r}."
            else:
                assert have == want, f"{what}: row {i} ({name!r}): '{col}' should be {want!r}, got {have!r}."


def test_the_example():
    check(pd.DataFrame({"id": [1, 2, 3, 4], "name": [" Asha   Rao", "Meera Iyer Nair", "Cher", None]}), "example")


def test_every_name_has_a_last_name_and_other_columns_survive():
    df = pd.DataFrame({"name": ["A B", "C D E"], "city": ["Pune", "Agra"], "qty": [1, 2]}, index=[5, 9])
    check(df, "all two-word names")
    got = split_full_name(df)
    assert got["city"].tolist() == ["Pune", "Agra"] and got["qty"].tolist() == [1, 2], "other columns must be kept unchanged."


def test_only_one_word_names_gives_only_one_column_from_split():
    check(pd.DataFrame({"name": ["Cher", "Madonna", "Prince"]}), "only one-word names")
    got = split_full_name(pd.DataFrame({"name": ["Cher", "Madonna"]}))
    assert got["last"].tolist() == ["", ""], (
        f"one-word names have last == '' (empty text); got {got['last'].tolist()}. If the split gives one column only, "
        "reindex(columns=[0, 1]) so column 1 exists.")


def test_all_missing_and_mixed_missing():
    check(pd.DataFrame({"name": [None, None]}), "all missing")
    check(pd.DataFrame({"name": ["Ann Lee", None, "Bo"]}, index=[3, 2, 1]), "mixed with missing, odd index")


def test_many_rows_match_plain_python():
    words = ["Asha", "Ben", "Chitra", "Dev", "Esha", "Farid"]
    names = []
    for i in range(60):
        k = 1 + i % 3
        base = " ".join(words[(i + j) % 6] for j in range(k))
        names.append(None if i % 8 == 0 else ("  " + base + "  " if i % 3 == 0 else base))
    check(pd.DataFrame({"name": names}), "60 generated names")
