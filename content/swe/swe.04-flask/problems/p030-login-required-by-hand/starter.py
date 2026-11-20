import functools

from flask import Flask, g, redirect, request, session, url_for

USERS = {1: {"id": 1, "name": "asha"}, 2: {"id": 2, "name": "ravi"}}


def login_required(view):
    return view                                   # TODO: protect the view


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")
    app.config.update(test_config or {})

    # TODO: before_request hook load_user -> g.user

    @app.get("/")
    def home():
        return "home"

    @app.get("/auth/login")
    def login():
        return "login page"

    @app.get("/dashboard")
    @login_required
    def dashboard():
        return f"Dashboard of {g.user['name']}"

    @app.get("/settings")
    @login_required
    def settings():
        return f"Settings of {g.user['name']}"

    @app.get("/posts/<int:post_id>/private")
    @login_required
    def private_post(post_id):
        return f"Private post {post_id} for {g.user['name']}"

    return app
