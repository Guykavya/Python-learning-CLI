from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)

    @app.get("/items")
    def items():
        page = request.args.get("page", "1")           # TODO: these are strings
        per_page = request.args.get("per_page", "20")
        return jsonify(page=page, per_page=per_page, offset=0)

    return app
