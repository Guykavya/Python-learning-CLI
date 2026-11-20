from flask import Flask, jsonify
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
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"))
    author: Mapped["User"] = db.relationship()
    comments: Mapped[list["Comment"]] = db.relationship()


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(db.ForeignKey("post.id"))
    text: Mapped[str] = mapped_column(db.String(200))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()


    @app.get("/")
    def home():
        posts = db.session.scalars(db.select(Post).order_by(Post.id.desc())).all()
        return jsonify([
            {"title": p.title, "author": p.author.username, "comments": len(p.comments)}   # two hidden queries per post
            for p in posts
        ])

    return app
