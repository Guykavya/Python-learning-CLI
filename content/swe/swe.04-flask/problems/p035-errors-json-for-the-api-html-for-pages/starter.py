from flask import Flask, abort, jsonify, request


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})

    @app.get("/")
    def home():
        return "home"

    @app.get("/api/items")
    def items():
        return jsonify(items=[])

    @app.get("/boom")
    @app.get("/api/boom")
    def boom():
        raise RuntimeError("db password is hunter2")

    @app.get("/api/forbidden")
    def forbidden():
        abort(403)

    # TODO: error handlers

    return app
