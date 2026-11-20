import functools

from flask import Flask, abort, current_app, g, redirect, request, session, url_for

USERS = {1: {"id": 1, "name": "asha"}, 2: {"id": 2, "name": "ravi"}}


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def get_post_for_edit(post_id):
    return current_app.extensions["posts"][post_id]      # TODO: 404 and 403


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")
    app.config.update(test_config or {})
    app.extensions["posts"] = {
        1: {"id": 1, "title": "Asha's post", "author_id": 1},
        2: {"id": 2, "title": "Ravi's post", "author_id": 2},
    }

    @app.before_request
    def load_user():
        g.user = USERS.get(session.get("user_id"))

    @app.get("/auth/login")
    def login():
        return "login page"

    @app.get("/posts/<int:post_id>")
    def show(post_id):
        post = current_app.extensions["posts"].get(post_id)
        if post is None:
            abort(404)
        return post["title"]

    @app.post("/posts/<int:post_id>/edit")
    @login_required
    def edit(post_id):
        post = get_post_for_edit(post_id)
        title = request.form.get("title", "").strip()
        if not title:
            abort(400)
        post["title"] = title
        return "updated"

    @app.post("/posts/<int:post_id>/delete")
    @login_required
    def delete(post_id):
        post = get_post_for_edit(post_id)
        del current_app.extensions["posts"][post["id"]]
        return "", 204

    return app
