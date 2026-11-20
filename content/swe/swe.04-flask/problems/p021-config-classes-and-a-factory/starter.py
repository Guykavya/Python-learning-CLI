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
    app = Flask(__name__)
    app.config.from_object(CONFIGS[name])          # TODO: unknown name, production key, copies
    return app
