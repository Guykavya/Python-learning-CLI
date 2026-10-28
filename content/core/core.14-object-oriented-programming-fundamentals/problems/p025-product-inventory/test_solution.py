import pytest

from solution import Inventory, Product

CSV = "sku,name,price,stock\nP1,Pen,10,40\nN2,Notebook,45.5,3\n"


def test_product_attributes():
    p = Product("P1", "Pen", 10, 40)
    assert (p.sku, p.name, p.price, p.stock) == ("P1", "Pen", 10, 40), "Store sku, name, price and stock as attributes."
    q = Product("E1", "Eraser", 5)
    assert q.stock == 0, "stock defaults to 0."


def test_product_validation():
    for price in (-1, "10"):
        with pytest.raises(ValueError):
            Product("X", "x", price)
    for stock in (-1, 2.5, "3"):
        with pytest.raises(ValueError):
            Product("X", "x", 1, stock)
    assert Product("F", "Free sticker", 0).price == 0, "A price of 0 is allowed (0 or more)."


def test_from_row_converts_and_strips():
    p = Product.from_row({"sku": " P1", "name": "Pen ", "price": " 10", "stock": "40 "})
    assert isinstance(p, Product), "from_row must return a Product object."
    assert p.sku == "P1" and p.name == "Pen", "Strip spaces from the text values."
    assert p.price == 10.0 and isinstance(p.price, float), "Turn price into a float."
    assert p.stock == 40 and isinstance(p.stock, int), "Turn stock into an int."


def test_from_row_bad_number():
    with pytest.raises(ValueError):
        Product.from_row({"sku": "P1", "name": "Pen", "price": "ten", "stock": "4"})
    with pytest.raises(ValueError):
        Product.from_row({"sku": "P1", "name": "Pen", "price": "10", "stock": "-4"})


def test_from_row_respects_subclass():
    class Book(Product):
        pass

    b = Book.from_row({"sku": "B1", "name": "Python", "price": "350", "stock": "2"})
    assert type(b) is Book, "from_row must build the object with cls(...), not Product(...), so subclasses get their own type."


def test_add_get_duplicate():
    inv = Inventory()
    pen = Product("P1", "Pen", 10, 40)
    inv.add(pen)
    assert inv.get("P1") is pen, "get(sku) returns the same Product object that was added."
    with pytest.raises(ValueError):
        inv.add(Product("P1", "Other pen", 12))
    assert inv.get("P1").name == "Pen", "A duplicate sku must not replace the first product."
    with pytest.raises(KeyError):
        inv.get("X9")


def test_from_csv():
    inv = Inventory.from_csv(CSV)
    assert isinstance(inv, Inventory), "from_csv returns an Inventory."
    n = inv.get("N2")
    assert (n.name, n.price, n.stock) == ("Notebook", 45.5, 3), "Each CSV row becomes a Product via from_row."
    assert inv.low_stock() == ["N2"], "N2 has 3 pieces, below the default threshold 5. P1 has 40."


def test_sell_and_restock():
    inv = Inventory.from_csv(CSV)
    assert inv.sell("P1", 5) == 50.0, "sell returns price * qty: 10 * 5 = 50.0."
    assert inv.get("P1").stock == 35, "Selling 5 of 40 leaves 35."
    inv.restock("N2", 10)
    assert inv.get("N2").stock == 13, "restock adds to the stock: 3 + 10."
    assert inv.low_stock() == [], "Nothing is below 5 now."
    assert inv.total_value() == 941.5, "total_value is 10*35 + 45.5*13 = 941.5."


def test_sell_too_many_changes_nothing():
    inv = Inventory.from_csv(CSV)
    with pytest.raises(ValueError, match="3"):
        inv.sell("N2", 4)
    assert inv.get("N2").stock == 3, "A failed sale must not change the stock."
    with pytest.raises(ValueError):
        inv.sell("N2", 0)
    with pytest.raises(KeyError):
        inv.sell("X9", 1)


def test_restock_bad_qty():
    inv = Inventory.from_csv(CSV)
    for bad in (0, -3, 1.5):
        with pytest.raises(ValueError):
            inv.restock("P1", bad)
    assert inv.get("P1").stock == 40, "A failed restock must not change the stock."
    with pytest.raises(KeyError):
        inv.restock("X9", 2)


def test_low_stock_threshold_and_order():
    inv = Inventory()
    inv.add(Product("C", "c", 1, 2))
    inv.add(Product("A", "a", 1, 9))
    inv.add(Product("B", "b", 1, 5))
    assert inv.low_stock(10) == ["C", "A", "B"], "Keep the order the products were added, do not sort."
    assert inv.low_stock(5) == ["C"], "Below means stock < threshold: 5 is not below 5."
    assert inv.low_stock(0) == [], "Nothing is below 0."


def test_inventories_are_separate():
    a = Inventory()
    b = Inventory()
    a.add(Product("P1", "Pen", 10))
    with pytest.raises(KeyError):
        b.get("P1")
