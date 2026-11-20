# The N+1 on the home page

Chapter section 14.6 (and swe.03, "N+1"). The blog home page lists every post with its **author's name** and its **number of comments**. The starter does it the obvious way: it loads the posts, then for each post touches `post.author` and `post.comments`, and each touch is a hidden query. For 30 posts that is **61 queries** for one page.

In `solution.py` the models `User`, `Post` and `Comment` are given (do not change them). Rewrite the view `GET /` so that the page runs **at most 3 SQL statements**, whatever the number of posts, and answers exactly the same JSON:

```json
[{"title": "Post 30", "author": "user30", "comments": 2}, ...]
```

newest post first (order by `Post.id` descending). The test counts the statements with an event listener and shows the statement that repeated if you are over the limit.

Ideas: one query with a `JOIN` to the users and a `LEFT OUTER JOIN` + `COUNT` for the comments (one statement), or `joinedload`/`selectinload` for the relationships and `len(...)` in Python (two or three statements).

## Example

Before: 1 query for the posts + 30 for the authors + 30 for the comments = 61. After: 1 to 3.
