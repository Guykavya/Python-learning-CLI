from flask import Flask, make_response, request


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(CORS_ORIGINS=["https://app.example"])
    app.config.update(test_config or {})

    @app.get("/api/ping")
    def api_ping():
        return "pong"

    @app.get("/ping")
    def ping():
        return "pong"

    # TODO: preflight answer and the after_request that adds the CORS headers

    return app
