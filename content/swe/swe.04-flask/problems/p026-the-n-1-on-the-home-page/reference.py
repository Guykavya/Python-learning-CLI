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
        rows = db.session.execute(
            db.select(Post.title, User.username, db.func.count(Comment.id))
            .join(User, Post.user_id == User.id)
            .outerjoin(Comment, Comment.post_id == Post.id)
            .group_by(Post.id, User.username)
            .order_by(Post.id.desc())
        ).all()
        return jsonify([{"title": t, "author": a, "comments": c} for t, a, c in rows])

    return app
