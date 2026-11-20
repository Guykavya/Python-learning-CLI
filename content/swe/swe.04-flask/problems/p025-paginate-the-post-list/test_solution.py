import pytest

from solution import Post, create_app, db


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    with app.app_context():
        db.session.add_all([Post(title=f"Post {i}") for i in range(1, 24)])
        db.session.commit()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_first_page_newest_first(client):
    r = client.get("/posts")
    assert r.status_code == 200
    data = r.get_json()
    assert data["items"] == ["Post 23", "Post 22", "Post 21", "Post 20", "Post 19"], f"Newest first, 5 per page; got {data['items']}"
    assert (data["page"], data["pages"], data["total"], data["per_page"]) == (1, 5, 23, 5), f"got {data}"


def test_links(client):
    data = client.get("/posts").get_json()
    assert data["next"] == "/posts?page=2&per_page=5", f"next link: build it with url_for('index', page=..., per_page=...); got {data['next']!r}"
    assert data["prev"] is None, "There is no page before page 1: prev is null."


def test_middle_page_has_both_links(client):
    data = client.get("/posts?page=3").get_json()
    assert data["items"] == ["Post 13", "Post 12", "Post 11", "Post 10", "Post 9"]
    assert data["prev"] == "/posts?page=2&per_page=5" and data["next"] == "/posts?page=4&per_page=5"


def test_last_page_is_shorter(client):
    data = client.get("/posts?page=5").get_json()
    assert data["items"] == ["Post 3", "Post 2", "Post 1"], f"The last page has the remaining 3 posts; got {data['items']}"
    assert data["next"] is None and data["prev"] == "/posts?page=4&per_page=5"


@pytest.mark.parametrize("query", ["?page=6", "?page=0", "?page=-1", "?page=99"])
def test_pages_out_of_range_are_404(client, query):
    r = client.get("/posts" + query)
    assert r.status_code == 404, f"/posts{query} is outside 1..5: 404 (db.paginate with error_out=True), got {r.status_code}."


def test_per_page_is_capped_at_20(client):
    data = client.get("/posts?per_page=100").get_json()
    assert data["per_page"] == 20 and len(data["items"]) == 20, f"Use max_per_page=20; got per_page={data['per_page']}, {len(data['items'])} items."
    assert data["pages"] == 2


def test_custom_per_page_is_kept_in_the_links(client):
    data = client.get("/posts?per_page=10").get_json()
    assert data["pages"] == 3 and data["next"] == "/posts?page=2&per_page=10"


def test_bad_page_text_means_page_one(client):
    data = client.get("/posts?page=abc").get_json()
    assert data["page"] == 1, "page=abc cannot be converted: use request.args.get('page', 1, type=int)."


def test_empty_table_first_page_is_fine():
    app = create_app({"TESTING": True})
    r = app.test_client().get("/posts")
    assert r.status_code == 200 and r.get_json()["items"] == [], "An empty list is a valid first page (200), not a 404."
