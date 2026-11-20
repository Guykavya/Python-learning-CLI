## Hint 1

Which call does the actual database work in async code, and what must you put in front of it? Which attribute of the result gives you the objects?

## Hint 2

`(await session.scalars(select(Author).options(selectinload(Author.books)))).all()`. After this, `author.books` is a normal list and needs no I/O.

## Hint 3

```text
authors = (await session.scalars(select(Author).options(selectinload(Author.books)))).all()
ranked = sorted(((a.name, len(a.books)) for a in authors), key=lambda t: (-t[1], t[0]))
return ranked[:n]
```
