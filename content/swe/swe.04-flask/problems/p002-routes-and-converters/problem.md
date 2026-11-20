# Routes and converters

Chapter sections 3.1 to 3.3. In `solution.py` write `create_app()` that returns a Flask app with three routes. The **view function names** (the endpoints) are fixed, because the tests call `url_for` with them:

| URL rule | Endpoint | Returns |
|---|---|---|
| `/user/<username>` | `user_profile` | `User: <username>` |
| `/post/<int:post_id>` | `show_post` | `Post 7 (int)`: the id, then the **name of its Python type** in brackets |
| `/files/<path:subpath>` | `show_file` | `File: a/b/c.txt` |

Requirements:

- `/post/abc` must be **404**, not 500 and not "Post abc (str)": use the `int` converter.
- `/post/-3` is also 404 (the default `int` converter accepts only digits).
- `/user/` (no name) is 404.
- `url_for("show_post", post_id=7)` must give `/post/7`.

## Example

```text
GET /user/asha         -> 200  User: asha
GET /post/7            -> 200  Post 7 (int)
GET /files/a/b/c.txt   -> 200  File: a/b/c.txt
GET /post/abc          -> 404
```
