## Approach

```python
import re
from decimal import Decimal

from bs4 import BeautifulSoup

_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _price(cell):
    if cell is None:
        return None
    found = _NUMBER.search(cell.get_text())
    if not found:
        return None
    return Decimal(found.group().replace(",", ""))


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    for row in soup.select("tr.product"):
        name_cell = row.select_one("td.name")
        if name_cell is None:
            continue
        stock_cell = row.select_one("td.stock")
        stock_text = " ".join(stock_cell.get_text().split()).lower() if stock_cell else ""
        products.append({
            "name": " ".join(name_cell.get_text().split()),
            "price": _price(row.select_one("td.price")),
            "in_stock": stock_text.startswith("in stock"),
        })
    return products
```

Every optional piece is looked up with `select_one`, which returns `None` instead of raising, and the code handles `None` explicitly: a scraper meets bad pages all the time and must not crash on them. `get_text()` plus `split()/join` is the standard way to normalise text (it removes the line breaks and indentation of the HTML source). The price is taken with a regular expression that finds the first number, so `₹`, `Rs.` or a trailing space do not matter; `Decimal` (not `float`) keeps money exact: `Decimal("1299.00")`. `"In stock"` is matched with `startswith` so that `"Out of stock"` (which *contains* `stock`) is not mistaken for it.

Example: the cell `₹1,299.00` gives the match `1,299.00`; removing the comma gives `1299.00`.

## Complexity

`O(size of the page)`.

## Another way

`lxml` with XPath, or `pandas.read_html`, parse tables too. BeautifulSoup is the most forgiving of broken HTML, which is common.

## Why it matters

Scraping fails at the edges: a missing cell, a price of "N/A", Indian-style or European number formats. Returning `None` and carrying on keeps one bad row from losing the whole page.
