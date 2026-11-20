from flask import Blueprint, Flask, abort, redirect, url_for

POSTS = {1: "Hello", 2: "Flask"}

auth = Blueprint("auth", __name__, url_prefix="/auth")
blog = Blueprint("blog", __name__)


@auth.get("/login")
def login():
    return "login page"


@auth.post("/logout")
def logout():
    return redirect(url_for("blog.index"))


@auth.get("/profile/<name>")
def profile(name):
    if name != "asha":
        abort(404)
    return f"profile {name}"


@auth.errorhandler(404)
def auth_not_found(error):
    return "auth 404", 404


@blog.get("/")
def index():
    return "home"


@blog.get("/post/<int:post_id>")
def show(post_id):
    if post_id not in POSTS:
        abort(404)
    return POSTS[post_id]


@blog.errorhandler(404)
def blog_not_found(error):
    return "blog 404", 404


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(blog)

    @app.errorhandler(404)
    def app_not_found(error):
        return "app 404", 404

    return app
