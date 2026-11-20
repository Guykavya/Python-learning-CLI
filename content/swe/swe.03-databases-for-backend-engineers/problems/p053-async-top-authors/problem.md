# Async top authors

Chapter section 17. With `AsyncSession` every database call is awaited, and **lazy loading cannot work**: reading an unloaded relationship would need I/O inside a plain attribute access, which an async program cannot do (it raises `MissingGreenlet`, or with `lazy="raise"` an `InvalidRequestError`). So in async code you **always load what you need up front**.

`starter.py` has the models `Author(id, name)` and `Book(id, author_id, title)` with `lazy="raise"` on both relationships, and a function that forgets to load the books. Write

```python
async def top_authors(session, n)       # session: an AsyncSession
```

returning the `n` authors with the most books, as a list of `(name, number_of_books)` tuples: **most books first, ties by name**; authors without books are included (with 0). Load the books with **`selectinload`** (no lazy loading anywhere). `n` larger than the number of authors returns all of them.

The test runs it with `asyncio.run(...)` against `sqlite+aiosqlite:///` in a temporary folder.

## Example

```python
await top_authors(session, 2)       # [("Mira", 3), ("Dev", 2)]
```
