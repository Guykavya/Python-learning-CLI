from sqlalchemy import Column, Integer, MetaData, String, Table, select

metadata = MetaData()
books = Table(
    "books", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("author", String(100), nullable=False),
    Column("price_paise", Integer, nullable=False),
)

ORDERS = {"title": books.c.title, "price": books.c.price_paise, "author": books.c.author}


def search_books(conn, title=None, max_price=None, author=None, order="title"):
    if order not in ORDERS:
        raise ValueError(f"cannot order by {order!r}; use one of {sorted(ORDERS)}")
    query = select(books.c.title, books.c.author, books.c.price_paise)
    if title is not None:
        query = query.where(books.c.title.icontains(title, autoescape=True))
    if max_price is not None:
        query = query.where(books.c.price_paise <= max_price)
    if author is not None:
        query = query.where(books.c.author == author)
    query = query.order_by(ORDERS[order], books.c.id)
    return [tuple(row) for row in conn.execute(query)]
