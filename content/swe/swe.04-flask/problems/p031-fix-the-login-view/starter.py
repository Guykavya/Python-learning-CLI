from urllib.parse import urlsplit

from flask import Flask, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

USERS = {
    "asha": generate_password_hash("correct horse", method="pbkdf2:sha256:1000"),
    "ravi": generate_password_hash("battery staple", method="pbkdf2:sha256:1000"),
}
DUMMY_HASH = generate_password_hash("not-a-real-password", method="pbkdf2:sha256:1000")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")
    app.config.update(test_config or {})

    @app.get("/")
    def home():
        return f"Hello {session['user']}" if "user" in session else "Hello anonymous"

    @app.route("/auth/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            if username not in USERS:
                return "No such user", 401                                   # BUG 1
            if not check_password_hash(USERS[username], password):
                return "Wrong password", 401                                 # BUG 1
            session["user"] = username                                       # BUG 2
            return redirect(request.args.get("next") or "/")                 # BUG 3
        return "login form"

    return app
