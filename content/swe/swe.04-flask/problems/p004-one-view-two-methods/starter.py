from flask import Flask, request


def create_app():
    app = Flask(__name__)

    @app.route("/contact")             # TODO: this route accepts only GET
    def contact():
        if request.method == "POST":
            return "TODO"
        return '<form method="post"><input name="name"></form>'

    return app
