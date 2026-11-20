import jinja2
from flask import Flask, render_template, request

TEMPLATES = {
    "macros.html": """{% macro render_field(name, label, value="", errors=(), type="text") -%}
<div class="field">
  <label for="{{ name }}">{{ label }}</label>
  <input id="{{ name }}" name="{{ name }}" type="{{ type }}"
    {%- if type != "password" %} value="{{ value or '' }}"{% endif %}
    {%- if errors %} aria-invalid="true" aria-describedby="{{ name }}-errors"{% endif %}>
  {%- if errors %}
  <ul class="errors" id="{{ name }}-errors">
    {%- for error in errors %}
    <li>{{ error }}</li>
    {%- endfor %}
  </ul>
  {%- endif %}
</div>
{%- endmacro %}""",
    "signup.html": """{% from "macros.html" import render_field %}<!doctype html>
<form method="post">
{{ render_field("email", "Email", values.email, errors.email) }}
{{ render_field("password", "Password", values.password, errors.password, type="password") }}
<button>Sign up</button>
</form>
""",
}


def create_app(test_config=None):
    app = Flask(__name__)
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)
    app.config.update(test_config or {})

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        values, errors = {}, {}
        if request.method == "POST":
            values = request.form.to_dict()
            if "@" not in values.get("email", ""):
                errors["email"] = ["Not a valid address"]
            if len(values.get("password", "")) < 8:
                errors["password"] = ["Use at least 8 characters"]
        return render_template("signup.html", values=values, errors=errors)

    return app
