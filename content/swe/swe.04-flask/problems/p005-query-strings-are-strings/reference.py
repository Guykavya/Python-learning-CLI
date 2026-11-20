from flask import Flask, jsonify, request


def create_app():
    app = Flask(__name__)

    @app.get("/items")
    def items():
        page = max(1, request.args.get("page", 1, type=int))
        per_page = min(100, max(1, request.args.get("per_page", 20, type=int)))
        return jsonify(page=page, per_page=per_page, offset=(page - 1) * per_page)

    return app
