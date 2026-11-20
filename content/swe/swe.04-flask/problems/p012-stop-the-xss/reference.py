import re

import jinja2
from flask import Flask, render_template
from markupsafe import Markup, escape

TEMPLATES = {
    "index.html": """<!doctype html>
{% for c in comments %}
<div class="comment"><b class="author">{{ c.author }}</b><div class="text">{{ c.text|comment_html }}</div></div>
{% endfor %}
""",
}

BOLD = re.compile(r"\*\*(.+?)\*\*")


def format_comment(text):
    safe = str(escape(text))                              # 1. neutralise the user's HTML
    safe = BOLD.sub(r"<strong>\1</strong>", safe)         # 2. now add our own tags
    safe = safe.replace("\n", "<br>")
    return Markup(safe)                                   # 3. tell Jinja it is already safe


def create_app(test_config=None):
    app = Flask(__name__)
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)
    app.jinja_env.filters["comment_html"] = format_comment
    app.config["COMMENTS"] = []
    app.config.update(test_config or {})

    @app.get("/")
    def index():
        return render_template("index.html", comments=app.config["COMMENTS"])

    return app
