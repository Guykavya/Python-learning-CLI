import dataclasses

import pytest

from solution import Account, Range, Rectangle


# ---------------------------------------------------------------- Account
def test_account_normalises_owner():
    a = Account("  asha rao ")
    assert a.owner == "Asha Rao", "__post_init__ should clean the owner: strip() then title()."


def test_account_history_starts_with_open_entry():
    a = Account("ravi", 50.0)
    assert a.history == [("open", 50.0)], "history is created by default_factory (init=False) and __post_init__ appends ('open', balance)."
    assert Account("x").history == [("open", 0.0)], "Each account has its own history list."


def test_account_history_is_not_an_init_parameter():
    with pytest.raises(TypeError):
        Account("ravi", 1.0, [])
    names = [f.name for f in dataclasses.fields(Account) if f.init]
    assert names == ["owner", "balance"], "history must be field(default_factory=list, init=False): it is not a parameter of __init__."


def test_account_validation():
    for bad_owner in ("", "   ", None, 5):
        with pytest.raises(ValueError):
            Account(bad_owner)
    with pytest.raises(ValueError):
        Account("a", -1)
    assert Account("a", 0).balance == 0, "A balance of exactly 0 is allowed."


def test_account_repr_includes_history():
    assert repr(Account("ab", 1.0)) == "Account(owner='Ab', balance=1.0, history=[('open', 1.0)])", "history is a normal field for repr (only init=False)."


# ---------------------------------------------------------------- Range
def test_range_valid_and_values():
    r = Range(1, 10, 3)
    assert r.values() == [1, 4, 7, 10], "values() returns list(range(low, high + 1, step))."
    assert Range(5, 5).values() == [5], "low == high is valid and has one value."


def test_range_validation_in_post_init():
    with pytest.raises(ValueError):
        Range(5, 1)
    with pytest.raises(ValueError):
        Range(1, 5, 0)
    with pytest.raises(ValueError):
        Range(1, 5, -2)


def test_range_is_frozen_so_post_init_only_checks():
    r = Range(1, 3)
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.low = 0
    assert hash(Range(1, 3)) == hash(r), "Frozen dataclass: hashable and equal values hash equal."


# ---------------------------------------------------------------- Rectangle (InitVar)
def test_rectangle_area_computed_and_not_in_init():
    r = Rectangle(3, 4)
    assert r.area == 12, "area is computed in __post_init__ as width * height."
    with pytest.raises(TypeError):
        Rectangle(3, 4, 1.0, 99)
    assert [f.name for f in dataclasses.fields(Rectangle)] == ["width", "height", "area"], "area is a field; unit_scale is an InitVar, which is NOT a field."


def test_rectangle_initvar_scales_the_sides():
    r = Rectangle(2, 3, unit_scale=10)
    assert (r.width, r.height, r.area) == (20, 30, 600), "unit_scale is passed to __post_init__ as an argument and multiplies both sides before the area is computed."
    assert "unit_scale" not in vars(r), "An InitVar is not stored on the object: do not assign self.unit_scale."


def test_rectangle_repr_hides_the_initvar():
    assert repr(Rectangle(1, 2)) == "Rectangle(width=1.0, height=2.0, area=2.0)", "width *= unit_scale (a float 1.0) makes the sides floats: 1 * 1.0 == 1.0."
