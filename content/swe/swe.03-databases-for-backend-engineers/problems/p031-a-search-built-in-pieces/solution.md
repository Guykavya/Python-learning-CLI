## Approach

```python
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
```

Each `if` adds one condition only when the caller gave a value, so no "empty" condition can match everything or nothing by mistake. The values become **bound parameters** (never pasted into the SQL). The sort column comes from a **whitelist dictionary**: the user's text is only a key, so `"price; DROP TABLE books"` is simply not a key. `icontains(..., autoescape=True)` escapes `%` and `_`, so a search for `50%` finds a title with a real percent sign instead of matching everything.

Example: `search_books(conn, title="py", max_price=20000)` produces `WHERE lower(title) LIKE '%' || lower(?) || '%' ESCAPE ... AND price_paise <= ?`.

## Complexity

One query.

## Another way

Build a list of conditions and use `.where(*conditions)`, or `and_(*conditions)`. For optional filters the "chain of `if`" form reads best.

## Why it matters

Search forms are the classic place for injection and for broken `LIKE` patterns. Whitelisting column names and escaping wildcards closes both.
