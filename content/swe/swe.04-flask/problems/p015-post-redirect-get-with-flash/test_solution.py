import pytest
from bs4 import BeautifulSoup

from solution import create_app

GOOD = {"name": "Asha", "message": "Great course, thank you"}


@pytest.fixture
def app():
    return create_app({"TESTING": True})


@pytest.fixture
def client(app):
    return app.test_client()


def soup(r):
    return BeautifulSoup(r.get_data(as_text=True), "html.parser")


def test_form_page(client):
    s = soup(client.get("/feedback"))
    assert s.find("input", attrs={"name": "name"}) and s.find("textarea", attrs={"name": "message"})


def test_valid_post_redirects(client, app):
    r = client.post("/feedback", data=GOOD)
    assert r.status_code == 302, f"A valid POST must redirect (302), not render a page; got {r.status_code}. That is Post/Redirect/Get."
    assert r.headers["Location"] == "/thanks", f"Redirect to the thanks page with url_for('thanks'); got {r.headers['Location']!r}"
    assert app.extensions["feedback"] == [GOOD], f"The valid submission must be stored in app.extensions['feedback']; got {app.extensions['feedback']}"


def test_flash_is_shown_once(client):
    client.post("/feedback", data=GOOD)
    first = soup(client.get("/thanks"))
    assert [p.get_text() for p in first.select("p.flash")] == ["Thanks, Asha!"], "The flashed message must appear on /thanks."
    second = soup(client.get("/thanks"))
    assert second.select("p.flash") == [], "A flashed message is removed from the session after it is read once."
    assert "Nothing to see" in second.get_text()


def test_following_the_redirect(client):
    r = client.post("/feedback", data=GOOD, follow_redirects=True)
    assert r.status_code == 200 and "Thanks, Asha!" in r.get_data(as_text=True)


def test_refreshing_does_not_submit_again(client, app):
    client.post("/feedback", data=GOOD)
    client.get("/thanks")
    client.get("/thanks")
    assert len(app.extensions["feedback"]) == 1, "Reloading the thanks page must not store the feedback again."


def test_invalid_post_shows_errors_and_keeps_values(client, app):
    r = client.post("/feedback", data={"name": "  ", "message": "short <b>"})
    assert r.status_code == 200, "An invalid form is shown again with status 200 (no redirect)."
    s = soup(r)
    errors = [p.get_text() for p in s.select("p.error")]
    assert errors == ["Name is required", "Message must have at least 10 characters"], f"got {errors}"
    assert s.find("textarea").get_text() == "short <b>", "Keep what the user typed (the template escapes it)."
    assert s.find("b") is None
    assert app.extensions["feedback"] == [], "Invalid input must not be stored."


def test_only_the_bad_field_has_an_error(client):
    s = soup(client.post("/feedback", data={"name": "Asha", "message": "too short"}))
    assert [p.get_text() for p in s.select("p.error")] == ["Message must have at least 10 characters"]
    assert s.find("input", attrs={"name": "name"})["value"] == "Asha", "The valid field keeps its value."


def test_values_are_stripped(client, app):
    client.post("/feedback", data={"name": "  Asha ", "message": "  Great course, thank you  "})
    assert app.extensions["feedback"] == [GOOD], "Strip the values before validating and storing."
