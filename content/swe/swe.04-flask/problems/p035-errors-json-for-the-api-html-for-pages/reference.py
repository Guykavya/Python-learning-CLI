from flask import Flask, abort, jsonify, render_template_string, request
from werkzeug.exceptions import HTTPException

PAGE = """<!doctype html>
<h1>{{ status }} {{ name }}</h1>
<p><a href="/">Back to the home page</a></p>"""


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})

    def error_response(status, name, allow=None):
        if request.path.startswith("/api/"):
            response = jsonify(error={"code": name.lower().replace(" ", "_"), "message": name})
            response.status_code = status
        else:
            response = app.make_response((render_template_string(PAGE, status=status, name=name), status))
        if allow:
            response.headers["Allow"] = allow
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        allow = error.get_response().headers.get("Allow")
        return error_response(error.code, error.name, allow)

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.exception("unhandled exception on %s", request.path)    # the details go to the log
        return error_response(500, "Internal Server Error")

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

    return app
