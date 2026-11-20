import re
import uuid

from flask import Flask, g, request

VALID_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})

    @app.before_request
    def set_request_id():
        incoming = request.headers.get("X-Request-ID", "")
        g.request_id = incoming if VALID_ID.fullmatch(incoming) else uuid.uuid4().hex

    @app.after_request
    def add_headers(response):
        response.headers["X-Request-ID"] = g.get("request_id", "")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        return response

    @app.get("/whoami")
    def whoami():
        return g.request_id

    return app
