import jinja2
from flask import (Blueprint, Flask, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
import functools
import hmac
import re
import secrets
from urllib.parse import urlsplit

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, joinedload, mapped_column
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

USERNAME = re.compile(r"[a-z0-9_]{3,20}")
DUMMY_HASH = generate_password_hash("not-a-real-password", method="pbkdf2:sha256:1000")


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


TEMPLATES = {
    "base.html": """<!doctype html>
<title>{% block title %}Blog{% endblock %}</title>
<nav>
  <a href="{{ url_for('blog.index') }}">Home</a>
  {% if g.user %}
    <a href="{{ url_for('blog.new') }}">New post</a>
    <span class="nav-user">{{ g.user.username }}</span>
    <form method="post" action="{{ url_for('auth.logout') }}" class="logout">
      <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"><button>Log out</button>
    </form>
  {% else %}
    <a href="{{ url_for('auth.login') }}">Log in</a>
    <a href="{{ url_for('auth.register') }}">Register</a>
  {% endif %}
</nav>
{% for message in get_flashed_messages() %}<p class="flash">{{ message }}</p>{% endfor %}
{% block content %}{% endblock %}
""",
    "index.html": """{% extends "base.html" %}
{% block content %}
<h1>Posts</h1>
<ul>
{% for post in pagination.items %}
  <li class="post"><a href="{{ url_for('blog.show', post_id=post.id) }}">{{ post.title }}</a> by <span class="author">{{ post.author.username }}</span></li>
{% else %}
  <li class="empty">No posts yet.</li>
{% endfor %}
</ul>
<p class="pages">
{% if pagination.has_prev %}<a class="prev" href="{{ url_for('blog.index', page=pagination.prev_num) }}">Newer</a>{% endif %}
{% if pagination.has_next %}<a class="next" href="{{ url_for('blog.index', page=pagination.next_num) }}">Older</a>{% endif %}
</p>
{% endblock %}
""",
    "post.html": """{% extends "base.html" %}
{% block content %}
<h1>{{ post.title }}</h1>
<p>by <span class="author">{{ post.author.username }}</span></p>
<div class="body">{{ post.body }}</div>
{% if g.user and g.user.id == post.user_id %}
<p><a class="edit" href="{{ url_for('blog.edit', post_id=post.id) }}">Edit</a></p>
<form method="post" action="{{ url_for('blog.delete', post_id=post.id) }}" class="delete">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"><button>Delete</button>
</form>
{% endif %}
{% endblock %}
""",
    "post_form.html": """{% extends "base.html" %}
{% block content %}
<h1>{{ heading }}</h1>
{% for message in errors.values() %}<p class="error">{{ message }}</p>{% endfor %}
<form method="post">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input name="title" value="{{ values.get('title', '') }}">
  <textarea name="body">{{ values.get('body', '') }}</textarea>
  <button>Save</button>
</form>
{% endblock %}
""",
    "login.html": """{% extends "base.html" %}
{% block content %}
<h1>Log in</h1>
{% for message in errors.values() %}<p class="error">{{ message }}</p>{% endfor %}
<form method="post">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input name="username" value="{{ values.get('username', '') }}">
  <input name="password" type="password">
  <button>Log in</button>
</form>
{% endblock %}
""",
    "register.html": """{% extends "base.html" %}
{% block content %}
<h1>Register</h1>
{% for message in errors.values() %}<p class="error">{{ message }}</p>{% endfor %}
<form method="post">
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
  <input name="username" value="{{ values.get('username', '') }}">
  <input name="password" type="password">
  <input name="confirm" type="password">
  <button>Create account</button>
</form>
{% endblock %}
""",
    "error.html": """{% extends "base.html" %}
{% block content %}<h1>{{ status }} {{ name }}</h1><p><a href="/">Back to the home page</a></p>{% endblock %}
""",
}

auth = Blueprint("auth", __name__, url_prefix="/auth")
blog = Blueprint("blog", __name__)


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def safe_next(target):
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return "/"
    parts = urlsplit(target)
    return "/" if parts.scheme or parts.netloc else target


def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def get_post_for_edit(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404)
    if g.user is None or post.user_id != g.user.id:
        abort(403)
    return post


def validate_post(form):
    values = {"title": form.get("title", "").strip(), "body": form.get("body", "").strip()}
    errors = {}
    if not values["title"]:
        errors["title"] = "Title is required"
    elif len(values["title"]) > 100:
        errors["title"] = "Title must have at most 100 characters"
    return values, errors


# ----------------------------------------------------------------- auth
@auth.route("/register", methods=["GET", "POST"])
def register():
    values, errors = {}, {}
    if request.method == "POST":
        values = {"username": request.form.get("username", "").strip()}
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        if not USERNAME.fullmatch(values["username"]):
            errors["username"] = "Username: 3 to 20 characters, a-z, 0-9 and _"
        if len(password) < 8:
            errors["password"] = "Password must have at least 8 characters"
        elif password != confirm:
            errors["confirm"] = "The passwords do not match"
        if not errors:
            user = User(username=values["username"],
                        password_hash=generate_password_hash(password, method=current_app.config["HASH_METHOD"]))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors["username"] = "That username is taken"
            else:
                flash("Account created. Please log in.")
                return redirect(url_for("auth.login"))
    return render_template("register.html", values=values, errors=errors)


@auth.route("/login", methods=["GET", "POST"])
def login():
    values, errors = {}, {}
    if request.method == "POST":
        values = {"username": request.form.get("username", "").strip()}
        password = request.form.get("password", "")
        user = db.session.scalar(db.select(User).where(User.username == values["username"]))
        stored = user.password_hash if user else DUMMY_HASH
        if not (check_password_hash(stored, password) and user):
            errors["login"] = "Invalid username or password"
            return render_template("login.html", values=values, errors=errors), 401
        session.clear()
        session["user_id"] = user.id
        flash(f"Welcome, {user.username}!")
        return redirect(safe_next(request.args.get("next")))
    return render_template("login.html", values=values, errors=errors)


@auth.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("blog.index"))


# ----------------------------------------------------------------- blog
@blog.get("/")
def index():
    page = request.args.get("page", 1, type=int)
    pagination = db.paginate(
        db.select(Post).options(joinedload(Post.author)).order_by(Post.id.desc()),
        page=page, per_page=current_app.config["PER_PAGE"], error_out=True)
    return render_template("index.html", pagination=pagination)


@blog.get("/post/<int:post_id>")
def show(post_id):
    post = db.get_or_404(Post, post_id)
    return render_template("post.html", post=post)


@blog.route("/new", methods=["GET", "POST"])
@login_required
def new():
    values, errors = {}, {}
    if request.method == "POST":
        values, errors = validate_post(request.form)
        if not errors:
            post = Post(title=values["title"], body=values["body"], user_id=g.user.id)
            db.session.add(post)
            db.session.commit()
            flash("Post created.")
            return redirect(url_for("blog.show", post_id=post.id))
    return render_template("post_form.html", heading="New post", values=values, errors=errors)


@blog.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = get_post_for_edit(post_id)
    values, errors = {"title": post.title, "body": post.body}, {}
    if request.method == "POST":
        values, errors = validate_post(request.form)
        if not errors:
            post.title, post.body = values["title"], values["body"]
            db.session.commit()
            flash("Post updated.")
            return redirect(url_for("blog.show", post_id=post.id))
    return render_template("post_form.html", heading="Edit post", values=values, errors=errors)


@blog.post("/post/<int:post_id>/delete")
@login_required
def delete(post_id):
    post = get_post_for_edit(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.")
    return redirect(url_for("blog.index"))


@blog.get("/api/posts")
def api_posts():
    posts = db.session.scalars(
        db.select(Post).options(joinedload(Post.author)).order_by(Post.id.desc()).limit(20)).all()
    return jsonify(items=[{"id": p.id, "title": p.title, "author": p.author.username} for p in posts])


# ----------------------------------------------------------------- factory
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite://",
        PER_PAGE=5,
        HASH_METHOD="scrypt",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    app.config.update(test_config or {})
    app.jinja_loader = jinja2.DictLoader(TEMPLATES)
    app.jinja_env.globals["csrf_token"] = csrf_token
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(auth)
    app.register_blueprint(blog)

    @app.before_request
    def load_user_and_check_csrf():
        user_id = session.get("user_id")
        g.user = db.session.get(User, user_id) if user_id else None
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            sent = request.form.get("csrf_token", "")
            expected = session.get("csrf_token", "")
            if not sent or not expected or not hmac.compare_digest(sent.encode(), expected.encode()):
                abort(400, description="Bad or missing CSRF token.")

    def error_response(status, name):
        if request.path.startswith("/api/"):
            response = jsonify(error={"code": name.lower().replace(" ", "_"), "message": name})
            response.status_code = status
            return response
        return render_template("error.html", status=status, name=name), status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return error_response(error.code, error.name)

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception("unhandled exception on %s", request.path)
        return error_response(500, "Internal Server Error")

    return app
