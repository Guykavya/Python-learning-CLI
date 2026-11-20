from collections import Counter

import pytest
from sqlalchemy import event

from solution import Comment, Post, User, create_app, db


class QueryLog:
    def __init__(self, engine):
        self.statements = []
        event.listen(engine, "before_cursor_execute", self._record)

    def _record(self, conn, cursor, statement, parameters, context, executemany):
        self.statements.append(" ".join(statement.split()))

    def report(self):
        common = Counter(self.statements).most_common(1)
        return f"{len(self.statements)} statements; most repeated ({common[0][1]}x): {common[0][0][:90]}" if common else "no statements"


def seed(app, count):
    with app.app_context():
        users = [User(username=f"user{i}") for i in range(1, count + 1)]
        db.session.add_all(users)
        db.session.flush()
        for i, user in enumerate(users, 1):
            post = Post(title=f"Post {i}", user_id=user.id)
            post.comments = [Comment(text=f"c{j}") for j in range(i % 4)]
            db.session.add(post)
        db.session.commit()


def expected(count):
    return [{"title": f"Post {i}", "author": f"user{i}", "comments": i % 4} for i in range(count, 0, -1)]


@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    seed(app, 30)
    return app


def test_same_answer_as_before(app):
    r = app.test_client().get("/")
    assert r.status_code == 200
    assert r.get_json() == expected(30), "The JSON must be unchanged: newest first, author name, number of comments (0 when there are none)."


def test_at_most_three_queries(app):
    with app.app_context():
        log = QueryLog(db.engine)
    r = app.test_client().get("/")
    assert r.get_json() == expected(30)
    assert len(log.statements) <= 3, f"The page must run at most 3 statements for 30 posts (it ran {log.report()}). Load authors and comment counts together with the posts."


def test_query_count_does_not_grow_with_the_data():
    small, large = create_app({"TESTING": True}), create_app({"TESTING": True})
    seed(small, 3)
    seed(large, 40)
    counts = []
    for app in (small, large):
        with app.app_context():
            log = QueryLog(db.engine)
        app.test_client().get("/")
        counts.append(len(log.statements))
    assert counts[0] == counts[1], f"3 posts ran {counts[0]} statements and 40 posts ran {counts[1]}: the number of queries must not depend on the number of posts (N+1)."


def test_posts_without_comments_are_listed(app):
    data = app.test_client().get("/").get_json()
    assert any(p["comments"] == 0 for p in data), "Posts with no comments must still appear, with 0 (use an OUTER join or len())."
    assert len(data) == 30, "A plain INNER JOIN to the comments would drop the posts without comments."


def test_empty_blog():
    app = create_app({"TESTING": True})
    assert app.test_client().get("/").get_json() == []
