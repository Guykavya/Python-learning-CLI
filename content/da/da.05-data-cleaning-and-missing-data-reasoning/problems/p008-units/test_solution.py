import math

import pytest

from solution import to_kg


def close(got, want):
    assert len(got) == len(want), "return one value per input value: expected %d, got %d." % (len(want), len(got))
    for g, w in zip(got, want):
        assert math.isclose(g, w, rel_tol=1e-9, abs_tol=1e-12), "expected %s, got %s." % (want, got)


def test_each_unit():
    close(to_kg([500, 2, 10], ["g", "kg", "lb"]), [0.5, 2.0, 4.5359237])


def test_grams_use_a_factor_of_one_thousandth():
    close(to_kg([1000, 250], ["g", "g"]), [1.0, 0.25])


def test_case_and_spaces_are_ignored():
    close(to_kg([1, 1, 1, 1], [" KG ", "Kg", "LB", "  g"]), [1.0, 1.0, 0.45359237, 0.001])


def test_result_is_a_list_of_floats():
    out = to_kg([3], ["kg"])
    assert isinstance(out, list) and isinstance(out[0], float), "return a list of floats. Got %r." % (out,)


def test_missing_value_stays_missing():
    out = to_kg([None, float("nan"), 2], ["kg", "g", "kg"])
    assert math.isnan(out[0]) and math.isnan(out[1]), "a missing value stays nan (never 0). Got %s." % out
    assert out[2] == 2.0


def test_unknown_unit_raises_value_error_naming_it():
    with pytest.raises(ValueError) as info:
        to_kg([1, 2], ["kg", "stone"])
    assert "stone" in str(info.value), "the message must contain the unit text 'stone'. Got %r." % str(info.value)


def test_unknown_unit_is_reported_stripped_as_written():
    with pytest.raises(ValueError) as info:
        to_kg([1], ["  Stone "])
    assert "Stone" in str(info.value), "name the unit as written (case kept, spaces stripped). Got %r." % str(info.value)


def test_unknown_unit_raises_even_for_a_missing_value():
    with pytest.raises(ValueError):
        to_kg([None], ["oz"])


def test_empty_input():
    assert to_kg([], []) == [], "no values, no output."
