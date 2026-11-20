from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=True)

    def set_password(self, password):
        self.password_hash = password            # TODO: never store the password itself

    def check_password(self, password):
        return self.password_hash == password    # TODO

    def to_dict(self):
        return {"id": self.id, "username": self.username, "password_hash": self.password_hash}   # TODO


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://")
    app.config.update(test_config or {})
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app
