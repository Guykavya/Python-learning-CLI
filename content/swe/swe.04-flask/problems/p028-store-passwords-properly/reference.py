from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=True)

    def set_password(self, password):
        if not isinstance(password, str) or not password:
            raise ValueError("password must be a non-empty string")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash or not isinstance(password, str):
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app
