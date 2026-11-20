# Posts with CRUD and `get_or_404`

Chapter sections 14.2 to 14.4. In `solution.py` the starter has the extension object `db` and the model `Post` (`id`, `title`, `body`). Write the factory and four routes for a small JSON API:

| Route | Behaviour |
|---|---|
| `POST /posts` | JSON `{"title": "...", "body": "..."}` (`body` optional, default `""`). Missing/blank title → **400** `{"error": "title is required"}`. Success → **201** with the post (`{"id", "title", "body"}`). |
| `GET /posts` | list of posts ordered by `id`, as JSON |
| `GET /posts/<int:post_id>` | the post, or **404** when it does not exist |
| `DELETE /posts/<int:post_id>` | **204** with no body, or **404** when it does not exist |

The factory (starter) already creates the tables. A missing id must give a clean **404**, not a 500 caused by `None.title`: use **`db.get_or_404(Post, post_id)`**.

## Example

```text
POST /posts {"title": "Hello"}        -> 201 {"id": 1, "title": "Hello", "body": ""}
GET  /posts/1                         -> 200 {"id": 1, ...}
GET  /posts/99                        -> 404
DELETE /posts/1                       -> 204
```
