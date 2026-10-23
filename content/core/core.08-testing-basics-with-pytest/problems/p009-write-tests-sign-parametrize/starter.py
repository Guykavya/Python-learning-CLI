# Save the function from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py
import pytest

from target import sign


def test_positive():
    assert sign(5) == 1
