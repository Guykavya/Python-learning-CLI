# A search built in pieces

Chapter section 8.4. A search form has optional fields. `solution.py` defines the table `books(id, title, author, price_paise)` (`metadata`, `books`). Write

```python
search_books(conn, title=None, max_price=None, author=None, order="title")
```

`conn` is a SQLAlchemy `Connection`. Build **one** `select` for the columns `title, author, price_paise` and add a `where` only for the filters that were **given** (not `None`):

- `title`: the title **contains** the text, ignoring case. Characters such as `%` and `_` in the text mean themselves (use `icontains(text, autoescape=True)`).
- `max_price`: `price_paise <= max_price`.
- `author`: exactly equal.
- `order`: one of `"title"`, `"price"`, `"author"` (sort by that column, then by `id`). **Any other value raises `ValueError`**, even when no filter is given: the column name must come from a whitelist, never from the user's text.

Return a list of tuples `(title, author, price_paise)`.

## Example

```python
search_books(conn, title="python", max_price=50000, order="price")
search_books(conn)                                  # every book, ordered by title
search_books(conn, order="price; DROP TABLE books") # ValueError
```
