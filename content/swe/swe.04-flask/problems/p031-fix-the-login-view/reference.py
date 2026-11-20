from urllib.parse import urlsplit

from flask import Flask, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

USERS = {
    "asha": generate_password_hash("correct horse", method="pbkdf2:sha256:1000"),
    "ravi": generate_password_hash("battery staple", method="pbkdf2:sha256:1000"),
}
DUMMY_HASH = generate_password_hash("not-a-real-password", method="pbkdf2:sha256:1000")


def safe_next(target):
    """Return target only if it is a plain local path; otherwise '/'."""
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return "/"
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return "/"
    return target


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
            stored = USERS.get(username, DUMMY_HASH)              # same work for unknown users
            valid = check_password_hash(stored, password) and username in USERS
            if not valid:
                return "Invalid username or password", 401
            session.clear()                                        # a new session for the new login
            session["user"] = username
            return redirect(safe_next(request.args.get("next")))
        return "login form"

    return app
