from datetime import timedelta

from flask import Flask, request, session


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")          # TODO: cookie flags and lifetime
    app.config.update(test_config or {})

    @app.post("/login")
    def login():
        session["user"] = request.form.get("username", "")
        session.permanent = True                  # TODO: only when 'remember' is ticked
        return "ok"

    @app.post("/logout")
    def logout():
        session.clear()
        return "bye"

    return app
