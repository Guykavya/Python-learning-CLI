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
    skipped = []
    added = 0
    for email in emails:
        try:
            with session.begin_nested():            # a SAVEPOINT: a failure undoes only this user
                session.add(User(email=email))
            added += 1
        except IntegrityError:
            skipped.append(email)
    session.commit()
    return added, skipped
