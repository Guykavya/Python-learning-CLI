from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["Book"]] = relationship(back_populates="author", lazy="raise")


class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped["Author"] = relationship(back_populates="books", lazy="raise")


from sqlalchemy import select


async def top_authors(session, n):
    # TODO: load authors WITH their books (selectinload), rank by (-count, name), return the first n
    authors = (await session.scalars(select(Author))).all()
    return [(a.name, len(a.books)) for a in authors][:n]
