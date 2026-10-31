import pytest

import shop

PRICES = {"pen": 150, "book": 1200, "mug": 1000, "lamp": 4000}


@pytest.fixture
def inv():
    inventory = shop.Inventory()
    for sku in PRICES:
        inventory.add_stock(sku, 5)
    return inventory


@pytest.fixture
def cart():
    return shop.Cart(PRICES)


# ---- Inventory ----

def test_stock_adds_up_and_unknown_is_zero(inv):
    inv.add_stock("pen", 3)
    assert inv.stock("pen") == 8, "add_stock adds to what is already there."
    assert inv.stock("never-added") == 0, "An item that was never added has stock 0 (no KeyError)."


@pytest.mark.parametrize("qty", [0, -1])
def test_add_stock_needs_a_positive_quantity(inv, qty):
    with pytest.raises(ValueError):
        inv.add_stock("pen", qty)


def test_remove_stock(inv):
    inv.remove_stock("pen", 2)
    assert inv.stock("pen") == 3, "remove_stock subtracts."


def test_can_remove_exactly_all_stock(inv):
    inv.remove_stock("pen", 5)
    assert inv.stock("pen") == 0, "Removing exactly what is there is allowed."


def test_cannot_remove_more_than_stock(inv):
    with pytest.raises(shop.OutOfStock):
        inv.remove_stock("pen", 6)
    assert inv.stock("pen") == 5, "A failed removal must leave the stock unchanged."


# ---- Cart ----

def test_cart_merges_same_item_and_sums(cart):
    cart.add("pen")
    cart.add("pen", 2)
    cart.add("book")
    assert cart.items == {"pen": 3, "book": 1}, "Adding the same item twice adds the quantities."
    assert cart.subtotal() == 3 * 150 + 1200, "subtotal is price times quantity, summed."


@pytest.mark.parametrize("qty", [0, -2])
def test_cart_add_needs_a_positive_quantity(cart, qty):
    with pytest.raises(ValueError):
        cart.add("pen", qty)


def test_cart_add_unknown_item(cart):
    with pytest.raises(KeyError):
        cart.add("sofa")


def test_cart_remove(cart):
    cart.add("pen")
    cart.remove("pen")
    assert cart.items == {}, "remove takes the item out."
    with pytest.raises(KeyError):
        cart.remove("pen")


# ---- discount_cents ----

@pytest.mark.parametrize("subtotal, code, expected", [
    (4999, "SAVE10", 0), (5000, "SAVE10", 500), (5019, "SAVE10", 501), (10000, "SAVE10", 1000),
    (999, "FIVER", 0), (1000, "FIVER", 500), (1500, "FIVER", 500),
    (9999, None, 0),
])
def test_discount_cents(subtotal, code, expected):
    assert shop.discount_cents(subtotal, code) == expected, (
        f"discount_cents({subtotal}, {code!r}) should be {expected}: SAVE10 is 10% (rounded down) from 5000, "
        "FIVER is 500 from 1000.")


def test_unknown_discount_code():
    with pytest.raises(ValueError):
        shop.discount_cents(5000, "FREEMONEY")


# ---- shipping and tax ----

@pytest.mark.parametrize("amount, expected", [(0, 0), (1, 499), (4999, 499), (5000, 0), (7000, 0)])
def test_shipping_cents(amount, expected):
    assert shop.shipping_cents(amount) == expected, (
        "Shipping is 499, free from 5000, and 0 for an empty order.")


@pytest.mark.parametrize("amount, expected", [(0, 0), (1000, 80), (1006, 80), (1007, 81)])
def test_tax_cents(amount, expected):
    assert shop.tax_cents(amount) == expected, "Tax is 8% rounded half up (1007 * 8% = 80.56 gives 81)."


# ---- checkout ----

def test_checkout_receipt_small_order(inv, cart):
    cart.add("pen", 2)
    receipt = shop.checkout(cart, inv)
    assert receipt == {"subtotal": 300, "discount": 0, "shipping": 499, "tax": 24, "total": 823}, (
        "Tax is only on the goods (300 * 8% = 24), shipping is added after.")


def test_checkout_free_shipping_at_exactly_5000(inv, cart):
    cart.add("lamp")
    cart.add("mug")
    receipt = shop.checkout(cart, inv)
    assert receipt == {"subtotal": 5000, "discount": 0, "shipping": 0, "tax": 400, "total": 5400}, (
        "An order of exactly 5000 ships free.")


def test_checkout_save10_at_exactly_5000(inv, cart):
    cart.add("lamp")
    cart.add("mug")
    receipt = shop.checkout(cart, inv, "SAVE10")
    assert receipt == {"subtotal": 5000, "discount": 500, "shipping": 499, "tax": 360, "total": 5359}, (
        "SAVE10 applies at exactly 5000, and the order after the discount (4500) pays shipping.")


def test_checkout_shipping_is_decided_after_the_discount(inv, cart):
    cart.add("lamp")
    cart.add("book")
    cart.add("pen", 2)
    receipt = shop.checkout(cart, inv, "SAVE10")
    assert receipt == {"subtotal": 5500, "discount": 550, "shipping": 499, "tax": 396, "total": 5845}, (
        "5500 - 550 = 4950 is below 5000, so shipping is charged.")


def test_checkout_fiver_at_exactly_1000(inv, cart):
    cart.add("mug")
    receipt = shop.checkout(cart, inv, "FIVER")
    assert receipt == {"subtotal": 1000, "discount": 500, "shipping": 499, "tax": 40, "total": 1039}, (
        "FIVER applies at exactly 1000.")


def test_checkout_takes_stock_and_empties_the_cart(inv, cart):
    cart.add("pen", 2)
    cart.add("mug")
    shop.checkout(cart, inv)
    assert inv.stock("pen") == 3 and inv.stock("mug") == 4, "checkout removes the bought quantities."
    assert cart.items == {}, "The cart is empty after checkout."


def test_checkout_can_buy_all_remaining_stock(inv, cart):
    cart.add("pen", 5)
    shop.checkout(cart, inv)
    assert inv.stock("pen") == 0, "Buying exactly all the stock is allowed."


def test_checkout_out_of_stock_changes_nothing(inv, cart):
    cart.add("pen")
    cart.add("book", 6)
    with pytest.raises(shop.OutOfStock):
        shop.checkout(cart, inv)
    assert inv.stock("pen") == 5 and inv.stock("book") == 5, "All or nothing: no stock may be taken."
    assert cart.items == {"pen": 1, "book": 6}, "The cart is unchanged after a failed checkout."


def test_checkout_unknown_code_changes_nothing(inv, cart):
    cart.add("pen")
    with pytest.raises(ValueError):
        shop.checkout(cart, inv, "NOPE")
    assert inv.stock("pen") == 5, "A bad code must not take stock."


def test_checkout_empty_cart(inv, cart):
    with pytest.raises(ValueError):
        shop.checkout(cart, inv)
