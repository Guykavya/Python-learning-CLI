import pytest

from solution import create_app

ALLOWED = "https://app.example"


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def preflight(client, origin=ALLOWED, path="/api/ping"):
    headers = {"Access-Control-Request-Method": "POST"}
    if origin is not None:
        headers["Origin"] = origin
    return client.options(path, headers=headers)


def cors_headers(response):
    return {k: v for k, v in response.headers.items() if k.lower().startswith("access-control-")}


def test_preflight_for_an_allowed_origin(client):
    r = preflight(client)
    assert r.status_code == 204 and r.get_data() == b"", f"A preflight is answered 204 with no body, got {r.status_code}."
    assert r.headers["Access-Control-Allow-Origin"] == ALLOWED, "Echo the allowed origin exactly."
    methods = {m.strip() for m in r.headers["Access-Control-Allow-Methods"].split(",")}
    assert methods == {"GET", "POST", "PUT", "PATCH", "DELETE"}, f"got {methods}"
    headers = {h.strip().lower() for h in r.headers["Access-Control-Allow-Headers"].split(",")}
    assert headers == {"content-type", "authorization"}, f"got {headers}"
    assert r.headers["Access-Control-Max-Age"] == "600"
    assert r.headers["Access-Control-Allow-Credentials"] == "true"


def test_the_origin_is_echoed_never_a_wildcard(client):
    for r in (preflight(client), client.get("/api/ping", headers={"Origin": ALLOWED})):
        assert r.headers["Access-Control-Allow-Origin"] != "*", "Never send * together with credentials: echo the exact allowed origin."


def test_vary_origin_on_every_api_response(client):
    for r in (preflight(client), preflight(client, "https://evil.example"), client.get("/api/ping"), client.get("/api/ping", headers={"Origin": ALLOWED})):
        assert "Origin" in r.headers.get("Vary", ""), "Every /api/ response needs Vary: Origin, so caches do not mix up answers for different origins."


def test_normal_request_from_an_allowed_origin(client):
    r = client.get("/api/ping", headers={"Origin": ALLOWED})
    assert r.status_code == 200 and r.get_data(as_text=True) == "pong"
    assert r.headers["Access-Control-Allow-Origin"] == ALLOWED and r.headers["Access-Control-Allow-Credentials"] == "true"
    assert "Access-Control-Allow-Methods" not in r.headers, "The method/header lists belong to the preflight only."


@pytest.mark.parametrize("origin", ["https://evil.example", "null", "http://app.example", "https://app.example.evil.com", "https://sub.app.example", "HTTPS://APP.EXAMPLE", ""])
def test_other_origins_get_nothing(client, origin):
    r = preflight(client, origin)
    assert cors_headers(r) == {}, f"Origin {origin!r} is not allowed: no Access-Control-* header at all, got {cors_headers(r)}. Compare with the exact string."
    r = client.get("/api/ping", headers={"Origin": origin})
    assert r.status_code == 200 and cors_headers(r) == {}, "The request is still served; only the CORS headers are withheld."


def test_no_origin_header_means_no_cors_headers(client):
    r = client.get("/api/ping")
    assert r.status_code == 200 and cors_headers(r) == {}


def test_outside_api_nothing_is_added(client):
    r = client.get("/ping", headers={"Origin": ALLOWED})
    assert r.status_code == 200 and cors_headers(r) == {} and "Vary" not in r.headers, "Only /api/ paths take part in CORS."


def test_options_without_preflight_headers_is_not_a_preflight(client):
    r = client.options("/api/ping", headers={"Origin": ALLOWED})
    assert "Access-Control-Allow-Methods" not in r.headers, "A preflight needs the Access-Control-Request-Method header."


def test_allowed_origins_come_from_the_config():
    client = create_app({"TESTING": True, "CORS_ORIGINS": ["https://one.example", "https://two.example"]}).test_client()
    assert preflight(client, "https://two.example").headers["Access-Control-Allow-Origin"] == "https://two.example"
    assert cors_headers(preflight(client, ALLOWED)) == {}, "The list in app.config['CORS_ORIGINS'] decides."
