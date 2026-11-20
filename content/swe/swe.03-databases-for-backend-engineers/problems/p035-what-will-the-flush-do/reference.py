from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


def pending(session):
    def names(objects):
        return sorted(o.name for o in objects)
    return {"new": names(session.new), "dirty": names(session.dirty), "deleted": names(session.deleted)}
