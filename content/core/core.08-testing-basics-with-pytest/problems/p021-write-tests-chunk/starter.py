# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py
import pytest

from target import chunk


def test_exact_division():
    assert chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
