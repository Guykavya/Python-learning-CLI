import pytest

from solution import Direction, Weekday


def test_weekday_is_an_enum_with_seven_members_in_order():
    assert [d.name for d in Weekday] == ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"], "List the members MON ... SUN in this order; iterating an Enum follows the definition order."
    assert len(Weekday) == 7, "len(Weekday) is the number of members."


def test_auto_values_start_at_one():
    assert [d.value for d in Weekday] == [1, 2, 3, 4, 5, 6, 7], "Use `= auto()` for each member: the values are 1, 2, 3, ... (the default)."
    assert Weekday.MON.value == 1 and Weekday.SUN.value == 7, "MON is 1 and SUN is 7."


def test_lookup_by_value_and_name():
    assert Weekday(3) is Weekday.WED, "Weekday(3) looks a member up by VALUE."
    assert Weekday["FRI"] is Weekday.FRI, "Weekday['FRI'] looks a member up by NAME."
    with pytest.raises(ValueError):
        Weekday(8)
    with pytest.raises(KeyError):
        Weekday["FUNDAY"]


def test_members_are_singletons_with_identity_and_repr():
    assert Weekday.MON is Weekday(1), "There is exactly one object per member, so `is` is right for comparing."
    assert repr(Weekday.TUE) == "<Weekday.TUE: 2>", "Default repr of an enum member: <Weekday.TUE: 2>."
    assert str(Weekday.TUE) == "Weekday.TUE", "Default str of an enum member: Weekday.TUE."


def test_members_do_not_equal_their_values():
    assert Weekday.MON != 1, "A plain Enum member is NOT equal to its value; that is what makes enums safe."


def test_is_weekend_property():
    assert [d.name for d in Weekday if d.is_weekend] == ["SAT", "SUN"], "is_weekend is a @property that is True for SAT and SUN only."
    assert Weekday.MON.is_weekend is False, "is_weekend must be a real bool."


def test_from_name_classmethod():
    assert Weekday.from_name("monday") is Weekday.MON, "from_name accepts full names in any case: look at the first three letters."
    assert Weekday.from_name("  Sat ") is Weekday.SAT, "Surrounding spaces are ignored."
    assert Weekday.from_name("SUN") is Weekday.SUN, "Short names work too."
    with pytest.raises(ValueError):
        Weekday.from_name("xyz")
    with pytest.raises(ValueError):
        Weekday.from_name("")


def test_next_wraps_around():
    assert Weekday.MON.next() is Weekday.TUE, "next() gives the following day."
    assert Weekday.SUN.next() is Weekday.MON, "After SUN comes MON again (wrap around)."


def test_direction_values_are_strings():
    assert Direction("E") is Direction.EAST, "Direction('E') looks up by value."
    assert [d.value for d in Direction] == ["N", "E", "S", "W"], "Values are 'N', 'E', 'S', 'W' in this order."


def test_opposite():
    assert Direction.NORTH.opposite() is Direction.SOUTH and Direction.EAST.opposite() is Direction.WEST, "NORTH <-> SOUTH, EAST <-> WEST."
    for d in Direction:
        assert d.opposite().opposite() is d, "opposite() twice gives the original."


def test_members_are_hashable_and_usable_as_dict_keys():
    counts = {d: 0 for d in Direction}
    counts[Direction.WEST] += 1
    assert counts[Direction.WEST] == 1 and len(counts) == 4, "Enum members can be dict keys."


def test_cannot_change_members():
    with pytest.raises(AttributeError):
        Weekday.MON = 5
