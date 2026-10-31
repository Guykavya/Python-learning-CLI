# Save the code from problem.md as target.py in this same folder to try your tests:
#     python -m pytest solution.py -p no:cacheprovider
from unittest.mock import Mock

from target import fetch_with_retry


def test_success_at_once():
    client = Mock()
    client.get.return_value = "page"
    assert fetch_with_retry(client, "u") == "page"
