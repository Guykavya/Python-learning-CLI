import pandas as pd

from solution import standardise_city

MAPPING = {"pune": "Pune", "delhi": "Delhi", "dehli": "Delhi", "new delhi": "Delhi",
           "mumbai": "Mumbai", "mumbay": "Mumbai"}


def listed(series):
    return [None if pd.isna(v) else v for v in series.tolist()]


def run(values, mapping=None):
    s = pd.Series(values)
    return standardise_city(s, MAPPING if mapping is None else mapping)


def test_chapter_example():
    clean, unmapped = run([" PUNE ", "pune", "Delhi.", "Dehli", "Mumbay", "New  Delhi", None, "Goa", "goa.", "Lucknow"])
    assert listed(clean) == ["Pune", "Pune", "Delhi", "Delhi", "Mumbai", "Delhi", None, None, None, None], (
        "got %s" % listed(clean))
    assert unmapped == ["goa", "lucknow"], "unmapped = sorted distinct normalised keys not in the mapping. Got %s." % unmapped


def test_spaces_and_case():
    clean, unmapped = run(["  PUNE", "Pune  ", "pUnE", "\tpune\n"])
    assert listed(clean) == ["Pune"] * 4, "strip white space at both ends and ignore case. Got %s." % listed(clean)
    assert unmapped == []


def test_trailing_dots_and_dot_with_space():
    clean, _ = run(["Delhi.", "Delhi..", "Delhi . ", ". Delhi"])
    assert listed(clean)[:3] == ["Delhi"] * 3, (
        "strip, remove trailing dots, strip again: 'Delhi . ' also becomes delhi. Got %s." % listed(clean))
    assert listed(clean)[3] is None, "a dot at the START is not trailing: '. delhi' is not in the mapping."


def test_inner_runs_of_spaces_become_one():
    clean, _ = run(["New   Delhi", "new delhi", "NEW\tDELHI"])
    assert listed(clean) == ["Delhi"] * 3, "collapse any white space inside to a single space. Got %s." % listed(clean)


def test_typos_come_from_the_mapping_not_from_code():
    clean, unmapped = run(["Mumbay", "Dehli", "Mumbayy"])
    assert listed(clean) == ["Mumbai", "Delhi", None], "got %s" % listed(clean)
    assert unmapped == ["mumbayy"], "the key not in the table is reported: %s." % unmapped


def test_missing_stays_missing_and_is_not_unmapped():
    clean, unmapped = run(["Pune", None, float("nan")])
    assert listed(clean) == ["Pune", None, None]
    assert unmapped == [], "a missing input has nothing to map: it must not appear in unmapped. Got %s." % unmapped


def test_unmapped_is_sorted_distinct_keys():
    _, unmapped = run(["Zurich", "agra", "ZURICH ", "Agra.", "Pune"])
    assert unmapped == ["agra", "zurich"], "sorted, distinct, normalised keys. Got %s." % unmapped


def test_everything_covered_gives_empty_list():
    clean, unmapped = run(["pune", "DELHI", "Mumbai."])
    assert unmapped == [] and isinstance(unmapped, list), "when all keys are in the mapping, unmapped == []."
    assert clean.notna().all()


def test_index_is_kept_and_input_unchanged():
    s = pd.Series([" pune", "GOA"], index=[10, 20])
    clean, _ = standardise_city(s, MAPPING)
    assert clean.index.tolist() == [10, 20], "keep the index of the input Series."
    assert s.tolist() == [" pune", "GOA"], "do not change the input."
