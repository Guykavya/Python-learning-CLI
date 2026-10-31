# Save the code from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py -p no:cacheprovider
from unittest.mock import Mock

from target import notify


def test_returns_true():
    assert notify(Mock(), {"name": "Ann", "email": "ann@example.com"}, "hi")
