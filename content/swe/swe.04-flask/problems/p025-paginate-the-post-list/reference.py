from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.get("/posts")
    def index():
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)
        pagination = db.paginate(
            db.select(Post).order_by(Post.id.desc()),
            page=page, per_page=per_page, max_per_page=20, error_out=True,
        )
        next_url = url_for("index", page=pagination.next_num, per_page=pagination.per_page) if pagination.has_next else None
        prev_url = url_for("index", page=pagination.prev_num, per_page=pagination.per_page) if pagination.has_prev else None
        return jsonify(
            items=[p.title for p in pagination.items],
            page=pagination.page, pages=pagination.pages, total=pagination.total,
            per_page=pagination.per_page, next=next_url, prev=prev_url,
        )

    return app
