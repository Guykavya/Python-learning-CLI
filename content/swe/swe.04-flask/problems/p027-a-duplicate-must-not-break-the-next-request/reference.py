import re

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

NAME = re.compile(r"[a-z0-9_]{3,20}")


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(20), unique=True)


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.post("/register")
    def register():
        data = request.get_json(silent=True) or {}
        username = str(data.get("username") or "").strip()
        if not NAME.fullmatch(username):
            return jsonify(error="username must be 3-20 characters: a-z, 0-9 and _"), 400
        user = User(username=username)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()                      # the session is usable again
            taken = set(db.session.scalars(db.select(User.username).where(User.username.like(username + "%"))))
            suggestions = []
            n = 1
            while len(suggestions) < 2:
                if f"{username}{n}" not in taken:
                    suggestions.append(f"{username}{n}")
                n += 1
            return jsonify(error=f"username {username!r} is taken", suggestions=suggestions), 409
        return jsonify(id=user.id, username=user.username), 201

    return app
