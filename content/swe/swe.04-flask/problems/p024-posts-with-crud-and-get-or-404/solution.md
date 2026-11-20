## Approach

```python
@app.post("/posts")
def create():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400
    post = Post(title=title, body=data.get("body", ""))
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_dict()), 201


@app.get("/posts/<int:post_id>")
def show(post_id):
    return jsonify(db.get_or_404(Post, post_id).to_dict())


@app.delete("/posts/<int:post_id>")
def delete(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    return "", 204
```

(The list route and the complete file are in `reference.py`.)

Example: `GET /posts/99` runs `get_or_404`, which looks the row up and, when it is missing, calls `abort(404)`. The user sees a normal "Not Found" page; with the starter's `db.session.get` the value is `None` and `None.to_dict()` is an `AttributeError`, a **500** that looks like a bug in your server although it is a bad URL.

The pattern *"fetch or stop with 404"* is so common that it deserves a helper (and, with ownership, problem 32 builds on it).

## Complexity

`O(1)` per lookup by primary key; `O(n)` for the list.

## Another way

`db.first_or_404(db.select(Post).where(...))` when you look up by something other than the primary key (a slug).

## Not covered

Pagination (problem 25) and the N+1 problem (26).
