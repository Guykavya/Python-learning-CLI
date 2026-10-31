import pytest

from solution import to_text


def test_simple_types():
    assert to_text(42) == "42", "Register int: str(value)."
    assert to_text(-7) == "-7"
    assert to_text(3.5) == "3.50", "Floats always get two decimals: f'{value:.2f}'."
    assert to_text("hi") == '"hi"', "Strings are wrapped in double quotes."
    assert to_text(None) == "null", "Register type(None) to handle None."


def test_bool_is_not_int():
    assert to_text(True) == "yes", "bool is a subclass of int. Register bool separately, or True becomes 'True'."
    assert to_text(False) == "no"
    assert to_text.dispatch(bool) is not to_text.dispatch(int), "bool needs its own registered function."


def test_list_recursive():
    assert to_text([1, "a"]) == '[1, "a"]', "Convert each item with to_text and join with ', '."
    assert to_text([]) == "[]", "An empty list is []."
    assert to_text([[1], [True]]) == "[[1], [yes]]", "Nested lists: call to_text on the items, which may be lists."


def test_tuple():
    assert to_text((1, 2)) == "(1, 2)", "A tuple uses round brackets."
    assert to_text((7,)) == "(7,)", "A one-item tuple keeps its comma, like Python writes it."
    assert to_text(()) == "()", "An empty tuple is ()."


def test_list_and_tuple_differ():
    assert to_text([1]) == "[1]" and to_text((1,)) == "(1,)", "list and tuple need two separate registrations."


def test_dict():
    assert to_text({"a": 1}) == '{"a": 1}', "A dict shows key: value with both converted."
    assert to_text({"ok": True, "n": [1, 2]}) == '{"ok": yes, "n": [1, 2]}', "Values are converted with to_text too."
    assert to_text({}) == "{}"
    assert to_text({1: None}) == "{1: null}", "Keys are converted with to_text as well."


def test_mixed():
    assert to_text([1, "a", None, (2.5,)]) == '[1, "a", null, (2.50,)]'


def test_unknown_type():
    with pytest.raises(TypeError) as info:
        to_text({1, 2})
    assert "cannot convert set" in str(info.value), "The fallback function raises TypeError('cannot convert <type name>')."
    with pytest.raises(TypeError):
        to_text([1, {2}])
