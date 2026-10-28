import pytest

from solution import api_url, build_url, host_port, parse_query


def test_build_url_basic():
    assert build_url("https://shop.example/search", {"q": "python & sql", "page": 2}) == (
        "https://shop.example/search?q=python+%26+sql&page=2"
    ), "Use urlencode: '&' inside a value must become %26 and spaces become '+'. Numbers are converted for you."


def test_build_url_lists_and_unicode():
    url = build_url("http://x.example/f", {"tag": ["a b", "c"], "city": "Pune ñ"})
    assert url == "http://x.example/f?tag=a+b&tag=c&city=Pune+%C3%B1", (
        "A list value repeats the key: pass doseq=True to urlencode. Non-ASCII letters are UTF-8 percent-encoded."
    )


def test_build_url_empty_params():
    assert build_url("http://x.example/f", {}) == "http://x.example/f", "No params: return base unchanged, without a lone '?'."


def test_parse_query():
    got = parse_query("https://shop.example/search?q=python+%26+sql&tag=a&tag=b")
    assert got == {"q": ["python & sql"], "tag": ["a", "b"]}, "parse_qs decodes '+' and %26 and returns lists, one item per repeat."


def test_parse_query_blank_and_missing():
    assert parse_query("http://x.example/?a=&b=1") == {"a": [""], "b": ["1"]}, "Keep keys with empty values: keep_blank_values=True."
    assert parse_query("http://x.example/path") == {}, "No query string: an empty dict."
    assert parse_query("http://x.example/p?x=1#y=2") == {"x": ["1"]}, "The #fragment is not part of the query: use urlsplit(url).query."


def test_roundtrip():
    params = {"q": "a=b&c?d/e", "n": "100%"}
    assert {k: v[0] for k, v in parse_query(build_url("http://h.example/s", params)).items()} == params, (
        "Encoding then decoding must give the original values back, however strange."
    )


def test_host_port_defaults():
    assert host_port("https://Example.COM/api") == ("example.com", 443), "Host in lower case (urlsplit(...).hostname); https defaults to 443."
    assert host_port("http://shop.example") == ("shop.example", 80), "http defaults to port 80."


def test_host_port_explicit():
    assert host_port("http://localhost:8080/") == ("localhost", 8080), "An explicit port wins; .port is already an int."
    assert host_port("https://127.0.0.1:8443/x?y=1") == ("127.0.0.1", 8443), "IP addresses are hosts too."


def test_host_port_errors():
    with pytest.raises(ValueError):
        host_port("/just/a/path")            # no host
    with pytest.raises(ValueError):
        host_port("ftp://files.example/")    # no port and no default for ftp


def test_api_url():
    assert api_url("http://127.0.0.1:8000/api/", "users", "a b/c") == "http://127.0.0.1:8000/api/users/a%20b%2Fc", (
        "Escape each segment with quote(s, safe=''): with the default safe='/' the '/' inside 'a b/c' stays and adds a path level."
    )


def test_api_url_more():
    assert api_url("http://h.example/api", "café", "?x=1") == "http://h.example/api/caf%C3%A9/%3Fx%3D1", (
        "'?' and '=' inside a segment must be escaped too, or they start a query string."
    )
    assert api_url("http://h.example/api") == "http://h.example/api", "No segments: just the base without a trailing '/'."
    assert api_url("http://h.example/api///", "x") == "http://h.example/api/x", "Remove all trailing '/' from base (rstrip)."
