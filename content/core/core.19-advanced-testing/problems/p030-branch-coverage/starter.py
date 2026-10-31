# Save the function from problem.md as target.py in this folder, then try:
#     python -m coverage run --branch -m pytest solution.py
#     python -m coverage report -m
from target import parcel_fee


def test_ten_kilos_at_home():
    assert parcel_fee(10, "home", False, []) == 1000
