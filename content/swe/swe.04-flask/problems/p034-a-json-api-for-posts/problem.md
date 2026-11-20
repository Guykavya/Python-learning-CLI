# A JSON API for posts

Chapter section 18. Build a small REST API for posts in `solution.py`. The starter gives you `db`, `User`, `Post` (with `to_dict()`), and the helper `api_error(status, code, message, **extra)` that builds **every error answer** in one shape:

```json
{"error": {"code": "not_found", "message": "Post 99 not found"}}
```

The user is identified by the session (`session["user_id"]`, set by the tests): the `before_request` hook loads `g.user` (a `User` or `None`).

| Request | Answer |
|---|---|
| `GET /api/posts` | **200** `{"items": [post, ...]}`, newest first |
| `GET /api/posts/<int:id>` | **200** the post, or **404** `not_found` |
| `POST /api/posts` | anonymous: **401** `unauthorized`. Not JSON: **415** `unsupported_media_type`. Body not an object: **400** `bad_request`. `title` missing/blank/over 100 characters or `body` not a string: **422** `validation_error` with `"fields": {...}` in the error. Success: **201**, the post, header `Location: /api/posts/<id>`; the author is the logged-in user. |
| `PATCH /api/posts/<int:id>` | updates **only the fields that are present** (`title` and/or `body`); the same validation for the given fields. Anonymous **401**; not the author **403** `forbidden`; missing **404**. Returns **200** and the post. |
| `DELETE /api/posts/<int:id>` | same checks; success **204** with no body. |

Check in this order: login (401), JSON shape (415/400), existence (404), ownership (403), validation (422). A post is `{"id", "title", "body", "author_id"}`.

Anonymous users get a **401 with JSON**, never a redirect to a login page: an API client cannot follow a login form.

## Example

```text
POST  /api/posts {"title": "Hi"}        (logged in as user 1) -> 201 Location: /api/posts/1
PATCH /api/posts/1 {"body": "new text"}                        -> 200 title unchanged, body "new text"
PATCH /api/posts/1                       (as user 2)           -> 403 {"error": {"code": "forbidden", ...}}
```
