import pytest

from solution import classify


@pytest.mark.parametrize("addr,want", [
    ("127.0.0.1", "loopback"), ("127.5.5.5", "loopback"), ("::1", "loopback"),
    ("169.254.10.1", "link-local"), ("fe80::1", "link-local"),
    ("10.0.0.1", "private"), ("172.16.5.5", "private"), ("192.168.1.20", "private"), ("fd12:3456::1", "private"),
    ("8.8.8.8", "global"), ("1.1.1.1", "global"), ("2001:4860:4860::8888", "global"),
    ("224.0.0.1", "other"),
])
def test_valid_addresses(addr, want):
    assert classify(addr) == want, (
        f"{addr} should be '{want}'. Check from the most specific flag (loopback) to the most general; "
        "127.0.0.1 is also 'private' in the module's flags.")


@pytest.mark.parametrize("addr", ["", "999.1.1.1", "1.2.3", "localhost", "8.8.8.8:80", " 8.8.8.8", "abc", None, 12])
def test_invalid(addr):
    assert classify(addr) == "invalid", f"{addr!r} is not an IP address: return 'invalid', do not raise."
