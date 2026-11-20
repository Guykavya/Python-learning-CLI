## Hint 1

Which SQL clauses does a page need? Which of them must come first, so that page 2 is always "the next ones" and not a random selection?

## Hint 2

`db.paginate(select, page=, per_page=, max_per_page=, error_out=True)` returns a `Pagination` with `.items`, `.page`, `.pages`, `.total`, `.has_next`, `.next_num`, `.has_prev`, `.prev_num`. Pass the select with `.order_by(Post.id.desc())`. Read `page` and `per_page` yourself with `type=int` and defaults.

## Hint 3

```text
page = args.get("page", 1, type=int);  per_page = args.get("per_page", 5, type=int)
p = db.paginate(db.select(Post).order_by(Post.id.desc()), page=page, per_page=per_page, max_per_page=20, error_out=True)
next = url_for("index", page=p.next_num, per_page=p.per_page) if p.has_next else None
prev = same with p.prev_num / p.has_prev
return jsonify(items=[titles], page, pages, total, per_page, next, prev)
```
