from flask import Blueprint, Flask, abort, redirect, url_for

POSTS = {1: "Hello", 2: "Flask"}

auth = Blueprint("auth", __name__, url_prefix="/auth")
blog = Blueprint("blog", __name__)


@auth.get("/login")
def login():
    return "login page"


# TODO: logout, profile, the blog routes and the three 404 handlers


def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    # TODO: blog, app-level 404
    return app
