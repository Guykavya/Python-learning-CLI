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
