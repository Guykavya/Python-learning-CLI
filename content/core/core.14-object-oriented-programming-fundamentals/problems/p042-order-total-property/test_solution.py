import pytest

from solution import Order


def sample():
    o = Order("Asha")
    o.add_line("pen", 10, 5)
    o.add_line("book", 150)
    return o


def test_class_settings():
    assert (Order.TAX_RATE, Order.SHIPPING, Order.FREE_SHIPPING_FROM) == (0.05, 40, 500), "Keep the class attributes as given."
    assert Order.COUPONS == {"WELCOME10": 10, "FEST25": 25, "HALF": 50}, "Keep the COUPONS class attribute as given."


def test_new_order():
    o = Order("Asha")
    assert o.customer == "Asha" and o.placed is False and o.discount_percent == 0, "Start open, with 0 percent discount."
    assert (o.subtotal, o.discount, o.tax, o.shipping, o.total) == (0, 0, 0, 0, 0), "An empty order costs nothing, not even shipping."


def test_totals_without_discount():
    o = sample()
    assert o.subtotal == 200, "subtotal = 10*5 + 150*1 = 200."
    assert o.tax == 10.0, "tax = (200 - 0) * 0.05 = 10.0."
    assert o.shipping == 40, "200 is below 500, so shipping is 40."
    assert o.total == 250.0, "total = 200 - 0 + 10 + 40 = 250.0."


def test_totals_are_always_fresh():
    o = sample()
    assert o.total == 250.0
    o.add_line("bag", 400)
    assert o.subtotal == 600, "After add_line the subtotal must change: compute it in the property, do not store it."
    assert (o.tax, o.shipping, o.total) == (30.0, 0, 630.0), "600 is at least 500: no shipping. 600 + 30 tax = 630.0."


def test_coupon_and_discount():
    o = sample()
    o.apply_coupon("WELCOME10")
    assert o.discount_percent == 10, "WELCOME10 sets discount_percent to 10."
    assert (o.discount, o.tax, o.total) == (20.0, 9.0, 229.0), (
        "discount = 200 * 10 / 100 = 20.0; tax = 180 * 0.05 = 9.0; total = 200 - 20 + 9 + 40 = 229.0."
    )
    o.add_line("bag", 400)
    assert (o.discount, o.shipping, o.total) == (60.0, 0, 567.0), (
        "subtotal 600, discount 60, 540 >= 500 so no shipping; tax 27; total 567.0."
    )


def test_discount_can_bring_back_shipping():
    o = Order("Ravi")
    o.add_line("lamp", 550)
    assert o.shipping == 0, "550 is at least 500: free shipping."
    o.discount_percent = 10
    assert o.shipping == 40, "Free shipping is checked after the discount: 550 - 55 = 495 is below 500."
    o2 = Order("Zoya")
    o2.add_line("x", 500)
    assert o2.shipping == 0, "Exactly 500 counts as 'at least 500'."


def test_discount_percent_validation():
    o = sample()
    o.discount_percent = 50
    assert o.discount_percent == 50, "50 itself is allowed."
    o.discount_percent = 12.5
    assert o.discount == 25.0, "A float percent is fine: 200 * 12.5 / 100 = 25.0."
    for bad in (-1, 50.5, 60, "10"):
        with pytest.raises(ValueError):
            o.discount_percent = bad
    assert o.discount_percent == 12.5, "A rejected value must not replace the old one."


def test_unknown_coupon():
    o = sample()
    with pytest.raises(KeyError):
        o.apply_coupon("FREE100")
    assert o.discount_percent == 0, "An unknown coupon changes nothing."


def test_add_line_validation():
    o = Order("A")
    for price, qty in ((-1, 1), ("10", 1), (10, 0), (10, 1.5), (10, "2")):
        with pytest.raises(ValueError):
            o.add_line("x", price, qty)
    assert o.subtotal == 0, "Rejected lines are not added."
    o.add_line("free sample", 0)
    assert o.subtotal == 0 and o.shipping == 40, "A price of 0 is allowed; the order now has a line, so shipping applies."


def test_computed_properties_are_read_only():
    o = sample()
    for name in ("subtotal", "discount", "tax", "shipping", "total", "placed"):
        with pytest.raises(AttributeError):
            setattr(o, name, 1)


def test_orders_do_not_share_lines():
    a = Order("A")
    b = Order("B")
    a.add_line("pen", 10)
    assert b.subtotal == 0, "Each order needs its own list of lines (create it in __init__)."


def test_place_locks_the_order():
    o = sample()
    o.place()
    assert o.placed is True, "place() marks the order as placed."
    with pytest.raises(RuntimeError, match="already placed"):
        o.add_line("ink", 5)
    with pytest.raises(RuntimeError, match="already placed"):
        o.discount_percent = 10
    with pytest.raises(RuntimeError, match="already placed"):
        o.apply_coupon("HALF")
    with pytest.raises(RuntimeError):
        o.place()
    assert (o.subtotal, o.discount_percent, o.total) == (200, 0, 250.0), "Nothing changes after placing; totals still work."


def test_cannot_place_empty_order():
    o = Order("A")
    with pytest.raises(ValueError):
        o.place()
    assert o.placed is False, "A refused place() leaves the order open."
