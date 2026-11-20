from datetime import timedelta

from flask import Flask, request, session


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=timedelta(days=14),
    )
    app.config.update(test_config or {})

    @app.post("/login")
    def login():
        session.clear()
        session["user"] = request.form.get("username", "")
        session.permanent = request.form.get("remember") == "on"
        return "ok"

    @app.post("/logout")
    def logout():
        session.clear()
        return "bye"

    return app
