## Approach

```python
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
from sqlalchemy.orm import selectinload


async def top_authors(session, n):
    authors = (await session.scalars(select(Author).options(selectinload(Author.books)))).all()
    ranked = sorted(((a.name, len(a.books)) for a in authors), key=lambda item: (-item[1], item[0]))
    return ranked[:n]
```

`await session.scalars(...)` runs the query without blocking the event loop. The `selectinload` option adds a second awaited query that loads **all** the books for those authors, so afterwards `a.books` is plain Python data. `lazy="raise"` on the models turns any forgotten option into an immediate error in the tests, instead of a confusing `MissingGreenlet` in production. Sorting by `(-count, name)` gives most books first and alphabetical ties.

Example: authors Mira (3 books), Dev (2), Zed (2), Ana (0): `top_authors(session, 3)` is `[("Mira", 3), ("Dev", 2), ("Zed", 2)]`.

## Complexity

Two queries; sorting `O(authors log authors)`.

## Another way

Let the database count: `select(Author.name, func.count(Book.id)).outerjoin(Book).group_by(Author.id).order_by(...).limit(n)` loads no books at all, which is better for big tables. The `selectinload` version shows the async loading rule.

## Why it matters

Async frameworks (FastAPI with async routes) fail in confusing ways when an ORM object lazily loads. Explicit loading, plus `lazy="raise"` in development, keeps async code honest.
