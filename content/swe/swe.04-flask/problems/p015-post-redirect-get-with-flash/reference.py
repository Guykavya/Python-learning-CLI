from flask import Flask, flash, redirect, render_template_string, request, url_for

FORM = """<h1>Feedback</h1>
{% for message in errors.values() %}<p class="error">{{ message }}</p>{% endfor %}
<form method="post">
<input name="name" value="{{ values.get('name', '') }}">
<textarea name="message">{{ values.get('message', '') }}</textarea>
<button>Send</button>
</form>"""

THANKS = """{% for message in get_flashed_messages() %}<p class="flash">{{ message }}</p>{% else %}Nothing to see{% endfor %}"""


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev")
    app.config.update(test_config or {})
    app.extensions["feedback"] = []

    @app.route("/feedback", methods=["GET", "POST"])
    def feedback():
        if request.method == "POST":
            values = {key: request.form.get(key, "").strip() for key in ("name", "message")}
            errors = {}
            if not values["name"]:
                errors["name"] = "Name is required"
            if len(values["message"]) < 10:
                errors["message"] = "Message must have at least 10 characters"
            if errors:
                return render_template_string(FORM, values=values, errors=errors)
            app.extensions["feedback"].append(values)
            flash(f"Thanks, {values['name']}!")
            return redirect(url_for("thanks"))
        return render_template_string(FORM, values={}, errors={})

    @app.get("/thanks")
    def thanks():
        return render_template_string(THANKS)

    return app
