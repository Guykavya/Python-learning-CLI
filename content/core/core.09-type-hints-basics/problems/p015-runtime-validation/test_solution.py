from typing import get_type_hints

import pytest

from solution import require_str_list, set_age


def test_hints():
    assert get_type_hints(set_age) == {"age": int, "return": int}, "set_age(age: int) -> int."
    assert get_type_hints(require_str_list) == {"values": object, "return": list[str]}, (
        "require_str_list takes anything (object) and returns list[str]."
    )


def test_valid_ages():
    assert set_age(21) == 21, "A normal age is returned unchanged."
    assert set_age(0) == 0 and set_age(150) == 150, "0 and 150 are both allowed."


def test_wrong_type_age():
    with pytest.raises(TypeError, match="int"):
        set_age("21")
    with pytest.raises(TypeError, match="int"):
        set_age(21.5)


def test_bool_is_not_an_age():
    with pytest.raises(TypeError, match="int"):
        set_age(True)


def test_age_out_of_range():
    with pytest.raises(ValueError, match="between"):
        set_age(-1)
    with pytest.raises(ValueError, match="between"):
        set_age(151)


def test_string_age_gives_type_error_not_compare_error():
    with pytest.raises(TypeError, match="age must be an int"):
        set_age("-5")


def test_require_str_list_ok():
    assert require_str_list(["a", "b"]) == ["a", "b"], "A list of strings is returned as it is."
    assert require_str_list([]) == [], "The empty list is a valid list of strings."


def test_require_str_list_not_a_list():
    with pytest.raises(TypeError, match="list"):
        require_str_list(("a", "b"))
    with pytest.raises(TypeError, match="list"):
        require_str_list("ab")


def test_require_str_list_bad_item():
    with pytest.raises(TypeError, match="str"):
        require_str_list(["a", 1])
