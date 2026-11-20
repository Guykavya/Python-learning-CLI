## Approach

Three small helpers and four short routes (the full file is `reference.py`).

```python
def owned_post(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        return None, api_error(404, "not_found", f"Post {post_id} not found")
    if post.user_id != g.user.id:
        return None, api_error(403, "forbidden", "Only the author may change this post")
    return post, None


@app.patch("/api/posts/<int:post_id>")
def update_post(post_id):
    if g.user is None:
        return unauthorized()
    data, error = json_object()
    if error:
        return error
    post, error = owned_post(post_id)
    if error:
        return error
    fields = validate(data, partial=True)
    if fields:
        return api_error(422, "validation_error", "Some fields are invalid", fields=fields)
    if "title" in data:
        post.title = data["title"].strip()
    if "body" in data:
        post.body = data["body"]
    db.session.commit()
    return jsonify(post.to_dict())
```

Example: `PATCH /api/posts/1 {"body": "new"}`: `"title" in data` is false, so the title is left alone. That is the difference between **PATCH** (partial update) and **PUT** (replace everything).

The status codes tell the client what to do: **401** (log in), **403** (you are logged in, but this is not yours), **404** (it does not exist), **415/400** (fix the request format), **422** (the format is fine, the *values* are not). The error shape is the same everywhere, so the client needs one error handler, not seven.

## Complexity

`O(1)` queries per request (one lookup by primary key, one commit).

## Another way

Marshmallow or Pydantic validate and serialise declaratively, and `flask-smorest`/`APIFlask` generate OpenAPI documentation from the same schemas. Writing it by hand once shows what they automate.

## Not covered

Pagination of the list (problem 25), CORS (problem 36), token authentication for non-browser clients (swe.07).
