# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py
import pytest

from target import add_item, remove_item, total_items, low_stock


def test_add_new_item():
    stock = {}
    assert add_item(stock, "pen", 5) == 5
