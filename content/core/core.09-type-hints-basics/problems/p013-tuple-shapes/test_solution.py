from typing import get_type_hints

from solution import head_tail, min_max, sorted_unique, split_name


def test_hints():
    assert get_type_hints(min_max) == {"numbers": list[int], "return": tuple[int, int]}, (
        "min_max always returns two ints: the fixed shape tuple[int, int]."
    )
    assert get_type_hints(sorted_unique) == {
        "numbers": tuple[int, ...],
        "return": tuple[int, ...],
    }, "sorted_unique takes and returns a tuple of any length: tuple[int, ...]."
    assert get_type_hints(split_name) == {"full": str, "return": tuple[str, str]}, (
        "split_name returns exactly two strings: tuple[str, str]."
    )
    assert get_type_hints(head_tail) == {
        "numbers": tuple[int, ...],
        "return": tuple[int | None, tuple[int, ...]],
    }, "head_tail returns a fixed pair: (int | None, tuple[int, ...])."


def test_min_max():
    assert min_max([4, 9, 1, 7]) == (1, 9), "Return (smallest, largest) as a tuple."
    assert min_max([5]) == (5, 5), "One item is both the smallest and the largest."


def test_sorted_unique():
    assert sorted_unique((3, 1, 3, 2, 1)) == (1, 2, 3), "Remove duplicates, sort, return a tuple."
    result = sorted_unique((2, 1))
    assert isinstance(result, tuple), "Return a tuple, not a list: wrap sorted(...) in tuple(...)."
    assert sorted_unique(()) == (), "An empty tuple stays empty."


def test_split_name():
    assert split_name("Mary Ann Lee") == ("Mary", "Ann Lee"), "Split at the first space only."
    assert split_name("Asha Rao") == ("Asha", "Rao"), "Two words: first and rest."
    assert split_name("Asha") == ("Asha", ""), "A single word gives (word, '')."
    assert split_name("") == ("", ""), "The empty string gives ('', '')."


def test_head_tail():
    assert head_tail((5, 6, 7)) == (5, (6, 7)), "Return the first item and a tuple of the rest."
    assert head_tail((9,)) == (9, ()), "One item: the rest is the empty tuple."
    assert head_tail(()) == (None, ()), "An empty tuple has no head: return None and ()."
    assert head_tail((0, 1)) == (0, (1,)), "0 is a real head. Check emptiness, not the first item."
