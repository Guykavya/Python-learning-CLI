from typing import get_type_hints

from solution import first_or_default, first_or_none


def test_hint_first_or_none():
    assert get_type_hints(first_or_none) == {"items": list[int], "return": int | None}, (
        "first_or_none can return an int or None: -> int | None, with items: list[int]."
    )


def test_hint_first_or_default():
    assert get_type_hints(first_or_default) == {
        "items": list[int],
        "default": int,
        "return": int,
    }, "first_or_default never returns None, so its hint is -> int."


def test_first_item():
    assert first_or_none([4, 5]) == 4, "Return items[0] when the list is not empty."


def test_empty_gives_none():
    assert first_or_none([]) is None, "An empty list has no first item: return None."


def test_zero_is_a_valid_item():
    assert first_or_none([0, 5]) == 0, "0 is falsy but it is a real first item. Do not treat it as 'nothing'."
    assert first_or_default([0], 9) == 0, "Compare with 'is None', not with 'if not first'."


def test_default_used_only_when_empty():
    assert first_or_default([], -1) == -1, "An empty list gives the default."
    assert first_or_default([7], -1) == 7, "A non-empty list ignores the default."
