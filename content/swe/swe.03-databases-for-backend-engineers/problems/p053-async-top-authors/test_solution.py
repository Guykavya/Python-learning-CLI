import asyncio

import pytest
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from solution import Author, Base, Book, top_authors

DATA = {"Mira": 3, "Dev": 2, "Zed": 2, "Ana": 0, "Bo": 1}


async def with_db(tmp_path, body):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'a.db'}")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSession(engine, expire_on_commit=False) as session:
            for name, n in DATA.items():
                author = Author(name=name)
                session.add(author)
                await session.flush()
                session.add_all([Book(author_id=author.id, title=f"{name}-{i}") for i in range(n)])
            await session.commit()
        async with AsyncSession(engine, expire_on_commit=False) as session:
            return await body(session)
    finally:
        await engine.dispose()


def test_ranking_with_ties_and_empty_authors(tmp_path):
    async def body(session):
        return await top_authors(session, 10)

    got = asyncio.run(with_db(tmp_path, body))
    assert got == [("Mira", 3), ("Dev", 2), ("Zed", 2), ("Bo", 1), ("Ana", 0)], (
        f"Most books first, ties by name, authors without books included. Got {got}.")


def test_n_limits_the_list(tmp_path):
    async def body(session):
        return await top_authors(session, 2), await top_authors(session, 0)

    two, zero = asyncio.run(with_db(tmp_path, body))
    assert two == [("Mira", 3), ("Dev", 2)] and zero == []


def test_no_lazy_loading_happens(tmp_path):
    async def body(session):
        await top_authors(session, 3)
        authors = (await session.scalars(__import__("sqlalchemy").select(Author))).all()
        with pytest.raises(InvalidRequestError):
            authors[0].books                      # the models forbid lazy loading
        return True

    assert asyncio.run(with_db(tmp_path, body))


def test_returns_plain_tuples(tmp_path):
    async def body(session):
        return await top_authors(session, 1)

    got = asyncio.run(with_db(tmp_path, body))
    assert isinstance(got[0], tuple) and isinstance(got[0][0], str) and isinstance(got[0][1], int)
