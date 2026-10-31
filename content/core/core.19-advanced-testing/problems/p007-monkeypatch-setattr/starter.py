# Save the code from problem.md as target.py in this folder, then run:
#     python -m pytest solution.py
import target


def test_price_with_tax_default():
    assert target.price_with_tax(10) == 12.0
