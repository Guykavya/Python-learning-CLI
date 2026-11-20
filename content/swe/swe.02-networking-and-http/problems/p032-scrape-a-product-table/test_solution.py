from decimal import Decimal

from solution import parse_products

PAGE = """
<html><body>
<table id="products">
  <tr><th>Name</th><th>Price</th><th>Stock</th></tr>
  <tr class="product">
    <td class="name">  Green <a href="/t/1"><b>Tea</b></a>
    </td>
    <td class="price">₹1,299.00</td>
    <td class="stock">In stock</td>
  </tr>
  <tr class="product"><td class="name">Coffee   Beans</td><td class="price"> N/A </td><td class="stock"> Out of   stock</td></tr>
  <tr class="product"><td class="name">Mug</td><td class="price">Rs. 250</td><td class="stock">IN STOCK (3 left)</td></tr>
  <tr class="product"><td class="name">Spoon</td><td class="price"></td></tr>
  <tr class="product"><td class="price">99</td><td class="stock">In stock</td></tr>
  <tr class="advert"><td class="name">Not a product</td></tr>
  <tr class="product"><td class="name">Kettle</td><td class="price"><span>₹</span> <b>12,45,000.50</b></td><td class="stock">Back soon</td></tr>
</table>
</body></html>
"""


def test_the_example_row():
    first = parse_products(PAGE)[0]
    assert first == {"name": "Green Tea", "price": Decimal("1299.00"), "in_stock": True}, (
        f"Got {first}. The name is the text with nested tags removed and white space collapsed; the price is a Decimal.")
    assert isinstance(first["price"], Decimal), "Money as Decimal, not float."


def test_all_rows_in_page_order():
    got = parse_products(PAGE)
    assert [p["name"] for p in got] == ["Green Tea", "Coffee Beans", "Mug", "Spoon", "Kettle"], (
        "Skip the header row, the row with class 'advert' and the row without a name cell.")


def test_missing_or_bad_prices_are_none():
    got = {p["name"]: p for p in parse_products(PAGE)}
    assert got["Coffee Beans"]["price"] is None, "'N/A' is not a number: price None, no exception."
    assert got["Spoon"]["price"] is None, "An empty price cell gives None."


def test_currency_signs_and_separators():
    got = {p["name"]: p for p in parse_products(PAGE)}
    assert got["Mug"]["price"] == Decimal("250"), "Ignore 'Rs.' and spaces."
    assert got["Kettle"]["price"] == Decimal("1245000.50"), "Remove all thousands commas, also inside nested tags."


def test_stock_flag():
    got = {p["name"]: p for p in parse_products(PAGE)}
    assert got["Coffee Beans"]["in_stock"] is False, "'Out of stock' contains 'stock' but is not in stock."
    assert got["Mug"]["in_stock"] is True, "Case does not matter and extra text after 'in stock' is fine."
    assert got["Spoon"]["in_stock"] is False, "A missing stock cell means not in stock."
    assert got["Kettle"]["in_stock"] is False


def test_empty_pages():
    assert parse_products("") == []
    assert parse_products("<html><body><p>nothing here</p></body></html>") == []
    assert parse_products('<table><tr><th>Name</th></tr></table>') == []
