import pytest
from bs4 import BeautifulSoup

from solution import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True})


def field(app, *args, **kwargs):
    macro = app.jinja_env.get_template("macros.html").module.render_field
    return BeautifulSoup(str(macro(*args, **kwargs)), "html.parser")


def test_label_and_input(app):
    soup = field(app, "email", "Email", "a@b.c")
    label = soup.find("label")
    assert label is not None and label["for"] == "email" and label.get_text(strip=True) == "Email", "Write <label for=\"NAME\">LABEL</label>."
    inp = soup.find("input")
    assert inp["id"] == "email" and inp["name"] == "email", "The input needs both id and name equal to NAME (the label points at the id)."
    assert inp["type"] == "text" and inp["value"] == "a@b.c"


def test_value_is_escaped(app):
    soup = field(app, "name", "Name", 'say "hi" <b>')
    assert soup.find("input")["value"] == 'say "hi" <b>', "The value attribute must be escaped so quotes cannot break out of it."
    assert soup.find("b") is None


def test_no_errors_means_no_error_markup(app):
    soup = field(app, "email", "Email", "x")
    inp = soup.find("input")
    assert not inp.has_attr("aria-invalid") and not inp.has_attr("aria-describedby"), "No errors: no aria attributes."
    assert soup.find("ul") is None, "No errors: no <ul>."


def test_errors_are_listed_and_linked(app):
    soup = field(app, "email", "Email", "x", ["Not valid", "Too short <b>"])
    inp = soup.find("input")
    assert inp["aria-invalid"] == "true", "Set aria-invalid=\"true\" when there are errors."
    assert inp["aria-describedby"] == "email-errors"
    ul = soup.find("ul", id="email-errors")
    assert ul is not None and "errors" in ul["class"], "Write <ul class=\"errors\" id=\"NAME-errors\">."
    assert [li.get_text() for li in ul.find_all("li")] == ["Not valid", "Too short <b>"], "One <li> per error, escaped."
    assert soup.find("b") is None


def test_password_value_is_never_printed(app):
    soup = field(app, "password", "Password", "secret123", type="password")
    inp = soup.find("input")
    assert inp["type"] == "password"
    assert "secret123" not in str(soup), "Never send a password back to the browser, not even in a failed form."


def test_missing_value_prints_nothing(app):
    soup = field(app, "email", "Email", None)
    assert soup.find("input").get("value", "") == "", "A None value must not print the word 'None'."


def test_page_keeps_values_and_shows_errors(app):
    client = app.test_client()
    r = client.post("/signup", data={"email": "bad", "password": "short"})
    soup = BeautifulSoup(r.get_data(as_text=True), "html.parser")
    assert soup.find("input", id="email")["value"] == "bad", "The typed email must stay in the field after a failed POST."
    assert [li.get_text() for li in soup.select("#email-errors li")] == ["Not a valid address"]
    assert [li.get_text() for li in soup.select("#password-errors li")] == ["Use at least 8 characters"]
    assert "short" not in str(soup.find("input", id="password")), "The password field must stay empty."


def test_fresh_page_has_no_errors(app):
    soup = BeautifulSoup(app.test_client().get("/signup").get_data(as_text=True), "html.parser")
    assert soup.find("ul", class_="errors") is None and soup.find(attrs={"aria-invalid": True}) is None
