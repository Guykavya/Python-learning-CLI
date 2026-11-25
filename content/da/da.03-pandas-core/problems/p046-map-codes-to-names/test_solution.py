import pandas as pd

from solution import map_regions

MAP = {"N": "North", "S": "South", "E": "East", "W": "West"}


def test_the_example():
    codes = pd.Series(["N", "S", "X", "E", "X", None, "Z"])
    names, unknown = map_regions(codes, {"N": "North", "S": "South", "E": "East"})
    got = [None if pd.isna(v) else v for v in names]
    assert got == ["North", "South", "Other", "East", "Other", None, "Other"], (
        f"unknown codes become 'Other', a missing code stays missing; got {got}.")
    assert unknown == ["X", "Z"], f"unknown should be the sorted distinct unknown codes ['X', 'Z'], got {unknown}."


def test_index_and_input_unchanged():
    s = pd.Series(["W", "Q", "N"], index=[5, 6, 7])
    names, unknown = map_regions(s, MAP)
    assert names.index.tolist() == [5, 6, 7], "keep the index of the input."
    assert names.tolist() == ["West", "Other", "North"], f"got {names.tolist()}."
    assert unknown == ["Q"], f"got {unknown}."
    assert s.tolist() == ["W", "Q", "N"], "do not change the input."
    assert isinstance(unknown, list), f"unknown must be a list, got {type(unknown).__name__}."


def test_all_known_gives_an_empty_list():
    names, unknown = map_regions(pd.Series(["N", "N", "S"]), MAP)
    assert unknown == [] and names.tolist() == ["North", "North", "South"], f"got {names.tolist()} / {unknown}."


def test_missing_values_are_not_unknown_codes():
    names, unknown = map_regions(pd.Series([None, None, "N"]), MAP)
    assert unknown == [], f"a missing code is not an unknown code, do not list it (got {unknown})."
    assert names.isna().tolist() == [True, True, False], "missing codes stay missing, they are not 'Other'."


def test_unknown_codes_are_distinct_and_sorted():
    s = pd.Series(["b", "a", "c", "a", "b", "N", "B"])
    _, unknown = map_regions(s, MAP)
    assert unknown == ["B", "a", "b", "c"], f"distinct and sorted (capital letters first in plain string order); got {unknown}."


def test_large_series_matches_a_plain_loop():
    import random
    rnd = random.Random(46)
    raw = [rnd.choice(["N", "S", "E", "W", "X", "Y", None]) for _ in range(500)]
    names, unknown = map_regions(pd.Series(raw), MAP)
    want = [None if c is None else MAP.get(c, "Other") for c in raw]
    assert [None if pd.isna(v) else v for v in names] == want, "the mapped values differ from the dictionary lookup."
    assert unknown == sorted({c for c in raw if c is not None and c not in MAP}), f"got {unknown}."
