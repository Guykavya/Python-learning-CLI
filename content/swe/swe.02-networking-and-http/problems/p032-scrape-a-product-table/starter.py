import re
from decimal import Decimal

from bs4 import BeautifulSoup


def parse_products(html):
    soup = BeautifulSoup(html, "html.parser")
    # TODO: one dict per tr.product: name (clean text), price (Decimal or None), in_stock (bool)
    return []
