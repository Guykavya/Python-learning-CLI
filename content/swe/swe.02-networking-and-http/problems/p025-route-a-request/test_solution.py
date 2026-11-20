import pytest

from solution import route

ROUTES = {
    ("GET", "/notes"): "list",
    ("POST", "/notes"): "add",
    ("GET", "/notes/{id}"): "get",
    ("DELETE", "/notes/{id}"): "delete",
    ("GET", "/notes/new"): "form",
    ("GET", "/users/{uid}/notes/{id}"): "user_note",
    ("GET", "/files/{name}.txt"): "file",
}


def test_fixed_paths():
    assert route(ROUTES, "GET", "/notes") == (200, "list", {})
    assert route(ROUTES, "POST", "/notes") == (200, "add", {})


def test_parameters_are_captured_as_text():
    assert route(ROUTES, "GET", "/notes/7") == (200, "get", {"id": "7"})
    assert route(ROUTES, "DELETE", "/notes/abc") == (200, "delete", {"id": "abc"})
    assert route(ROUTES, "GET", "/users/u1/notes/9") == (200, "user_note", {"uid": "u1", "id": "9"})


def test_unknown_path_is_404():
    for path in ("/nothing", "/", "/notes/7/extra", "/notes/", "/note", "/users/u1/notes"):
        assert route(ROUTES, "GET", path) == (404, None, {}), (
            f"{path} matches no pattern: 404. (Anchor the regex; a parameter is one non-empty segment.)")


def test_wrong_method_is_405_with_allow():
    assert route(ROUTES, "PUT", "/notes") == (405, None, {"Allow": "GET, POST"}), (
        "The path exists but not for PUT: 405 and an Allow header with the methods that work, sorted.")
    assert route(ROUTES, "POST", "/notes/7") == (405, None, {"Allow": "DELETE, GET"})


def test_more_specific_pattern_first():
    assert route(ROUTES, "GET", "/notes/new") == (200, "form", {}), "/notes/new beats /notes/{id}."
    assert route(ROUTES, "DELETE", "/notes/new") == (200, "delete", {"id": "new"}), (
        "The fixed route has no DELETE, but /notes/{id} does: use it.")
    assert route(ROUTES, "PUT", "/notes/new") == (405, None, {"Allow": "DELETE, GET"}), (
        "405 lists the methods of all patterns that match the path.")


def test_method_is_case_insensitive_and_head_uses_get():
    assert route(ROUTES, "get", "/notes") == (200, "list", {})
    assert route(ROUTES, "HEAD", "/notes/3") == (200, "get", {"id": "3"}), "HEAD falls back to the GET handler."
    r = dict(ROUTES)
    r[("HEAD", "/notes")] = "head_list"
    assert route(r, "HEAD", "/notes") == (200, "head_list", {})


def test_fixed_text_is_escaped():
    assert route(ROUTES, "GET", "/files/a.txt") == (200, "file", {"name": "a"})
    assert route(ROUTES, "GET", "/files/aXtxt") == (404, None, {}), "The '.' in a pattern is a dot, not 'any character'."


def test_a_parameter_never_matches_a_slash_or_nothing():
    assert route(ROUTES, "GET", "/notes/a/b")[0] == 404
    assert route(ROUTES, "GET", "/notes//")[0] == 404
