from flask import Flask, g


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})

    @app.get("/whoami")
    def whoami():
        return g.request_id          # TODO: nothing sets it yet

    # TODO: before_request that sets g.request_id
    # TODO: after_request that adds the three headers

    return app
