import functools

from flask import Flask, g, jsonify, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(30), unique=True)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100))
    body: Mapped[str] = mapped_column(db.Text, default="")
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"))

    def to_dict(self):
        return {"id": self.id, "title": self.title, "body": self.body, "author_id": self.user_id}


def api_error(status, code, message, **extra):
    """Every error of the API has this shape: {"error": {"code", "message", ...}}."""
    return jsonify(error={"code": code, "message": message, **extra}), status



def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", SECRET_KEY="dev")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.before_request
    def load_user():
        user_id = session.get("user_id")
        g.user = db.session.get(User, user_id) if user_id else None

    @app.get("/api/posts")
    def list_posts():
        posts = db.session.scalars(db.select(Post).order_by(Post.id.desc())).all()
        return jsonify(items=[p.to_dict() for p in posts])

    # TODO: show, create, update (PATCH), delete

    return app
