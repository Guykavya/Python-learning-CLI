import json
from typing import NotRequired, TypedDict, get_type_hints

import pytest

import solution
from solution import Address, User, check_value, load_user, validate

GOOD = {"id": 1, "name": "Ada", "address": {"city": "Pune", "zip": "411001"}}


class Point(TypedDict):
    x: float
    y: float


class Opt(TypedDict, total=False):
    a: int
    b: str


class Mixed(TypedDict):
    id: int
    flags: NotRequired[list[bool]]


def with_(**changes):
    d = json.loads(json.dumps(GOOD))
    d.update(changes)
    return d


def test_definitions_kept():
    assert User.__required_keys__ == frozenset({"id", "name", "address"}), "Keep User as given: tags and nickname are NotRequired."
    assert Address.__required_keys__ == frozenset({"city", "zip"}), "Keep Address as given."
    assert get_type_hints(load_user)["return"] is User, "load_user(text: str) -> User."


def test_check_value_basic_types():
    assert check_value(3, int) is True and check_value("a", int) is False, "An int fits int; a str does not."
    assert check_value("a", str) is True and check_value(3, str) is False, "A str fits str."
    assert check_value(True, bool) is True and check_value(1, bool) is False, "Only True/False fit bool."
    assert check_value(True, int) is False, "bool is a subclass of int, but a JSON true is not an id: reject bool for int."
    assert check_value(True, float) is False, "Reject bool for float as well."
    assert check_value(2, float) is True and check_value(2.5, float) is True, "int is accepted where float is wanted."
    assert check_value("2", float) is False, "A str is not a float."


def test_check_value_none_and_unions():
    assert check_value(None, str | None) is True, "None fits str | None."
    assert check_value("a", str | None) is True, "str fits str | None."
    assert check_value(3, str | None) is False, "int fits neither member of str | None."
    assert check_value(None, int) is False, "None does not fit int."
    assert check_value(1, int | str) is True, "Any member of the union may fit."


def test_check_value_lists():
    assert check_value(["a", "b"], list[str]) is True, "Every item fits str."
    assert check_value([], list[str]) is True, "An empty list fits list[str]."
    assert check_value(["a", 1], list[str]) is False, "One bad item makes the whole list wrong: check every item."
    assert check_value("ab", list[str]) is False, "A str is not a list."
    assert check_value([[1], [2, 3]], list[list[int]]) is True, "Lists nest: check recursively."
    assert check_value([[1], ["x"]], list[list[int]]) is False, "Nested items are checked too."
    assert check_value((1, 2), list[int]) is False, "A tuple is not a list."


def test_check_value_nested_typeddict():
    assert check_value({"city": "Pune", "zip": "1"}, Address) is True, "A valid dict fits a nested TypedDict."
    assert check_value({"city": "Pune"}, Address) is False, "A missing key means it does not fit."
    assert check_value([{"x": 1, "y": 2}], list[Point]) is True, "A list of TypedDicts: check each recursively."
    assert check_value([{"x": 1, "y": "2"}], list[Point]) is False, "Nested wrong type is found."


def test_validate_returns_the_same_dict():
    data = with_()
    assert validate(data, User) is data, "Return the very same dict when it is valid."
    assert validate({"x": 1, "y": 2.5}, Point) == {"x": 1, "y": 2.5}, "validate works for any TypedDict."


def test_validate_optional_keys():
    assert validate(with_(tags=["a"], nickname=None), User), "Optional keys may be present (nickname may be None)."
    assert validate(with_(nickname="Ad"), User), "nickname may be a str."
    assert validate({}, Opt) == {}, "total=False: no key is required."
    assert validate({"a": 1}, Opt) == {"a": 1}, "A present optional key is validated."
    assert validate({"id": 1}, Mixed) == {"id": 1}, "NotRequired key may be absent."


def test_validate_not_a_dict():
    for bad in ([], "x", 3, None):
        with pytest.raises(TypeError):
            validate(bad, User)


def test_validate_missing_key_is_value_error_naming_the_key():
    data = with_()
    del data["name"]
    with pytest.raises(ValueError, match="name"):
        validate(data, User)
    with pytest.raises(ValueError, match="x"):
        validate({"y": 1}, Point)


def test_validate_unknown_key():
    with pytest.raises(ValueError, match="colour"):
        validate(with_(colour="red"), User)


def test_validate_wrong_type_is_type_error_naming_the_key():
    with pytest.raises(TypeError, match="id"):
        validate(with_(id="1"), User)
    with pytest.raises(TypeError, match="id"):
        validate(with_(id=True), User)
    with pytest.raises(TypeError, match="tags"):
        validate(with_(tags=["a", 2]), User)
    with pytest.raises(TypeError, match="nickname"):
        validate(with_(nickname=5), User)


def test_validate_nested():
    with pytest.raises(TypeError, match="address"):
        validate(with_(address={"city": "Pune", "zip": 411001}), User)
    with pytest.raises(TypeError, match="address"):
        validate(with_(address={"city": "Pune"}), User)
    with pytest.raises(TypeError, match="address"):
        validate(with_(address="Pune"), User)


def test_load_user():
    assert load_user(json.dumps(GOOD)) == GOOD, "load_user parses the JSON text and returns the validated dict."
    with pytest.raises(TypeError):
        load_user(json.dumps(with_(id="1")))
    with pytest.raises(ValueError):
        load_user('{"name": "Ada"}')
    with pytest.raises(json.JSONDecodeError):
        load_user("{not json")
    with pytest.raises(TypeError):
        load_user("[1, 2]")


def test_uses_the_typeddict_description_not_hardcoded_keys():
    class Other(TypedDict):
        title: str
        pages: int

    assert validate({"title": "T", "pages": 3}, Other) == {"title": "T", "pages": 3}, (
        "validate must read __required_keys__ and get_type_hints(td), so it works for any TypedDict."
    )
    with pytest.raises(TypeError, match="pages"):
        validate({"title": "T", "pages": "3"}, Other)
    assert hasattr(solution, "check_value"), "keep check_value"
