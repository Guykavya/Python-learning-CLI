from flask import Flask, render_template_string, request

FORM = """<form method="post" action="/deposit">
<input name="amount"> <button>Deposit</button>
</form>"""


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")
    app.config.update(test_config or {})
    bank = app.extensions["bank"] = {"balance": 0}

    @app.get("/form")
    def form():
        return render_template_string(FORM)      # TODO: the token must be in the form

    @app.post("/deposit")
    def deposit():
        amount = request.form.get("amount", type=int, default=0)
        bank["balance"] += amount
        return f"Deposited {amount}"

    @app.get("/balance")
    def balance():
        return str(bank["balance"])

    # TODO: csrf_token() helper, Jinja global, before_request check

    return app
