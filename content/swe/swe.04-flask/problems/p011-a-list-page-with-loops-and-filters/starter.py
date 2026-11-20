import jinja2
from flask import Flask, render_template

TEMPLATES = {
    "index.html": """<!doctype html>
<h1>Posts</h1>
<ul>
{% for post in posts %}
  <li class="post">
    <h2>{{ post.title }}</h2>
    {{ post.created }}
    <p class="summary">{{ post.body }}</p>
  </li>
{% endfor %}
</ul>
""",
}


def create_app(test_config=None):
    app = Flask(__name__)
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)
    app.config["POSTS"] = []
    app.config.update(test_config or {})

    @app.get("/")
    def index():
        return render_template("index.html", posts=app.config["POSTS"])

    return app
