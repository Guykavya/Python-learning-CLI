from typing import get_type_hints

import solution


def hints():
    return get_type_hints(solution)


def test_values_unchanged():
    assert solution.count == 0 and solution.price == 9.5 and solution.title == "Report", (
        "Keep the starting values: count = 0, price = 9.5, title = 'Report'."
    )
    assert solution.tags == [] and solution.stock == {}, "tags and stock must still start empty."
    assert solution.origin == (0, 0) and solution.nickname is None, (
        "origin is (0, 0) and nickname starts as None."
    )


def test_simple_hints():
    h = hints()
    assert h.get("count") is int, "count holds whole numbers: count: int = 0."
    assert h.get("price") is float, "price holds decimals: price: float = 9.5."
    assert h.get("title") is str, "title holds text: title: str = 'Report'."


def test_list_hint():
    assert hints().get("tags") == list[str], (
        "tags is a list of strings: list[str]. A bare 'list' does not say what is inside."
    )


def test_dict_hint():
    assert hints().get("stock") == dict[str, int], (
        "stock maps text to whole numbers: dict[str, int]. Separate the two types with a comma."
    )


def test_tuple_hint():
    assert hints().get("origin") == tuple[int, int], (
        "origin is a pair of ints with a fixed shape: tuple[int, int], not tuple[int, ...]."
    )


def test_optional_hint():
    assert hints().get("nickname") == (str | None), (
        "nickname may be None, so the hint is str | None. 'nickname: str = None' is a type error."
    )
