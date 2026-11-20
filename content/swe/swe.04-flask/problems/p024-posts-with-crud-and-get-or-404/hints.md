## Hint 1

What does `db.session.get(Post, 99)` return when row 99 does not exist? And what happens one line later in the starter's `show`?

## Hint 2

`db.get_or_404(Model, id)` does the same lookup but raises a 404 error for you when the row is missing. For creating: build the object, `db.session.add(...)`, `db.session.commit()`. For listing: `db.session.scalars(db.select(Post).order_by(Post.id)).all()`.

## Hint 3

```text
POST: read JSON, strip title; empty -> 400 {"error": "title is required"}; add, commit; return to_dict(), 201
GET list: scalars(select(Post).order_by(Post.id)).all() -> [to_dict()]
GET one: db.get_or_404(Post, post_id)
DELETE: post = db.get_or_404(...); db.session.delete(post); commit; return "", 204
```
