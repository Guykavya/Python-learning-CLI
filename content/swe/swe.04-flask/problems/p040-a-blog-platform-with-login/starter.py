import jinja2
from flask import (Blueprint, Flask, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(256))


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100))
    body: Mapped[str] = mapped_column(db.Text, default="")
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"))
    author: Mapped["User"] = db.relationship()


# Templates live here, because the exercise runner copies only .py files (a real project has templates/).
TEMPLATES = {
    "base.html": """<!doctype html>
<title>Blog</title>
{% block content %}{% endblock %}
""",
    # TODO: index.html, post.html, post_form.html, login.html, register.html, error.html
}

auth = Blueprint("auth", __name__, url_prefix="/auth")
blog = Blueprint("blog", __name__)

# TODO: csrf_token(), safe_next(), login_required, get_post_for_edit()
# TODO: auth routes: register, login, logout
# TODO: blog routes: index (paginated), show, new, edit, delete, /api/posts


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="dev", SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    # TODO: config defaults, blueprints, before_request (g.user + CSRF), error handlers
    return app
