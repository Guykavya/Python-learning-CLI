import hmac
import secrets

from flask import Flask, abort, render_template_string, request, session

FORM = """<form method="post" action="/deposit">
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
<input name="amount"> <button>Deposit</button>
</form>"""

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")
    app.config.update(test_config or {})
    bank = app.extensions["bank"] = {"balance": 0}

    def csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        return session["csrf_token"]

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def check_csrf():
        if request.method in SAFE_METHODS:
            return
        sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
        expected = session.get("csrf_token", "")
        if not sent or not expected or not hmac.compare_digest(sent.encode(), expected.encode()):
            abort(400, description="Bad or missing CSRF token.")

    @app.get("/form")
    def form():
        return render_template_string(FORM)

    @app.post("/deposit")
    def deposit():
        amount = request.form.get("amount", type=int, default=0)
        bank["balance"] += amount
        return f"Deposited {amount}"

    @app.get("/balance")
    def balance():
        return str(bank["balance"])

    return app
