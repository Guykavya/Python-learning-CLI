from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)



from sqlalchemy.exc import IntegrityError


def add_users(session, emails):
    # TODO: one SAVEPOINT (begin_nested) per user; skip duplicates; commit at the end
    for email in emails:
        session.add(User(email=email))
    session.commit()
    return len(emails), []
