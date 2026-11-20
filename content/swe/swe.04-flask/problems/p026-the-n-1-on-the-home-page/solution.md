## Approach

Ask the database for exactly the page, in one statement:

```python
rows = db.session.execute(
    db.select(Post.title, User.username, db.func.count(Comment.id))
    .join(User, Post.user_id == User.id)
    .outerjoin(Comment, Comment.post_id == Post.id)
    .group_by(Post.id, User.username)
    .order_by(Post.id.desc())
).all()
return jsonify([{"title": t, "author": a, "comments": c} for t, a, c in rows])
```

Example: for a post with 2 comments the `LEFT OUTER JOIN` produces 2 rows; `GROUP BY Post.id` folds them into one, and `COUNT(Comment.id)` counts the non-null comment ids: 2. For a post without comments the join gives one row with `NULL` in the comment columns, and `COUNT(Comment.id)` ignores `NULL`s, so the count is 0. (`COUNT(*)` would say 1: a classic mistake.)

The cost does not depend on the number of posts: one statement. The starter pays `1 + N + N` round trips.

## Complexity

One query; the database does `O(posts + comments)` work, with indexes on the foreign keys.

## Another way

```python
db.select(Post).options(joinedload(Post.author), selectinload(Post.comments)).order_by(Post.id.desc())
```
and `len(p.comments)` in Python: 2 statements. It loads every comment row only to count it; for big comment lists the aggregate query is better. If you need the comments' text too, `selectinload` is the right tool.

## Not covered

Adding `Post.comment_count` as a stored column (denormalisation), updated when a comment is added.
