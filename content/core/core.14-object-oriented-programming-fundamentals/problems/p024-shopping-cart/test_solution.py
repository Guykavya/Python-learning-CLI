import pytest

from solution import Cart


def test_new_cart_is_empty():
    cart = Cart()
    assert cart.items() == [], "A new cart has no products: items() should be []."
    assert cart.count() == 0, "A new cart has 0 pieces."
    assert cart.total() == 0, "The total of an empty cart is 0."


def test_add_and_items_order():
    cart = Cart()
    cart.add("pen", 10)
    cart.add("notebook", 45.5, 2)
    assert cart.items() == [("pen", 10, 1), ("notebook", 45.5, 2)], (
        "items() gives (name, price, qty) tuples in the order products were first added. qty defaults to 1."
    )


def test_add_same_product_again_adds_pieces():
    cart = Cart()
    cart.add("pen", 10)
    cart.add("notebook", 45.5, 2)
    cart.add("pen", 10, 3)
    assert cart.items() == [("pen", 10, 4), ("notebook", 45.5, 2)], (
        "Adding a product that is already in the cart adds to its qty (1 + 3 = 4) and keeps its first place."
    )


def test_count_is_pieces_not_products():
    cart = Cart()
    cart.add("pen", 10, 4)
    cart.add("notebook", 45.5, 2)
    assert cart.count() == 6, "count() is the number of pieces (4 + 2), not the number of different products (2)."


def test_total():
    cart = Cart()
    cart.add("pen", 10, 4)
    cart.add("notebook", 45.5, 2)
    assert cart.total() == 131.0, "total() is the sum of price * qty: 10*4 + 45.5*2 = 131.0."
    cart2 = Cart()
    cart2.add("a", 0.1, 3)
    assert cart2.total() == 0.3, "Round the total with round(x, 2): 0.1 * 3 is 0.30000000000000004 without it."


def test_remove_some_and_all():
    cart = Cart()
    cart.add("pen", 10, 4)
    cart.add("notebook", 45.5, 2)
    cart.remove("notebook")
    assert cart.items() == [("pen", 10, 4), ("notebook", 45.5, 1)], "remove(name) takes out 1 piece by default."
    assert cart.total() == 85.5, "After removing one notebook the total is 40 + 45.5."
    cart.remove("pen", 4)
    assert cart.items() == [("notebook", 45.5, 1)], (
        "When the qty reaches 0 the product must leave the cart completely, not stay with qty 0."
    )
    assert cart.count() == 1, "Only one notebook is left."


def test_remove_unknown_raises_keyerror():
    cart = Cart()
    cart.add("pen", 10)
    with pytest.raises(KeyError):
        cart.remove("ink")
    cart.remove("pen")
    with pytest.raises(KeyError):
        cart.remove("pen")


def test_remove_bad_qty_raises_valueerror():
    cart = Cart()
    cart.add("pen", 10, 2)
    with pytest.raises(ValueError):
        cart.remove("pen", 3)
    with pytest.raises(ValueError):
        cart.remove("pen", 0)
    with pytest.raises(ValueError):
        cart.remove("pen", -1)
    assert cart.items() == [("pen", 10, 2)], "A failed remove must not change the cart."


def test_add_bad_price_raises():
    cart = Cart()
    for bad in (0, -5, "10"):
        with pytest.raises(ValueError):
            cart.add("ink", bad)
    assert cart.items() == [], "A failed add must not put anything in the cart."


def test_add_bad_qty_raises():
    cart = Cart()
    for bad in (0, -2, 1.5, "2"):
        with pytest.raises(ValueError):
            cart.add("ink", 5, bad)
    assert cart.items() == [], "A failed add must not put anything in the cart."


def test_add_with_different_price_raises():
    cart = Cart()
    cart.add("notebook", 45.5, 2)
    with pytest.raises(ValueError):
        cart.add("notebook", 50)
    assert cart.items() == [("notebook", 45.5, 2)], "A price mismatch must not change the qty."


def test_carts_are_separate():
    a = Cart()
    b = Cart()
    a.add("pen", 10)
    assert b.items() == [], (
        "Adding to one cart changed another. Create the storage in __init__ (self.x = {}), "
        "not as a class attribute that every cart shares."
    )
