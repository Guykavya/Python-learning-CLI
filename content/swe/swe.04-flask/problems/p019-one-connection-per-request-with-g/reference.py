import sqlite3

from flask import Flask, current_app, g, jsonify


def init_db(path):
    db = sqlite3.connect(path)
    db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL)")
    db.commit()
    db.close()


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(DATABASE="app.db")
    app.config.update(test_config or {})
    init_db(app.config["DATABASE"])
    app.teardown_appcontext(close_db)

    @app.get("/")
    def home():
        return "home page: no database here"

    @app.get("/count")
    def count():
        get_db().execute("INSERT INTO notes (text) VALUES ('x')")
        get_db().commit()
        rows = get_db().execute("SELECT COUNT(*) AS n FROM notes").fetchone()
        return jsonify(count=rows["n"])

    @app.get("/boom")
    def boom():
        get_db().execute("SELECT 1")
        raise RuntimeError("something failed after using the database")

    return app
