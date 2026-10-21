import pytest
from solution import rank_students

RECORDS = [("ravi", 75), ("Asha", 82), ("meena", 91), ("Kiran", 75)]


def test_full_ranking():
    assert rank_students(RECORDS) == ["meena", "Asha", "Kiran", "ravi"], (
        "Highest marks first; Kiran and ravi tie on 75, so alphabetical ignoring case: Kiran, ravi.")


def test_ties_not_reversed():
    recs = [("b", 50), ("a", 50), ("c", 50)]
    assert rank_students(recs) == ["a", "b", "c"], (
        "Ties must be A-to-Z. reverse=True would reverse the names as well; negate the marks instead.")


def test_top():
    assert rank_students(RECORDS, top=2) == ["meena", "Asha"]
    assert rank_students(RECORDS, top=10) == ["meena", "Asha", "Kiran", "ravi"]
    assert rank_students(RECORDS, top=0) == [], "top=0 means no names. Test `top is None`, not `if top`."


def test_empty():
    assert rank_students([]) == []


def test_top_keyword_only():
    with pytest.raises(TypeError):
        rank_students(RECORDS, 2)


def test_input_unchanged():
    recs = list(RECORDS)
    rank_students(recs)
    assert recs == RECORDS
