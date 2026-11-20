from sqlalchemy import Column, Integer, MetaData, String, Table, select

metadata = MetaData()
books = Table(
    "books", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("author", String(100), nullable=False),
    Column("price_paise", Integer, nullable=False),
)


def search_books(conn, title=None, max_price=None, author=None, order="title"):
    # TODO: start from select(title, author, price_paise); add where() only for the filters given;
    #       order_by a column chosen from a whitelist (ValueError otherwise)
    return [tuple(r) for r in conn.execute(select(books.c.title, books.c.author, books.c.price_paise))]
