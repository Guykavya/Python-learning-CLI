import datetime

from bs4 import BeautifulSoup

from solution import create_app

LONG = "Flask is a small framework that maps URLs to Python functions and lets you add what you need"


def page(posts):
    app = create_app({"TESTING": True, "POSTS": posts})
    r = app.test_client().get("/")
    assert r.status_code == 200, f"The home page must answer 200, got {r.status_code}."
    return BeautifulSoup(r.get_data(as_text=True), "html.parser")


def test_one_item_per_post_in_order():
    posts = [
        {"title": "first", "body": "a", "created": datetime.date(2026, 3, 5)},
        {"title": "second", "body": "b", "created": datetime.date(2026, 11, 19)},
    ]
    soup = page(posts)
    items = soup.select("li.post")
    assert len(items) == 2, f"Expected one <li class='post'> per post, found {len(items)}."
    assert [li.h2.get_text(strip=True) for li in items] == ["First", "Second"]


def test_title_filter():
    soup = page([{"title": "hello WORLD of flask", "body": "x", "created": datetime.date(2026, 1, 1)}])
    assert soup.select_one("li.post h2").get_text(strip=True) == "Hello World Of Flask", "Use {{ post.title|title }}."


def test_date_format():
    soup = page([{"title": "t", "body": "x", "created": datetime.date(2026, 3, 5)}])
    assert soup.select_one("li.post time").get_text(strip=True) == "05 Mar 2026", "Use post.created.strftime('%d %b %Y') inside a <time> element."


def test_truncate_filter():
    soup = page([{"title": "t", "body": LONG, "created": datetime.date(2026, 1, 1)}])
    summary = soup.select_one("li.post p.summary").get_text(strip=True)
    assert summary == "Flask is a small framework that maps...", f"Use {{{{ post.body|truncate(40) }}}}; got {summary!r}."


def test_short_body_is_not_cut():
    soup = page([{"title": "t", "body": "short text", "created": datetime.date(2026, 1, 1)}])
    assert soup.select_one("p.summary").get_text(strip=True) == "short text"


def test_empty_list_uses_else_branch():
    soup = page([])
    assert soup.select("li.post") == [], "With no posts there must be no li.post items."
    empty = soup.select("li.empty")
    assert len(empty) == 1 and empty[0].get_text(strip=True) == "No posts yet.", "Add {% else %}<li class='empty'>No posts yet.</li> to the for loop."


def test_list_with_posts_has_no_empty_message():
    soup = page([{"title": "t", "body": "x", "created": datetime.date(2026, 1, 1)}])
    assert soup.select("li.empty") == [], "The else branch of a for loop runs only when the list is empty."


def test_user_text_is_escaped():
    soup = page([{"title": "<script>alert(1)</script>", "body": "<b>bold</b>", "created": datetime.date(2026, 1, 1)}])
    assert soup.find("script") is None, "The title must be escaped: never use |safe on user text."
    assert soup.select_one("p.summary b") is None
    assert "<script>" in soup.select_one("h2").get_text().lower(), "The escaped text is shown as visible characters."
