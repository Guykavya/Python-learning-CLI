# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py
import pytest

from target import average


def test_simple_list():
    assert average([2, 4, 6]) == 4
