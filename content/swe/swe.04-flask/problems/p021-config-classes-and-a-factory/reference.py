import copy
import os

from flask import Flask, jsonify


class Config:
    SECRET_KEY = "change-me"
    DEBUG = False
    TESTING = False
    PER_PAGE = 10
    FEATURES = {"beta": False}


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "dev-key"


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "test-key"


class ProductionConfig(Config):
    pass


CONFIGS = {"development": DevelopmentConfig, "testing": TestingConfig, "production": ProductionConfig}


def create_app(name="development"):
    if name not in CONFIGS:
        raise ValueError(f"unknown configuration {name!r}; choose one of {sorted(CONFIGS)}")
    config_class = CONFIGS[name]
    app = Flask(__name__)
    values = {key: getattr(config_class, key) for key in dir(config_class) if key.isupper()}
    app.config.from_mapping(copy.deepcopy(values))
    if name == "production":
        key = os.environ.get("SECRET_KEY", "")
        if not key or key == Config.SECRET_KEY:
            raise RuntimeError("Set the SECRET_KEY environment variable to a random value before running in production.")
        app.config["SECRET_KEY"] = key

    @app.get("/config")
    def show_config():
        return jsonify(name=name, debug=app.debug, testing=app.testing, per_page=app.config["PER_PAGE"])

    return app
