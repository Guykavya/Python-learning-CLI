from unittest.mock import Mock

import pytest

from target import fetch_with_retry


def test_success_at_once():
    client = Mock()
    client.get.side_effect = ["page"]
    assert fetch_with_retry(client, "u") == "page"
    assert client.get.call_count == 1, "No retry is needed after a success."


def test_success_on_the_last_attempt():
    client = Mock()
    client.get.side_effect = [ConnectionError("1"), ConnectionError("2"), "page"]
    assert fetch_with_retry(client, "u") == "page", "The third call is still allowed."
    assert client.get.call_count == 3


def test_all_attempts_fail_raises_the_last_error():
    client = Mock()
    client.get.side_effect = [ConnectionError("one"), ConnectionError("two"), ConnectionError("three")]
    with pytest.raises(ConnectionError, match="three"):
        fetch_with_retry(client, "u")
    assert client.get.call_count == 3, "Exactly 3 calls, no more."


def test_other_errors_are_not_retried():
    client = Mock()
    client.get.side_effect = [ValueError("bad"), "page"]
    with pytest.raises(ValueError):
        fetch_with_retry(client, "u")
    assert client.get.call_count == 1


def test_attempts_argument_is_used():
    for attempts in (1, 5):
        client = Mock()
        client.get.side_effect = ConnectionError("x")
        with pytest.raises(ConnectionError):
            fetch_with_retry(client, "u", attempts=attempts)
        assert client.get.call_count == attempts


def test_zero_attempts_is_invalid():
    with pytest.raises(ValueError):
        fetch_with_retry(Mock(), "u", attempts=0)
