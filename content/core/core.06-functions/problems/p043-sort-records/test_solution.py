import pytest
from solution import sort_records

PEOPLE = [{"name": "Ravi", "age": 21}, {"name": "Asha"},
          {"name": "Meena", "age": 19}, {"name": "Kiran", "age": 21}]


def names(rs):
    return [r["name"] for r in rs]


def test_ascending():
    assert names(sort_records(PEOPLE, "age")) == ["Meena", "Ravi", "Kiran", "Asha"], (
        "Ascending by age; Ravi before Kiran (equal ages keep their order); Asha has no age, so last.")


def test_descending_missing_still_last():
    assert names(sort_records(PEOPLE, "age", descending=True)) == ["Ravi", "Kiran", "Meena", "Asha"], (
        "Descending, but records without the field still go LAST, and equal ages keep their order.")


def test_by_name():
    assert names(sort_records(PEOPLE, "name")) == ["Asha", "Kiran", "Meena", "Ravi"]


def test_nobody_has_field():
    assert names(sort_records(PEOPLE, "city")) == ["Ravi", "Asha", "Meena", "Kiran"], (
        "No record has 'city': all of them are 'missing', in their original order.")


def test_empty():
    assert sort_records([], "age") == []


def test_input_unchanged():
    people = [dict(p) for p in PEOPLE]
    sort_records(people, "age", descending=True)
    assert people == PEOPLE


def test_descending_keyword_only():
    with pytest.raises(TypeError):
        sort_records(PEOPLE, "age", True)
