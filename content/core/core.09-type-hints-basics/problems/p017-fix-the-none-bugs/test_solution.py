from typing import get_type_hints

from solution import cheapest_item, find_price, price_label, total_cost

MENU = {"tea": 2.5, "cake": 4.0, "water": 0.0}


def test_find_price_untouched():
    assert get_type_hints(find_price) == {
        "menu": dict[str, float],
        "item": str,
        "return": float | None,
    }, "find_price is correct as it is: -> float | None. Do not change it."
    assert find_price(MENU, "soup") is None, "find_price still returns None for an unknown item."


def test_total_cost_normal():
    assert total_cost(MENU, ["tea", "cake"]) == 6.5, "Add the prices of the items ordered."
    assert total_cost(MENU, []) == 0.0, "An empty order costs nothing."


def test_total_cost_skips_unknown_items():
    assert total_cost(MENU, ["tea", "soup", "cake"]) == 6.5, (
        "soup is not on the menu: skip it. Check 'price is None' before adding."
    )


def test_total_cost_free_item_counts_as_zero():
    assert total_cost(MENU, ["water", "tea"]) == 2.5, "water costs 0.0, which is a valid price."


def test_cheapest_hint_says_none_is_possible():
    assert get_type_hints(cheapest_item) == {"menu": dict[str, float], "return": str | None}, (
        "cheapest_item returns None for an empty menu, so the hint must be -> str | None."
    )


def test_cheapest_item():
    assert cheapest_item(MENU) == "water", "water costs 0.0, the lowest price."
    assert cheapest_item({"tea": 2.5, "cake": 4.0}) == "tea", "tea is cheaper than cake."
    assert cheapest_item({"a": 1.0, "b": 1.0}) == "a", "On a tie, return the first item found."


def test_cheapest_item_empty_menu():
    assert cheapest_item({}) is None, "An empty menu has no cheapest item: return None."


def test_price_label():
    assert price_label(MENU, "tea") == "$2.50", "Two decimals: '$2.50'."
    assert price_label(MENU, "cake") == "$4.00", "Two decimals: '$4.00'."


def test_price_label_unknown_and_free():
    assert price_label(MENU, "soup") == "n/a", "An unknown item gives 'n/a', not a crash."
    assert price_label(MENU, "water") == "$0.00", (
        "A price of 0.0 is a real price. Check 'is None', not 'if not price'."
    )


def test_other_hints_unchanged():
    assert get_type_hints(total_cost) == {
        "menu": dict[str, float],
        "order": list[str],
        "return": float,
    }, "total_cost keeps its hints: -> float."
    assert get_type_hints(price_label) == {"menu": dict[str, float], "item": str, "return": str}, (
        "price_label keeps its hints: -> str."
    )
