import inspect
import typing
from collections.abc import Callable, Iterable, Sequence
from typing import Self, get_args, get_origin, get_type_hints

import pytest

import solution
from solution import (
    Order,
    apply_discount,
    filter_orders,
    find_order,
    format_price,
    parse_price,
    summarise,
    top_customer,
    totals_by_customer,
)

ITEMS = list[tuple[str, int, int]]


def contains_any(t):
    if t is typing.Any:
        return True
    if isinstance(t, (list, tuple)):
        return any(contains_any(x) for x in t)
    return any(contains_any(a) for a in get_args(t))


def one_of(hint, *options):
    return any(hint == o for o in options)


def orders_hint(hint):
    return one_of(hint, list[Order], Sequence[Order], Iterable[Order])


class Hints(dict):
    def __missing__(self, key):
        raise AssertionError(f"There is no hint for '{key}'. Annotate every parameter and the return.")


def hints(func):
    return Hints(get_type_hints(func))


def make():
    a = Order(1, "Asha").add("pen", 150, 2).add("book", 999)
    b = Order(2, "Ben").add("gum", 50, 3)
    c = Order(3, "Asha").add("bag", 2500)
    return [a, b, c]


# ------------------------------------------------------------------ hints
def test_every_public_function_and_method_is_fully_annotated():
    targets = [parse_price, format_price, find_order, totals_by_customer, apply_discount, top_customer, summarise, filter_orders]
    targets += [getattr(Order, n) for n in ("__init__", "add", "total", "is_empty")]
    for f in targets:
        sig = inspect.signature(f)
        for name, p in sig.parameters.items():
            if name == "self":
                continue
            assert p.annotation is not inspect.Parameter.empty, (
                f"{f.__qualname__}: parameter '{name}' has no annotation. Every parameter needs a hint."
            )
        assert sig.return_annotation is not inspect.Signature.empty, (
            f"{f.__qualname__} has no return annotation. Add '-> ...' (even '-> None' for __init__)."
        )


def test_no_any_in_hints():
    funcs = [parse_price, format_price, find_order, totals_by_customer, apply_discount, top_customer, summarise, filter_orders]
    funcs += [getattr(Order, n) for n in ("__init__", "add", "total", "is_empty")]
    for f in funcs:
        for name, h in hints(f).items():
            assert not contains_any(h), f"{f.__qualname__}: '{name}' uses Any. Say what the type really is."


def test_parse_price_hints():
    assert hints(parse_price) == {"text": str, "return": int | None}, (
        "parse_price(text: str) -> int | None. It returns None for text that is not a number."
    )


def test_format_price_hints():
    assert hints(format_price) == {"cents": int, "symbol": str, "return": str}, (
        "format_price(cents: int, symbol: str = '$') -> str."
    )


def test_order_init_hints():
    h = hints(Order.__init__)
    assert h["order_id"] is int and h["customer"] is str, "order_id: int, customer: str."
    assert h["return"] is type(None), "__init__ returns nothing: -> None."
    assert one_of(h["items"], ITEMS | None, Sequence[tuple[str, int, int]] | None, Iterable[tuple[str, int, int]] | None), (
        "items is a list of (name, cents, qty) tuples, or None by default: list[tuple[str, int, int]] | None = None."
    )
    assert inspect.signature(Order.__init__).parameters["items"].default is None, "Keep the default items=None."


def test_order_method_hints():
    add = hints(Order.add)
    assert (add["name"], add["cents"], add["qty"]) == (str, int, int), "add(name: str, cents: int, qty: int = 1)."
    assert one_of(add["return"], Order, Self), "add returns self, so its type is Order (or Self)."
    assert inspect.signature(Order.add).parameters["qty"].default == 1, "Keep the default qty=1."
    assert hints(Order.total)["return"] is int, "total() -> int."
    assert hints(Order.is_empty)["return"] is bool, "is_empty() -> bool."


def test_find_order_hint_admits_none():
    h = hints(find_order)
    assert orders_hint(h["orders"]) and h["order_id"] is int, "find_order(orders: list[Order], order_id: int)."
    assert h["return"] == Order | None, (
        "find_order falls off the end of the function (returning None) when nothing matches: -> Order | None."
    )


def test_collection_functions_hints():
    assert orders_hint(hints(totals_by_customer)["orders"]) and hints(totals_by_customer)["return"] == dict[str, int], (
        "totals_by_customer(orders: list[Order]) -> dict[str, int]."
    )
    h = hints(top_customer)
    assert orders_hint(h["orders"]) and h["return"] == tuple[str, int] | None, (
        "top_customer returns (name, total) or None for no orders: -> tuple[str, int] | None."
    )
    h = hints(summarise)
    assert orders_hint(h["orders"]) and h["symbol"] is str and h["return"] == list[str], (
        "summarise(orders: list[Order], symbol: str = '$') -> list[str]."
    )
    assert hints(apply_discount) == {"cents": int, "percent": int, "return": int}, "apply_discount(cents: int, percent: int) -> int."


def test_filter_orders_hints():
    h = hints(filter_orders)
    assert orders_hint(h["orders"]), "orders: list[Order]."
    assert h["predicate"] == Callable[[Order], bool], "predicate is a function from Order to bool: Callable[[Order], bool]."
    assert h["return"] == list[Order], "filter_orders returns a new list[Order]."


# ------------------------------------------------------------------ behaviour (must not change)
@pytest.mark.parametrize("text, expected", [
    ("$12.50", 1250), (" 12.5 ", 1250), ("3", 300), ("$0.99", 99), ("abc", None), ("", None), ("$", None),
])
def test_parse_price(text, expected):
    assert parse_price(text) == expected, f"parse_price({text!r}) should be {expected!r}: behaviour must not change."


@pytest.mark.parametrize("cents, symbol, expected", [
    (1250, "$", "$12.50"), (5, "$", "$0.05"), (0, "$", "$0.00"), (-250, "$", "-$2.50"), (1999, "EUR ", "EUR 19.99"),
])
def test_format_price(cents, symbol, expected):
    assert format_price(cents, symbol) == expected, f"format_price({cents}, {symbol!r}) should be {expected!r}."


def test_format_price_default_symbol():
    assert format_price(100) == "$1.00", "The default symbol is '$'."


def test_order_basics():
    o = Order(9, "Zed")
    assert o.is_empty() is True and o.total() == 0, "A new order is empty with total 0."
    assert o.add("pen", 150, 2) is o, "add returns the same order (so calls can be chained)."
    assert o.add("book", 999).total() == 1299, "total is the sum of cents * qty: 300 + 999."
    assert o.is_empty() is False, "An order with items is not empty."
    assert o.items == [("pen", 150, 2), ("book", 999, 1)], "Items are stored as (name, cents, qty) tuples; qty defaults to 1."


def test_order_init_copies_items():
    src = [("a", 1, 1)]
    o = Order(1, "x", src)
    o.add("b", 2)
    assert src == [("a", 1, 1)], "The constructor copies the list; do not change that behaviour."
    assert o.total() == 3, "Initial items count in the total."
    assert Order(1, "x", []).items == [], "An empty list gives an empty order."


def test_default_items_not_shared():
    assert Order(1, "a").add("x", 1).items != Order(2, "b").items, "Each order has its own item list."


def test_find_order():
    orders = make()
    assert find_order(orders, 2) is orders[1], "find_order returns the order with that id."
    assert find_order(orders, 99) is None, "Not found: None."
    assert find_order([], 1) is None, "No orders: None."


def test_totals_and_top_customer():
    orders = make()
    assert totals_by_customer(orders) == {"Asha": 300 + 999 + 2500, "Ben": 150}, "Totals are added up per customer."
    assert top_customer(orders) == ("Asha", 3799), "The customer with the highest total, with the total."
    assert top_customer([]) is None, "No orders: None."
    assert totals_by_customer([]) == {}, "No orders: empty dict."


def test_apply_discount():
    assert apply_discount(1000, 10) == 900, "10% off 1000 is 900."
    assert apply_discount(999, 10) == 900, "Integer arithmetic: 999 - 999 * 10 // 100 = 900."
    assert apply_discount(500, 0) == 500, "0% changes nothing."
    assert apply_discount(500, 100) == 0, "100% off is 0."


def test_summarise_and_filter():
    orders = make()
    assert summarise(orders) == ["#1 Asha: $12.99", "#2 Ben: $1.50", "#3 Asha: $25.00"], (
        "summarise gives one line per order: '#id customer: price'."
    )
    assert summarise(orders[:1], "EUR ") == ["#1 Asha: EUR 12.99"], "The symbol is passed to format_price."
    big = filter_orders(orders, lambda o: o.total() > 1000)
    assert [o.order_id for o in big] == [1, 3], "filter_orders keeps the orders for which predicate(order) is true."
    assert big is not orders, "filter_orders returns a new list."
