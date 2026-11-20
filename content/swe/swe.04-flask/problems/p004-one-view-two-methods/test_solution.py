import pytest

from solution import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def text(r):
    return r.get_data(as_text=True)


def test_get_shows_the_form(client):
    r = client.get("/contact")
    assert r.status_code == 200
    assert '<form method="post"' in text(r) and 'name="name"' in text(r), "The GET page must contain the form with an input called name."


def test_post_thanks(client):
    r = client.post("/contact", data={"name": "Asha"})
    assert r.status_code == 200, "POST must be allowed on /contact: add methods=['GET', 'POST'] to the route."
    assert text(r) == "Thanks, Asha!"


def test_post_is_escaped(client):
    r = client.post("/contact", data={"name": "<b>x</b>"})
    assert "<b>" not in text(r), "User input must be escaped before it goes into HTML (markupsafe.escape)."
    assert "&lt;b&gt;" in text(r)


@pytest.mark.parametrize("data", [{}, {"name": ""}, {"name": "   "}])
def test_missing_or_blank_name_is_400(client, data):
    r = client.post("/contact", data=data)
    assert r.status_code == 400, f"A missing or blank name is a client error (400), got {r.status_code}."
    assert text(r) == "Name is required"


def test_put_is_405_with_allow_header(client):
    r = client.put("/contact", data={"name": "x"})
    assert r.status_code == 405, f"Methods other than GET/POST must give 405, got {r.status_code}."
    allowed = {m.strip() for m in r.headers["Allow"].split(",")}
    assert allowed == {"GET", "HEAD", "OPTIONS", "POST"}, f"The Allow header should list GET, HEAD, OPTIONS, POST; got {sorted(allowed)}."


def test_delete_is_405(client):
    assert client.delete("/contact").status_code == 405
