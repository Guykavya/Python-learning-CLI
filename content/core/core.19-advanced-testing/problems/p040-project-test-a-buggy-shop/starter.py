# Save the buggy code from problem.md as shop.py in this folder.
# Write your tests here; run them with:   python -m pytest solution.py
import pytest

import shop


def test_subtotal():
    cart = shop.Cart({"pen": 150})
    cart.add("pen", 2)
    assert cart.subtotal() == 300
