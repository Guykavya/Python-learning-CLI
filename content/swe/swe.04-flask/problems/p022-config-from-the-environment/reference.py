from flask import Flask, jsonify


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(PER_PAGE=10, TITLE="My Blog", DEBUG=False, FEATURES={"beta": False}, SECRET_KEY="dev")
    app.config.from_prefixed_env("BLOG")
    app.config.update(test_config or {})

    @app.get("/settings")
    def settings():
        c = app.config
        return jsonify(per_page=c["PER_PAGE"], title=c["TITLE"], debug=c["DEBUG"], features=c["FEATURES"])

    return app
