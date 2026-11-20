from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient

from solution import build_app

GOOD = "https://app.example.com/cb"


@pytest.fixture
def client():
    with TestClient(build_app(), follow_redirects=False) as c:
        yield c


def authorize(client, uri, client_id="printshop"):
    return client.get("/authorize", params={"client_id": client_id, "redirect_uri": uri, "state": "xyz"})


def test_registered_uri_still_works(client):
    r = authorize(client, GOOD)
    assert r.status_code == 302, f"A registered redirect_uri must still get a redirect, got {r.status_code}."
    parts = urlsplit(r.headers["location"])
    query = parse_qs(parts.query)
    assert f"{parts.scheme}://{parts.netloc}{parts.path}" == GOOD
    assert query["state"] == ["xyz"] and len(query["code"][0]) >= 20, "The redirect must carry the code and echo the state."


def test_second_registered_uri_works(client):
    assert authorize(client, "https://app.example.com/cb2").status_code == 302, "A client may register several URIs; each must work."


def test_custom_scheme_of_a_mobile_client_works(client):
    r = authorize(client, "com.example.mobile:/oauth", client_id="mobile")
    assert r.status_code == 302, "Exact matching must also work for non-https registered URIs."


@pytest.mark.parametrize("evil", [
    "https://app.example.com.evil.net/cb",
    "https://app.example.com/cb/../x",
    "https://app.example.com/cb/",
    "https://app.example.com/cbevil",
    "https://app.example.com/cb?next=https://evil.net",
    "https://app.example.com/cb#frag",
    "https://app.example.com/cb2/extra",
    "https://app.example.com@evil.net/cb",
    "http://app.example.com/cb",
    "HTTPS://APP.EXAMPLE.COM/cb",
    "https://evil.net/",
    "",
])
def test_anything_but_an_exact_match_is_refused(client, evil):
    r = authorize(client, evil)
    assert r.status_code == 400, (
        f"redirect_uri {evil!r} was accepted ({r.status_code}). Compare the WHOLE string with the registered values; "
        "'starts with' lets https://app.example.com.evil.net/cb through.")
    assert "location" not in r.headers, "Never redirect to an unverified address, not even with an error."
    assert "code" not in r.text, "No authorization code may be issued for a refused redirect_uri."


def test_a_client_cannot_use_another_clients_uri(client):
    assert authorize(client, "com.example.mobile:/oauth", client_id="printshop").status_code == 400, "A redirect_uri is registered per client."
    assert authorize(client, GOOD, client_id="mobile").status_code == 400


def test_unknown_client_is_refused(client):
    assert authorize(client, GOOD, client_id="nobody").status_code == 400
