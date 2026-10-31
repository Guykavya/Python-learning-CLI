# Save the Cart class from problem.md as target.py in this folder, then run:
#     python -m pytest solution.py
import pytest

from target import Cart


def test_total():
    cart = Cart()
    cart.add("apple", 1.5, 2)
    assert cart.total() == 3.0
