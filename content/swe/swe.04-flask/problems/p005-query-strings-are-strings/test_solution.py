import pytest

from solution import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def get(client, query):
    r = client.get("/items" + query)
    assert r.status_code == 200, f"/items{query} must answer 200, got {r.status_code}"
    return r.get_json()


def test_defaults(client):
    assert get(client, "") == {"page": 1, "per_page": 20, "offset": 0}


def test_values_are_numbers(client):
    data = get(client, "?page=3&per_page=5")
    assert data == {"page": 3, "per_page": 5, "offset": 10}, f"got {data}; the values must be ints, not '3' and '5'."


@pytest.mark.parametrize("bad", ["abc", "0", "-3", "", "2.5"])
def test_bad_page_falls_back_to_1(client, bad):
    assert get(client, f"?page={bad}")["page"] == 1, f"page={bad!r} is not a page number >= 1, so the page is 1."


@pytest.mark.parametrize("raw,expected", [("500", 100), ("100", 100), ("101", 100), ("0", 1), ("-5", 1), ("abc", 20), ("", 20), ("7", 7)])
def test_per_page_is_clamped(client, raw, expected):
    assert get(client, f"?per_page={raw}")["per_page"] == expected, (
        f"per_page={raw!r} should become {expected}: clamp to 1..100, and use 20 when it is not a number.")


def test_offset(client):
    assert get(client, "?page=4&per_page=25")["offset"] == 75, "offset = (page - 1) * per_page"
    assert get(client, "?page=2&per_page=500")["offset"] == 100, "compute the offset with the CLAMPED per_page"
