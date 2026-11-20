from flask import Flask, make_response, request


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(CORS_ORIGINS=["https://app.example"])
    app.config.update(test_config or {})

    def is_preflight():
        return (request.method == "OPTIONS" and "Origin" in request.headers
                and "Access-Control-Request-Method" in request.headers)

    @app.before_request
    def answer_preflight():
        if request.path.startswith("/api/") and is_preflight():
            return make_response("", 204)

    @app.after_request
    def add_cors_headers(response):
        if not request.path.startswith("/api/"):
            return response
        response.headers.add("Vary", "Origin")
        origin = request.headers.get("Origin")
        if origin and origin in app.config["CORS_ORIGINS"]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            if is_preflight():
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE"
                response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
                response.headers["Access-Control-Max-Age"] = "600"
        return response

    @app.get("/api/ping")
    def api_ping():
        return "pong"

    @app.get("/ping")
    def ping():
        return "pong"

    return app
