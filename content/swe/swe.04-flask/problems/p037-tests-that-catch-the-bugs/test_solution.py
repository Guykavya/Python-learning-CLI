import secrets

from flask import Flask, abort, jsonify, request, session


def build_app(bug=None):
    """The app that your checks are run against. `bug` selects one deliberately broken version."""
    app = Flask(__name__)
    app.config.update(SECRET_KEY="test", TESTING=True)
    passwords = {"asha": "pw-asha", "ravi": "pw-ravi"}
    posts = {}

    @app.before_request
    def csrf_guard():
        if request.method != "POST" or bug == "csrf_not_checked":
            return
        sent = request.form.get("csrf_token", "")
        if bug == "csrf_value_ignored":
            valid = bool(sent)
        else:
            valid = bool(sent) and sent == session.get("csrf")
        if not valid:
            abort(400)

    @app.get("/csrf")
    def csrf():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(8)
        return session["csrf"]

    @app.post("/login")
    def login():
        user, password = request.form.get("username"), request.form.get("password")
        if user not in passwords or (bug != "any_password" and passwords[user] != password):
            return "bad login", 401
        session.clear()
        session["user"] = user
        return "ok"

    @app.post("/posts")
    def create_post():
        if "user" not in session:
            return "login required", 401
        post_id = len(posts) + 1
        posts[post_id] = {"owner": session["user"], "title": request.form.get("title", "")}
        return jsonify(id=post_id), 201

    @app.post("/posts/<int:post_id>/delete")
    def delete_post(post_id):
        if "user" not in session:
            return "login required", 401
        post = posts.get(post_id)
        if post is None:
            return "not found", 404
        if bug != "no_owner_check" and post["owner"] != session["user"]:
            return "forbidden", 403
        del posts[post_id]
        return "", 204

    return app


import pytest

from solution import check_csrf, check_login, check_owner_only

ALL_CHECKS = [check_login, check_csrf, check_owner_only]


def run(check, bug=None):
    app = build_app(bug)                        # a fresh app for every run
    check(lambda: app.test_client())


@pytest.mark.parametrize("check", ALL_CHECKS, ids=lambda c: c.__name__)
def test_checks_pass_on_the_correct_app(check):
    run(check)                                  # must not raise: a check that fails here is wrong or too strict


@pytest.mark.parametrize("check,bug,what", [
    (check_csrf, "csrf_not_checked", "the app accepts a POST with no CSRF token"),
    (check_csrf, "csrf_value_ignored", "the app accepts ANY token, even a wrong one (test a wrong token too)"),
    (check_owner_only, "no_owner_check", "any logged-in user can delete another user's post"),
    (check_login, "any_password", "a wrong password is accepted at login"),
], ids=lambda v: v if isinstance(v, str) and "_" in v and " " not in v else None)
def test_each_check_catches_its_bug(check, bug, what):
    try:
        run(check, bug)
    except AssertionError:
        return                                  # the check failed on the broken app, as it should
    pytest.fail(f"{check.__name__} did not fail on the broken app '{bug}': {what}. Add an assert that this bug would break.")


def test_checks_do_not_swallow_assertions():
    class Always403Client:
        def __getattr__(self, name):
            raise AssertionError("not used")

    for check in ALL_CHECKS:
        with pytest.raises(Exception):
            check(lambda: Always403Client())
