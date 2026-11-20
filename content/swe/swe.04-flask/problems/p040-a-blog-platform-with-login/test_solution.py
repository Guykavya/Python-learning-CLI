from urllib.parse import parse_qs, urlsplit

import pytest
from bs4 import BeautifulSoup
from sqlalchemy import event
from werkzeug.security import check_password_hash

from solution import Post, User, create_app, db

CONFIG = {"TESTING": True, "PROPAGATE_EXCEPTIONS": False, "PER_PAGE": 5, "HASH_METHOD": "pbkdf2:sha256:1000"}
PASSWORD = "password123"


@pytest.fixture
def app():
    return create_app(dict(CONFIG))


def soup(response):
    return BeautifulSoup(response.get_data(as_text=True), "html.parser")


def token(client, page):
    field = soup(client.get(page)).find("input", attrs={"name": "csrf_token"})
    assert field is not None, f"The page {page} must contain a hidden input named csrf_token (the forms of every page need one)."
    return field["value"]


def post(client, url, page=None, **data):
    """POST with a real CSRF token taken from a page (like a browser would)."""
    data["csrf_token"] = token(client, page or url)
    return client.post(url, data=data)


def register(client, name, password=PASSWORD):
    return post(client, "/auth/register", username=name, password=password, confirm=password)


def login(client, name, password=PASSWORD, next=None):
    url = "/auth/login" + (f"?next={next}" if next else "")
    return post(client, url, page="/auth/login", username=name, password=password)


def user_client(app, name):
    client = app.test_client()
    assert register(client, name).status_code == 302
    assert login(client, name).status_code == 302
    return client


def seed(app, count, authors=("seed",)):
    with app.app_context():
        users = []
        for name in authors:
            user = User(username=name, password_hash="x")
            db.session.add(user)
            users.append(user)
        db.session.flush()
        for i in range(1, count + 1):
            db.session.add(Post(title=f"Post {i}", body=f"Body {i}", user_id=users[i % len(users)].id))
        db.session.commit()


def post_count(app):
    with app.app_context():
        return db.session.scalar(db.select(db.func.count()).select_from(Post))


# --------------------------------------------------------------------------- structure
def test_blueprints_and_models(app):
    assert {"auth", "blog"} <= set(app.blueprints), f"Register the blueprints 'auth' and 'blog'; found {sorted(app.blueprints)}."


def test_empty_home_page(app):
    r = app.test_client().get("/")
    assert r.status_code == 200 and soup(r).select_one("li.empty").get_text(strip=True) == "No posts yet.", "An empty blog shows <li class='empty'>No posts yet.</li>."


# --------------------------------------------------------------------------- registration and login
@pytest.mark.parametrize("fields,count", [
    ({"username": "Bad Name", "password": PASSWORD, "confirm": PASSWORD}, 1),
    ({"username": "asha", "password": "short", "confirm": "short"}, 1),
    ({"username": "asha", "password": PASSWORD, "confirm": "different-one"}, 1),
    ({"username": "", "password": "", "confirm": ""}, 2),
])
def test_registration_validation(app, fields, count):
    client = app.test_client()
    r = post(client, "/auth/register", **fields)
    assert r.status_code == 200, f"An invalid registration shows the form again with status 200, got {r.status_code}."
    assert len(soup(r).select("p.error")) >= count, f"Show an error message in <p class='error'> for each problem ({fields})."
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(User)) == 0, "Nothing may be created for invalid input."


def test_the_registration_form_keeps_the_username_but_not_the_passwords(app):
    r = post(app.test_client(), "/auth/register", username="asha", password="short", confirm="short")
    s = soup(r)
    assert s.find("input", attrs={"name": "username"})["value"] == "asha"
    assert "short" not in str(s.find("input", attrs={"name": "password"}))


def test_registration_stores_a_hash(app):
    register(app.test_client(), "asha")
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.username == "asha"))
        assert user.password_hash != PASSWORD and check_password_hash(user.password_hash, PASSWORD), "Store generate_password_hash(...), never the password."
        assert user.password_hash.startswith("pbkdf2:sha256:1000"), "Use app.config['HASH_METHOD'] as the hashing method."


def test_registration_redirects_to_login_with_a_flash_message(app):
    client = app.test_client()
    r = register(client, "asha")
    assert r.status_code == 302 and r.headers["Location"] == "/auth/login", f"After registering, redirect to the login page; got {r.status_code} {r.headers.get('Location')}"
    assert "Account created" in client.get("/auth/login").get_data(as_text=True), "Flash 'Account created. Please log in.'"


def test_duplicate_username_is_a_form_error_and_the_app_keeps_working(app):
    client = app.test_client()
    register(client, "asha")
    r = register(client, "asha")
    assert r.status_code == 200 and "taken" in r.get_data(as_text=True), "A duplicate username shows 'That username is taken' (status 200)."
    assert register(client, "ravi").status_code == 302, "After the duplicate the next registration must still work (rollback!)."


def test_login_logout_flow(app):
    client = app.test_client()
    register(client, "asha")
    r = login(client, "asha")
    assert r.status_code == 302 and r.headers["Location"] == "/"
    home = soup(client.get("/"))
    assert home.select_one(".nav-user").get_text(strip=True) == "asha", "The navigation shows <span class='nav-user'>username</span> when logged in."
    r = post(client, "/auth/logout", page="/")
    assert r.status_code == 302 and r.headers["Location"] == "/"
    assert soup(client.get("/")).select_one(".nav-user") is None, "After logout the user name must be gone."


def test_login_failures_look_the_same(app):
    client = app.test_client()
    register(client, "asha")
    a = login(client, "asha", "wrong-password")
    b = login(client, "nobody", "wrong-password")
    assert a.status_code == b.status_code == 401, "A failed login answers 401."
    assert [p.get_text() for p in soup(a).select("p.error")] == [p.get_text() for p in soup(b).select("p.error")] == ["Invalid username or password"]
    assert soup(client.get("/")).select_one(".nav-user") is None


def test_login_next_is_followed_only_when_local(app):
    client = app.test_client()
    register(client, "asha")
    assert login(client, "asha", next="/new").headers["Location"] == "/new"
    other = app.test_client()
    assert login(other, "asha", next="https://evil.example/").headers["Location"] == "/", "Never redirect to another site after login (open redirect)."


def test_login_starts_a_fresh_session(app):
    client = app.test_client()
    register(client, "asha")
    with client.session_transaction() as s:
        s["planted"] = "x"
    login(client, "asha")
    with client.session_transaction() as s:
        assert "planted" not in s and "user_id" in s, "session.clear() before setting the user (session fixation)."


def test_session_cookie_flags(app):
    client = app.test_client()
    register(client, "asha")
    r = login(client, "asha")
    cookie = [h for h in r.headers.getlist("Set-Cookie") if h.startswith("session=")][-1]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie, f"Set SESSION_COOKIE_HTTPONLY and SESSION_COOKIE_SAMESITE='Lax'; got {cookie}"


# --------------------------------------------------------------------------- posts
def test_the_whole_story(app):
    client = user_client(app, "asha")
    r = post(client, "/new", title="  Hello  ", body="First post")
    assert r.status_code == 302 and r.headers["Location"] == "/post/1", f"Creating a post redirects to it; got {r.status_code} {r.headers.get('Location')}"
    page = soup(client.get("/post/1"))
    assert page.h1.get_text(strip=True) == "Hello", "The title is stored stripped and shown in the <h1>."
    assert page.select_one(".body").get_text(strip=True) == "First post"
    assert page.select_one(".author").get_text(strip=True) == "asha"
    assert page.select_one("a.edit") is not None and page.select_one("form.delete") is not None, "The author sees the Edit link and the Delete form."
    form = soup(client.get("/post/1/edit"))
    assert form.find("input", attrs={"name": "title"})["value"] == "Hello", "The edit form starts with the current values."
    r = post(client, "/post/1/edit", title="Hello again", body="Changed")
    assert r.status_code == 302 and r.headers["Location"] == "/post/1"
    assert soup(client.get("/post/1")).h1.get_text(strip=True) == "Hello again"
    r = post(client, "/post/1/delete", page="/post/1")
    assert r.status_code == 302 and r.headers["Location"] == "/"
    assert client.get("/post/1").status_code == 404, "A deleted post is a 404."
    assert post_count(app) == 0


def test_post_validation(app):
    client = user_client(app, "asha")
    for title in ("", "   ", "x" * 101):
        r = post(client, "/new", title=title, body="text")
        assert r.status_code == 200 and soup(r).select("p.error"), f"title {title[:10]!r}... must be refused with an error message."
        assert soup(r).find("textarea").get_text() == "text", "Keep the typed body in the form."
    assert post_count(app) == 0


def test_anonymous_cannot_create(app):
    client = app.test_client()
    r = client.get("/new")
    parts = urlsplit(r.headers.get("Location", ""))
    assert r.status_code == 302 and parts.path == "/auth/login" and parse_qs(parts.query) == {"next": ["/new"]}, "Anonymous visitors are sent to /auth/login?next=/new."
    r = post(client, "/new", page="/auth/login", title="x", body="y")
    assert r.status_code == 302 and post_count(app) == 0, "A valid-token POST by an anonymous visitor must still be refused (redirect to login)."


def test_only_the_author_may_edit_or_delete(app):
    asha = user_client(app, "asha")
    post(asha, "/new", title="Asha's post", body="mine")
    ravi = user_client(app, "ravi")
    assert ravi.get("/post/1/edit").status_code == 403, "Another user opening the edit page gets 403."
    r = post(ravi, "/post/1/edit", page="/new", title="Hacked", body="x")
    assert r.status_code == 403, f"Another user's edit must give 403, got {r.status_code}."
    r = post(ravi, "/post/1/delete", page="/new")
    assert r.status_code == 403 and post_count(app) == 1, "Another user's delete must give 403 and keep the post."
    page = soup(ravi.get("/post/1"))
    assert page.select_one("a.edit") is None and page.select_one("form.delete") is None, "Other users do not see Edit/Delete."
    with app.app_context():
        assert db.session.get(Post, 1).title == "Asha's post"


def test_missing_posts_are_404(app):
    client = user_client(app, "asha")
    assert client.get("/post/99").status_code == 404
    assert client.get("/post/99/edit").status_code == 404
    assert post(client, "/post/99/delete", page="/new").status_code == 404


def test_user_text_is_escaped(app):
    client = user_client(app, "asha")
    post(client, "/new", title="<script>alert(1)</script>", body="<img src=x onerror=alert(2)>")
    for url in ("/", "/post/1"):
        page = soup(client.get(url))
        assert page.find("script") is None and page.find("img") is None, f"{url}: user text must be escaped (no |safe)."
    assert "<script>alert(1)</script>" in soup(client.get("/post/1")).h1.get_text()


# --------------------------------------------------------------------------- CSRF
def test_every_post_needs_a_csrf_token(app):
    client = user_client(app, "asha")
    for url, data in (("/new", {"title": "x", "body": "y"}), ("/auth/logout", {})):
        assert client.post(url, data=data).status_code == 400, f"POST {url} without a CSRF token must give 400."
    assert soup(client.get("/")).select_one(".nav-user") is not None, "The failed logout must not log the user out."
    assert post_count(app) == 0
    post(client, "/new", title="x", body="y")
    r = client.post("/post/1/delete", data={"csrf_token": "wrong"})
    assert r.status_code == 400 and post_count(app) == 1, "A wrong token must not delete anything."
    anonymous = app.test_client()
    assert anonymous.post("/auth/login", data={"username": "asha", "password": PASSWORD}).status_code == 400, "Even the login form is protected."
    assert anonymous.post("/auth/register", data={"username": "ravi", "password": PASSWORD, "confirm": PASSWORD}).status_code == 400


# --------------------------------------------------------------------------- pages, queries, API, errors
def test_pagination(app):
    seed(app, 12)
    client = app.test_client()
    page1 = soup(client.get("/"))
    assert [li.a.get_text() for li in page1.select("li.post")] == ["Post 12", "Post 11", "Post 10", "Post 9", "Post 8"], "Newest first, PER_PAGE items."
    assert page1.select_one("a.next")["href"] == "/?page=2" and page1.select_one("a.prev") is None
    page3 = soup(client.get("/?page=3"))
    assert [li.a.get_text() for li in page3.select("li.post")] == ["Post 2", "Post 1"]
    assert page3.select_one("a.next") is None and page3.select_one("a.prev")["href"] == "/?page=2"
    assert client.get("/?page=4").status_code == 404, "A page past the end is a 404."


def test_home_page_runs_at_most_three_queries(app):
    seed(app, 30, authors=("one", "two", "three"))
    app.config["PER_PAGE"] = 30
    with app.app_context():
        statements = []
        event.listen(db.engine, "before_cursor_execute", lambda conn, cur, stmt, *a: statements.append(" ".join(stmt.split())))
    r = app.test_client().get("/")
    assert len(soup(r).select("li.post")) == 30
    assert len(statements) <= 3, f"The home page ran {len(statements)} statements for 30 posts (N+1?): load the authors together with the posts. First: {statements[:3]}"


def test_json_api(app):
    seed(app, 3, authors=("one", "two"))
    r = app.test_client().get("/api/posts")
    assert r.status_code == 200 and r.is_json
    items = r.get_json()["items"]
    assert [p["title"] for p in items] == ["Post 3", "Post 2", "Post 1"] and set(items[0]) == {"id", "title", "author"}, f"got {items}"


def test_errors_are_json_under_api_and_html_elsewhere(app):
    client = app.test_client()
    r = client.get("/api/nothing")
    assert r.status_code == 404 and r.mimetype == "application/json", f"Errors under /api/ are JSON, got {r.content_type}."
    assert r.get_json()["error"]["code"] == "not_found"
    r = client.get("/nothing")
    assert r.status_code == 404 and r.mimetype == "text/html" and "<h1>404 Not Found</h1>" in r.get_data(as_text=True)
    assert client.post("/new", data={}).status_code == 400
