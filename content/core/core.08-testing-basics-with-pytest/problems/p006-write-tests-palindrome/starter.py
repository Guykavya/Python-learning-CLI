# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py

from target import is_palindrome


def test_palindrome():
    assert is_palindrome("level") is True
