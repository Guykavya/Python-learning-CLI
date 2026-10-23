from typing import get_type_hints

from solution import by_length, centre, longest, price_of, shout_all, total


def test_total_hints():
    assert get_type_hints(total) == {"numbers": list[int], "return": int}, (
        "total takes a list of ints and returns an int: numbers: list[int], -> int."
    )


def test_longest_hints():
    assert get_type_hints(longest) == {"words": list[str], "return": str}, (
        "longest takes list[str] and returns one str."
    )


def test_price_of_hints():
    assert get_type_hints(price_of) == {"menu": dict[str, float], "item": str, "return": float}, (
        "price_of: menu is dict[str, float] (name to price), item is str, result is float."
    )


def test_shout_all_hints():
    assert get_type_hints(shout_all) == {"words": list[str], "return": list[str]}, (
        "shout_all takes list[str] and returns a new list[str], not a str."
    )


def test_centre_hints():
    assert get_type_hints(centre) == {
        "points": list[tuple[int, int]],
        "return": tuple[float, float],
    }, (
        "centre takes a list of (int, int) pairs: list[tuple[int, int]], "
        "and returns a pair of floats: tuple[float, float]."
    )


def test_by_length_hints():
    assert get_type_hints(by_length) == {"words": list[str], "return": dict[int, list[str]]}, (
        "by_length returns a dict from int (the length) to list[str]: dict[int, list[str]]."
    )


def test_behaviour_unchanged():
    assert total([1, 2, 3]) == 6, "total must still add the numbers."
    assert longest(["a", "ccc", "bb"]) == "ccc", "longest must still return the longest word."
    assert price_of({"tea": 2.5}, "tea") == 2.5, "price_of must still look the price up."
    assert shout_all(["a", "b"]) == ["A", "B"], "shout_all must still upper-case."
    assert centre([(0, 0), (4, 2)]) == (2.0, 1.0), "centre of (0,0) and (4,2) is (2.0, 1.0)."
    assert by_length(["a", "bb", "c"]) == {1: ["a", "c"], 2: ["bb"]}, (
        "by_length groups words by their length."
    )
