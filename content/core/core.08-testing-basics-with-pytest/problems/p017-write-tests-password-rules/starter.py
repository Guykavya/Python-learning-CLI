# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py

from target import is_valid_password


def test_valid():
    assert is_valid_password("Abcdefg1") is True
