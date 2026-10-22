from collections.abc import Callable
from typing import get_type_hints

import solution
from solution import (
    add_stock,
    apply_to_all,
    low_items,
    most_stocked,
    price_total,
    quantity,
    remove_stock,
    split_by_threshold,
)

STOCK = dict[str, int]


def fresh() -> dict[str, int]:
    return {"apple": 5, "pear": 2, "fig": 0}


def test_every_function_is_annotated():
    for name in (
        "add_stock", "remove_stock", "quantity", "low_items",
        "price_total", "most_stocked", "apply_to_all", "split_by_threshold",
    ):
        hints = get_type_hints(getattr(solution, name))
        assert "return" in hints, f"{name} has no return hint. Every function needs '-> ...'."


def test_hints_simple_functions():
    assert get_type_hints(add_stock) == {"stock": STOCK, "item": str, "qty": int, "return": type(None)}, (
        "add_stock returns nothing: -> None. Parameters: stock: dict[str, int], item: str, qty: int."
    )
    assert get_type_hints(remove_stock) == {"stock": STOCK, "item": str, "qty": int, "return": bool}, (
        "remove_stock returns True or False: -> bool."
    )
    assert get_type_hints(quantity) == {"stock": STOCK, "item": str, "return": int}, (
        "quantity returns an int (0 for unknown items, so never None)."
    )


def test_hints_list_and_float_functions():
    assert get_type_hints(low_items) == {"stock": STOCK, "threshold": int, "return": list[str]}, (
        "low_items returns a sorted list of names: -> list[str]."
    )
    assert get_type_hints(price_total) == {
        "stock": STOCK,
        "prices": dict[str, float],
        "return": float,
    }, "price_total: prices is dict[str, float] and the total is a float."


def test_hints_optional_callable_and_tuple():
    assert get_type_hints(most_stocked) == {"stock": STOCK, "return": str | None}, (
        "most_stocked returns None for an empty stock: -> str | None."
    )
    assert get_type_hints(apply_to_all) == {
        "stock": STOCK,
        "func": Callable[[int], int],
        "return": STOCK,
    }, "apply_to_all(stock, func: Callable[[int], int]) -> dict[str, int]."
    assert get_type_hints(split_by_threshold) == {
        "stock": STOCK,
        "threshold": int,
        "return": tuple[list[str], list[str]],
    }, "split_by_threshold returns a fixed pair of lists: tuple[list[str], list[str]]."


def test_behaviour_add_remove_quantity():
    s = fresh()
    add_stock(s, "kiwi", 4)
    add_stock(s, "apple", 1)
    assert s["kiwi"] == 4 and s["apple"] == 6, "add_stock creates or increases an item."
    assert remove_stock(s, "apple", 3) is True and s["apple"] == 3, "Enough stock: remove and return True."
    assert remove_stock(s, "pear", 5) is False and s["pear"] == 2, "Not enough: return False, change nothing."
    assert quantity(s, "nothing") == 0, "Unknown items have quantity 0."


def test_behaviour_queries():
    s = fresh()
    assert low_items(s, 3) == ["fig", "pear"], "Items below 3, sorted by name."
    assert price_total(s, {"apple": 0.5, "pear": 1.0}) == 4.5, "5 * 0.5 + 2 * 1.0 = 4.5; fig has no price."
    assert most_stocked(s) == "apple", "apple has the highest quantity."
    assert most_stocked({}) is None, "Empty stock: None."


def test_behaviour_apply_and_split():
    s = fresh()
    assert apply_to_all(s, lambda q: q * 2) == {"apple": 10, "pear": 4, "fig": 0}, "Apply func to each quantity."
    assert s == fresh(), "apply_to_all must return a new dict and leave the original unchanged."
    assert split_by_threshold(s, 3) == (["fig", "pear"], ["apple"]), "Return (low names, other names), both sorted."
