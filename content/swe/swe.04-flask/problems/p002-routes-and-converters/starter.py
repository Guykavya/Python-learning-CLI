from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/user/<username>")
    def user_profile(username):
        return f"User: {username}"

    @app.route("/post/<post_id>")          # TODO: this accepts anything
    def show_post(post_id):
        return f"Post {post_id} ({type(post_id).__name__})"

    @app.route("/files/<subpath>")         # TODO: a plain converter stops at the next slash
    def show_file(subpath):
        return f"File: {subpath}"

    return app
