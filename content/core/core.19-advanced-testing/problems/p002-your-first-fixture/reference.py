import pytest

from target import Cart


@pytest.fixture
def cart():
    c = Cart()
    c.add("apple", 1.5, 2)
    c.add("bread", 3.0)
    return c


def test_total_counts_every_unit(cart):
    assert cart.total() == 6.0, "2 apples at 1.50 plus 1 bread at 3.00 is 6.00 (quantity matters)."


def test_count_is_in_units(cart):
    assert cart.count() == 3, "count() is the number of units: 2 apples + 1 bread = 3."


def test_adding_an_existing_item_adds_quantity(cart):
    cart.add("apple", 1.5, 3)
    assert cart.count() == 6, "Adding apples again must increase the quantity, not replace the line."
    assert cart.total() == 7.5 + 3.0, "5 apples at 1.50 plus the bread."


def test_remove_takes_the_whole_line_away(cart):
    cart.remove("bread")
    assert cart.total() == 3.0, "After removing the bread only the apples are left."
    assert cart.count() == 2, "After removing the bread 2 units are left."


def test_removing_a_missing_item_raises(cart):
    with pytest.raises(KeyError):
        cart.remove("milk")


def test_zero_quantity_is_rejected(cart):
    with pytest.raises(ValueError):
        cart.add("milk", 1.0, 0)


def test_each_test_gets_a_fresh_cart(cart):
    cart.add("milk", 1.0)
    assert cart.count() == 4, "A new cart per test: milk is the only extra item here."
