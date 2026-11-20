import pytest

from solution import client_ip


@pytest.mark.parametrize("remote, header, n, expected", [
    ("10.0.0.1", "203.0.113.7", 1, "203.0.113.7"),
    ("10.0.0.1", "1.2.3.4, 203.0.113.7", 1, "203.0.113.7"),
    ("10.0.0.1", "1.2.3.4,203.0.113.7", 1, "203.0.113.7"),
    ("10.0.0.1", "  203.0.113.7  ", 1, "203.0.113.7"),
    ("10.0.0.2", "198.51.100.5, 10.0.0.1", 2, "198.51.100.5"),
    ("10.0.0.2", "6.6.6.6, 198.51.100.5, 10.0.0.1", 2, "198.51.100.5"),
    ("10.0.0.3", "9.9.9.9, 8.8.8.8, 7.7.7.7", 3, "9.9.9.9"),
    ("10.0.0.1", "2001:db8::1", 1, "2001:db8::1"),
    ("fd00::1", "2001:db8::7, 2001:db8::9", 1, "2001:db8::9"),
])
def test_count_from_the_right(remote, header, n, expected):
    got = client_ip(remote, header, n)
    assert got == expected, (
        f"remote_addr={remote!r}, header={header!r}, trusted_proxies={n}: expected {expected!r}, got {got!r}. "
        "Chain = header entries + [remote_addr]; the client is the item trusted_proxies + 1 places from the right.")


def test_default_is_one_trusted_proxy():
    assert client_ip("10.0.0.1", "5.5.5.5, 203.0.113.7") == "203.0.113.7", "trusted_proxies defaults to 1"


def test_a_spoofed_left_value_is_ignored():
    results = {client_ip("10.0.0.1", f"{lie}, 203.0.113.7", 1) for lie in ("1.1.1.1", "2.2.2.2", "127.0.0.1", "10.9.9.9", "unknown", "")}
    assert results == {"203.0.113.7"}, (
        f"Whatever the attacker writes on the left, the answer must stay 203.0.113.7; got {sorted(results)}. "
        "Do not read the left-most entry: the client controls it.")


def test_spoofed_header_cannot_give_a_fresh_key_each_time():
    keys = {client_ip("10.0.0.1", f"198.51.100.{i}, 203.0.113.7", 1) for i in range(1, 50)}
    assert len(keys) == 1, f"49 forged headers gave {len(keys)} different client keys; the limiter would never trigger"


@pytest.mark.parametrize("header", ["1.2.3.4", "1.2.3.4, 5.6.7.8", "", None])
def test_no_trusted_proxy_means_remote_addr(header):
    assert client_ip("203.0.113.7", header, 0) == "203.0.113.7", (
        "With trusted_proxies=0 nobody may be believed: return remote_addr, never a value from the header")
    assert client_ip("203.0.113.7", header, -1) == "203.0.113.7", "A negative count is treated like 0"


@pytest.mark.parametrize("header", [None, ""])
def test_missing_header_means_remote_addr(header):
    assert client_ip("203.0.113.7", header, 1) == "203.0.113.7", "No header: the connection address is the best we have"


def test_header_shorter_than_the_proxy_count():
    got = client_ip("10.0.0.2", "198.51.100.5", 3)
    assert got == "10.0.0.2", (
        f"3 proxies are expected but the chain has only 2 items: the request did not come through them. Fall back to remote_addr; got {got!r}")


@pytest.mark.parametrize("header", ["unknown", "not-an-ip", "999.1.1.1", "203.0.113.7, unknown", "203.0.113.7, "])
def test_invalid_entry_falls_back(header):
    got = client_ip("10.0.0.1", header, 1)
    assert got == "10.0.0.1", f"{header!r}: the chosen entry is not a valid IP address; return remote_addr, got {got!r}"


def test_returns_the_text_as_written():
    assert client_ip("10.0.0.1", "2001:DB8::A", 1) == "2001:DB8::A", "Return the entry unchanged (only stripped)"
