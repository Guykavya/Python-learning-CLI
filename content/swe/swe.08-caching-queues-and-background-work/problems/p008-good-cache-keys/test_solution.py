import hashlib
import re

import pytest

from solution import cache_key


def test_simple_key():
    assert cache_key("search", 2, page=1, sort="price", q="lamp") == "search:v2:page=1&q=lamp&sort=price", \
        "Expected 'search:v2:' + params sorted by name as name=value joined by '&'."


def test_order_does_not_matter():
    a = cache_key("search", 2, q="lamp", sort="price", page=1)
    b = cache_key("search", 2, page=1, q="lamp", sort="price")
    assert a == b, "The same parameters in another order must give the same key: sort by name."


def test_none_is_dropped():
    assert cache_key("search", 2, q="lamp", region=None) == "search:v2:q=lamp", "Parameters with value None are dropped."


def test_zero_and_empty_are_kept():
    assert cache_key("list", 1, page=0) == "list:v1:page=0", "0 is a real value: drop only None, not everything falsy."
    assert cache_key("list", 1, q="") == "list:v1:q=", "An empty string is a real value too."


def test_no_params():
    assert cache_key("config", 1) == "config:v1", "With no parameters the key is just 'namespace:vN'."
    assert cache_key("config", 1, x=None) == "config:v1", "All parameters None: also just 'namespace:vN'."


def test_version_changes_key():
    assert cache_key("p", 1, id=7) != cache_key("p", 2, id=7), "Bumping the version must give a new key."


def test_whitespace_is_hashed():
    key = cache_key("search", 2, q="red lamp", page=1)
    part = "page=1&q=red lamp"
    expected = "search:v2:sha256=" + hashlib.sha256(part.encode()).hexdigest()
    assert key == expected, "A params part with whitespace is replaced by 'sha256=' + the hex SHA-256 of that part."
    assert not re.search(r"\s", key), "The final key must contain no whitespace."
    assert cache_key("search", 2, q="redlamp", page=1) != key, "'red lamp' and 'redlamp' are different searches: do not just remove spaces."


def test_long_params_are_hashed():
    long_q = "x" * 70
    key = cache_key("search", 2, q=long_q)
    assert key.startswith("search:v2:sha256=") and len(key) == len("search:v2:sha256=") + 64, \
        "A params part longer than 64 characters is replaced by its SHA-256 hex (64 characters)."
    edge = "q=" + "y" * 62
    assert cache_key("s", 1, q="y" * 62) == "s:v1:" + edge, "Exactly 64 characters is NOT longer than 64: keep it as it is."


def test_tabs_and_newlines_are_whitespace():
    for text in ("a\tb", "a\nb"):
        assert "sha256=" in cache_key("s", 1, q=text), f"{text!r} contains whitespace: hash it."


def test_same_long_input_same_key():
    assert cache_key("s", 1, q="z" * 100) == cache_key("s", 1, q="z" * 100), "Hashing must be deterministic (SHA-256, not hash())."


@pytest.mark.parametrize("bad", ["", "a:b", "my cache", None])
def test_bad_namespace(bad):
    with pytest.raises(ValueError):
        cache_key(bad, 1, q="x")
