## Approach

```python
@app.get("/posts")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    pagination = db.paginate(
        db.select(Post).order_by(Post.id.desc()),
        page=page, per_page=per_page, max_per_page=20, error_out=True,
    )
    next_url = url_for("index", page=pagination.next_num, per_page=pagination.per_page) if pagination.has_next else None
    prev_url = url_for("index", page=pagination.prev_num, per_page=pagination.per_page) if pagination.has_prev else None
    return jsonify(
        items=[p.title for p in pagination.items],
        page=pagination.page, pages=pagination.pages, total=pagination.total,
        per_page=pagination.per_page, next=next_url, prev=prev_url,
    )
```

Example: with 23 posts and `per_page=5`, `pages = ceil(23 / 5) = 5`. Page 5 starts at offset 20 and holds the last 3 rows. `db.paginate` runs two queries: the `LIMIT 5 OFFSET 20` page and a `COUNT(*)` for the total.

`max_per_page=20` is a **safety limit**: the client chooses `per_page`, so without a cap one request could ask for a million rows. `error_out=True` turns an impossible page into a 404 instead of an empty list that hides a bug in the client.

## Complexity

`O(per_page)` rows returned plus a count query. Note that `OFFSET` itself costs `O(offset)` in the database: very deep pages get slow (see "Another way").

## Another way

**Keyset pagination**: `WHERE id < :last_seen ORDER BY id DESC LIMIT 5`. It stays fast on millions of rows and does not skip or repeat rows when new posts arrive during browsing. It cannot jump to "page 37", which is why simple UIs keep `OFFSET`.

## Not covered

HTML page links (`pagination.iter_pages()`), which build a numbered page bar in a template.
