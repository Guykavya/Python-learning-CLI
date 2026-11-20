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

    @app.post("/posts")
    def create():
        data = request.get_json(silent=True) or {}
        title = str(data.get("title") or "").strip()
        if not title:
            return jsonify(error="title is required"), 400
        post = Post(title=title, body=data.get("body", ""))
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict()), 201

    @app.get("/posts")
    def index():
        posts = db.session.scalars(db.select(Post).order_by(Post.id)).all()
        return jsonify([p.to_dict() for p in posts])

    @app.get("/posts/<int:post_id>")
    def show(post_id):
        return jsonify(db.get_or_404(Post, post_id).to_dict())

    @app.delete("/posts/<int:post_id>")
    def delete(post_id):
        post = db.get_or_404(Post, post_id)
        db.session.delete(post)
        db.session.commit()
        return "", 204

    return app
