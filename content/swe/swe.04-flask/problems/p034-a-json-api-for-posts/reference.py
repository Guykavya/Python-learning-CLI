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

    def validate(data, partial):
        fields = {}
        if "title" in data or not partial:
            title = data.get("title")
            if not isinstance(title, str) or not title.strip():
                fields["title"] = "is required and must be a non-empty string"
            elif len(title.strip()) > 100:
                fields["title"] = "must be at most 100 characters"
        if "body" in data and not isinstance(data["body"], str):
            fields["body"] = "must be a string"
        return fields

    def json_object():
        if not request.is_json:
            return None, api_error(415, "unsupported_media_type", "Send the body as application/json")
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return None, api_error(400, "bad_request", "The body must be a JSON object")
        return data, None

    def owned_post(post_id):
        post = db.session.get(Post, post_id)
        if post is None:
            return None, api_error(404, "not_found", f"Post {post_id} not found")
        if post.user_id != g.user.id:
            return None, api_error(403, "forbidden", "Only the author may change this post")
        return post, None

    unauthorized = lambda: api_error(401, "unauthorized", "Log in first")

    @app.get("/api/posts")
    def list_posts():
        posts = db.session.scalars(db.select(Post).order_by(Post.id.desc())).all()
        return jsonify(items=[p.to_dict() for p in posts])

    @app.get("/api/posts/<int:post_id>")
    def show_post(post_id):
        post = db.session.get(Post, post_id)
        if post is None:
            return api_error(404, "not_found", f"Post {post_id} not found")
        return jsonify(post.to_dict())

    @app.post("/api/posts")
    def create_post():
        if g.user is None:
            return unauthorized()
        data, error = json_object()
        if error:
            return error
        fields = validate(data, partial=False)
        if fields:
            return api_error(422, "validation_error", "Some fields are invalid", fields=fields)
        post = Post(title=data["title"].strip(), body=data.get("body", ""), user_id=g.user.id)
        db.session.add(post)
        db.session.commit()
        response = jsonify(post.to_dict())
        response.status_code = 201
        response.headers["Location"] = url_for("show_post", post_id=post.id)
        return response

    @app.patch("/api/posts/<int:post_id>")
    def update_post(post_id):
        if g.user is None:
            return unauthorized()
        data, error = json_object()
        if error:
            return error
        post, error = owned_post(post_id)
        if error:
            return error
        fields = validate(data, partial=True)
        if fields:
            return api_error(422, "validation_error", "Some fields are invalid", fields=fields)
        if "title" in data:
            post.title = data["title"].strip()
        if "body" in data:
            post.body = data["body"]
        db.session.commit()
        return jsonify(post.to_dict())

    @app.delete("/api/posts/<int:post_id>")
    def delete_post(post_id):
        if g.user is None:
            return unauthorized()
        post, error = owned_post(post_id)
        if error:
            return error
        db.session.delete(post)
        db.session.commit()
        return "", 204

    return app
