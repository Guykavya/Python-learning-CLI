from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100))
    body: Mapped[str] = mapped_column(db.Text, default="")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "body": self.body}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/posts/<int:post_id>")
    def show(post_id):
        post = db.session.get(Post, post_id)          # TODO: None for a missing id
        return jsonify(post.to_dict())

    # TODO: create, list, delete

    return app
