import pytest

from solution import split_hostport


def test_plain_host_and_port():
    assert split_hostport("example.com:8080") == ("example.com", 8080)
    port = split_hostport("example.com:8080")[1]
    assert isinstance(port, int), "The port must be an int, not a string."


def test_default_ports_by_scheme():
    assert split_hostport("localhost") == ("localhost", 80)
    assert split_hostport("localhost", "http") == ("localhost", 80)
    assert split_hostport("localhost", "https") == ("localhost", 443)
    assert split_hostport("localhost:8443", "https") == ("localhost", 8443), "An explicit port beats the default."


def test_unknown_scheme_without_port():
    with pytest.raises(ValueError):
        split_hostport("example.com", "ftp")
    assert split_hostport("example.com:21", "ftp") == ("example.com", 21)


def test_ipv6_in_brackets():
    assert split_hostport("[::1]:443") == ("::1", 443), "Remove the brackets from the host."
    assert split_hostport("[::1]") == ("::1", 80)
    assert split_hostport("[2001:db8::1]:9000") == ("2001:db8::1", 9000)
    assert split_hostport("[::1]", "https") == ("::1", 443)


@pytest.mark.parametrize("text", ["::1", "a:b:c", "2001:db8::1:80"])
def test_ipv6_without_brackets_is_ambiguous(text):
    with pytest.raises(ValueError):
        split_hostport(text)


@pytest.mark.parametrize("text", ["host:0", "host:65536", "host:70000", "host:http", "host:", "host:-1", "host: 80",
                                  "host:+80", "host:８０", "host:8 0"])
def test_bad_ports(text):
    with pytest.raises(ValueError):
        split_hostport(text)


def test_port_limits_are_allowed():
    assert split_hostport("h:1") == ("h", 1)
    assert split_hostport("h:65535") == ("h", 65535)


@pytest.mark.parametrize("text", ["", ":80", "[]:80", "[::1", "[::1]x", "[::1]:"])
def test_empty_host_and_bad_brackets(text):
    with pytest.raises(ValueError):
        split_hostport(text)
