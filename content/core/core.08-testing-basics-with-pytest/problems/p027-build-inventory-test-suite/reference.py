import pytest

from target import add_item, remove_item, total_items, low_stock


def test_add_new_item():
    stock = {}
    assert add_item(stock, "pen", 5) == 5, "add_item returns the new quantity."
    assert stock == {"pen": 5}, "The item must be stored in the dict."


def test_add_existing_item_adds_up():
    stock = {"pen": 5}
    assert add_item(stock, "pen", 3) == 8, "Adding to an existing item increases it (5 + 3), not replaces it."
    assert stock == {"pen": 8}, "The stored quantity must be 8."


def test_add_cleans_the_name():
    stock = {}
    add_item(stock, "  Pen ", 2)
    add_item(stock, "PEN", 1)
    assert stock == {"pen": 3}, "Names are stripped and lower-cased, so ' Pen ' and 'PEN' are the same item."


@pytest.mark.parametrize("qty", [0, -1, -10])
def test_add_rejects_bad_quantity(qty):
    with pytest.raises(ValueError, match="positive"):
        add_item({}, "pen", qty)


@pytest.mark.parametrize("name", ["", "   "])
def test_add_rejects_empty_name(name):
    with pytest.raises(ValueError, match="empty"):
        add_item({}, name, 1)


def test_remove_some():
    stock = {"pen": 5}
    assert remove_item(stock, "pen", 2) == 3, "remove_item returns what is left."
    assert stock == {"pen": 3}, "The quantity must go down by 2."


def test_remove_all_deletes_the_item():
    stock = {"pen": 5, "ink": 1}
    assert remove_item(stock, "pen", 5) == 0, "Removing everything leaves 0."
    assert "pen" not in stock, "An item with quantity 0 must be deleted from the dict."
    assert stock == {"ink": 1}, "Other items stay untouched."


def test_remove_unknown_item_is_key_error():
    with pytest.raises(KeyError):
        remove_item({"pen": 1}, "ink", 1)


def test_remove_more_than_stock():
    stock = {"pen": 2}
    with pytest.raises(ValueError, match="stock"):
        remove_item(stock, "pen", 3)
    assert stock == {"pen": 2}, "A failed removal must not change the stock."


def test_remove_bad_quantity():
    with pytest.raises(ValueError, match="positive"):
        remove_item({"pen": 2}, "pen", 0)


def test_total_items():
    assert total_items({}) == 0, "An empty inventory has 0 units."
    assert total_items({"pen": 2, "ink": 3}) == 5, "Add up the quantities, not the number of items."


def test_low_stock_is_below_the_limit():
    stock = {"pen": 2, "ink": 5, "pad": 9}
    assert low_stock(stock, 5) == ["pen"], "5 is not below 5: strictly below the limit."
    assert low_stock(stock, 6) == ["ink", "pen"], "Result must be sorted by name."
    assert low_stock({}, 5) == [], "Nothing in stock, nothing is low."
