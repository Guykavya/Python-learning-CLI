# Split the app into blueprints

Chapter section 13. A **blueprint** is a bundle of routes, error handlers and templates that you register on an app, usually under a URL prefix. In `solution.py` write two blueprints (module-level variables named `auth` and `blog`) and a factory `create_app()` that registers both.

**`auth`** (`url_prefix="/auth"`):

| Route | Answer |
|---|---|
| `GET /auth/login` | `login page` |
| `POST /auth/logout` | redirect (302) to the **blog home page** (use `url_for("blog.index")`) |
| `GET /auth/profile/<name>` | `profile <name>` for the name `asha`; any other name: `abort(404)` |

**`blog`** (no prefix):

| Route | Answer |
|---|---|
| `GET /` | `home` |
| `GET /post/<int:post_id>` | the title from the dict `POSTS = {1: "Hello", 2: "Flask"}`; other ids: `abort(404)` |

**Three different 404 pages**, so you can see which handler answered:

- a 404 raised by an **auth** view (`abort(404)`) → body `auth 404`, status 404 (handler on the blueprint `auth`);
- a 404 raised by a **blog** view → body `blog 404`;
- a 404 for a URL that matches **no route at all** (like `/auth/nothing` or `/xyz`) → body `app 404` (handler on the app).

Endpoints are prefixed with the blueprint name: `url_for("auth.login") == "/auth/login"`, `url_for("blog.show", post_id=1) == "/post/1"`. Name the post view function `show`.

## Example

```text
GET /auth/profile/ravi  -> 404 auth 404
GET /post/99            -> 404 blog 404
GET /auth/nothing       -> 404 app 404
```
