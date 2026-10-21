# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py
import pytest

from target import ticket_price


def test_adult():
    assert ticket_price(30) == 100
