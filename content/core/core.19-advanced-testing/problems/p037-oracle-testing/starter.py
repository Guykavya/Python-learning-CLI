# Save the code from problem.md as target.py in this folder to try your tests:
#     python -m pytest solution.py
import pytest
from hypothesis import given, settings, strategies as st

from target import max_subarray_sum


def test_known_case():
    assert max_subarray_sum([2, -5, 3, 4]) == 7
