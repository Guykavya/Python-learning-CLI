# Paginate the post list

Chapter section 14.5. A list of thousands of posts must be served **in pages**. In `solution.py` the starter has `db` and `Post(id, title)`. Write `GET /posts` using **`db.paginate`**:

- Newest first: `ORDER BY id DESC` (without an `ORDER BY`, pages are not stable).
- Query parameters `page` (default 1) and `per_page` (default **5**), read with `type=int`; `per_page` is limited to **20** (`max_per_page=20`).
- JSON answer:

```json
{"items": ["Post 23", "Post 22"], "page": 1, "pages": 5, "total": 23, "per_page": 5,
 "next": "/posts?page=2&per_page=5", "prev": null}
```

`next` and `prev` are URLs built with `url_for("index", page=..., per_page=...)`, or `null` when there is no such page.

- A page **past the end** (`page=6` of 5) and `page=0` give **404** (that is what `db.paginate(..., error_out=True)` does).
- The first page of an **empty** table is fine: `items: []`.
- `page=abc` falls back to page 1 (`type=int` default).

Name the view function `index`.

## Example (23 posts, `Post 1` to `Post 23`)

```text
GET /posts            -> items Post 23 .. Post 19, pages 5, next /posts?page=2&per_page=5, prev null
GET /posts?page=5     -> items Post 3, Post 2, Post 1; next null; prev /posts?page=4&per_page=5
GET /posts?page=6     -> 404
GET /posts?per_page=100 -> per_page 20
```
