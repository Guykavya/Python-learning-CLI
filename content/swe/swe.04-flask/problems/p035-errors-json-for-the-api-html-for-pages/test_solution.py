import pytest

from solution import create_app


@pytest.fixture
def client():
    return create_app({"TESTING": True, "PROPAGATE_EXCEPTIONS": False}).test_client()


def check_json_error(r, status, code, message):
    assert r.status_code == status, f"expected status {status}, got {r.status_code}"
    assert r.mimetype == "application/json", f"Under /api/ the error must be JSON, got {r.content_type} (a default HTML page?)."
    assert r.get_json() == {"error": {"code": code, "message": message}}, f"got {r.get_json()}"


def test_api_404_is_json(client):
    check_json_error(client.get("/api/missing"), 404, "not_found", "Not Found")


def test_page_404_is_html(client):
    r = client.get("/missing")
    assert r.status_code == 404 and r.mimetype == "text/html", f"Outside /api/ the error is an HTML page, got {r.content_type}."
    page = r.get_data(as_text=True)
    assert "<h1>404 Not Found</h1>" in page, f"The page needs <h1>404 Not Found</h1>; got {page[:120]!r}"
    assert 'href="/"' in page, "Add a link back to the home page."


def test_405_keeps_allow_in_both_shapes(client):
    r = client.post("/api/items")
    check_json_error(r, 405, "method_not_allowed", "Method Not Allowed")
    assert {m.strip() for m in r.headers["Allow"].split(",")} == {"GET", "HEAD", "OPTIONS"}, "A 405 must keep its Allow header."
    r = client.post("/")
    assert r.status_code == 405 and r.mimetype == "text/html" and "Allow" in r.headers
    assert "<h1>405 Method Not Allowed</h1>" in r.get_data(as_text=True)


def test_abort_inside_a_view_uses_the_same_handler(client):
    check_json_error(client.get("/api/forbidden"), 403, "forbidden", "Forbidden")


@pytest.mark.parametrize("path", ["/api/boom", "/boom"])
def test_unexpected_exception_is_a_clean_500(client, path):
    r = client.get(path)
    assert r.status_code == 500, f"An unexpected exception is a 500, got {r.status_code}. Register a handler for Exception."
    text = r.get_data(as_text=True)
    for secret in ("hunter2", "Traceback", "RuntimeError", "db password"):
        assert secret not in text, f"The error answer leaks {secret!r} to the client. Log the details, show a generic message."


def test_unexpected_exception_shapes(client):
    check_json_error(client.get("/api/boom"), 500, "internal_server_error", "Internal Server Error")
    r = client.get("/boom")
    assert r.mimetype == "text/html" and "<h1>500 Internal Server Error</h1>" in r.get_data(as_text=True)


def test_the_details_are_logged(client, caplog):
    import logging
    with caplog.at_level(logging.ERROR):
        client.get("/api/boom")
    assert any("hunter2" in r.getMessage() or (r.exc_info and "hunter2" in str(r.exc_info[1])) for r in caplog.records), (
        "The real exception must be written to the log (app.logger.exception(...)) so that you can debug it.")


def test_normal_pages_are_untouched(client):
    assert client.get("/").get_data(as_text=True) == "home"
    assert client.get("/api/items").get_json() == {"items": []}
