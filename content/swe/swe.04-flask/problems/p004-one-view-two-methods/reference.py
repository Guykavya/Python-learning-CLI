from flask import Flask, request
from markupsafe import escape


def create_app():
    app = Flask(__name__)

    @app.route("/contact", methods=["GET", "POST"])
    def contact():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            if not name:
                return "Name is required", 400
            return f"Thanks, {escape(name)}!"
        return '<form method="post"><input name="name"><button>Send</button></form>'

    return app
