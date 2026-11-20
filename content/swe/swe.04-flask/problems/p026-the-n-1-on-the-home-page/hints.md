## Hint 1

Read the starter's list comprehension. Which attributes does it touch that the first query did not load? Each one of them is a hidden `SELECT`, once per post.

## Hint 2

You need three facts per post: the title, the author's username, and a count of comments. One SQL statement can give them all: `JOIN` the user table, `LEFT OUTER JOIN` the comments (so posts without comments stay), `GROUP BY` the post, `COUNT(Comment.id)`. Or tell SQLAlchemy to load the relationships in advance (`joinedload`, `selectinload`).

## Hint 3

```text
rows = db.session.execute(
    db.select(Post.title, User.username, db.func.count(Comment.id))
      .join(User, Post.user_id == User.id)
      .outerjoin(Comment, Comment.post_id == Post.id)
      .group_by(Post.id, User.username)
      .order_by(Post.id.desc())).all()
return jsonify([{"title": t, "author": a, "comments": c} for t, a, c in rows])
```
