# A blog platform with login

The project of the module (chapter section 24): a multi-page app with registration and login, built from an almost empty `solution.py`. Everything you learned in this module is used once: factory, blueprints, templates, forms, validation, CSRF, sessions, passwords, authorisation, Flask-SQLAlchemy, pagination, error handling, and a test suite that checks the whole story.

The starter gives you the models (`User`, `Post`), the extension `db`, the two blueprints `auth` and `blog`, an almost empty `TEMPLATES` dict and a minimal `create_app`. As in the other exercises the **templates live in `solution.py`** (a `DictLoader`), because the runner copies only `.py` files; the project in the chapter uses a `templates/` folder.

## Configuration (defaults in the factory; `test_config` overrides them)

`SECRET_KEY="dev"`, `SQLALCHEMY_DATABASE_URI="sqlite://"`, `PER_PAGE=5`, `HASH_METHOD="scrypt"` (the password hashing method passed to `generate_password_hash`; the tests use a fast one), `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE="Lax"`.

## Behaviour

**Every `POST`** needs the form field `csrf_token` equal to the session's token (`hmac.compare_digest`, empty never matches), otherwise **400** and nothing happens. Every form contains the hidden input. `csrf_token()` is a Jinja global. A `before_request` hook also sets `g.user` (the `User` for `session["user_id"]`, or `None`).

| Route | Behaviour |
|---|---|
| `GET/POST /auth/register` | fields `username` (`[a-z0-9_]{3,20}`), `password` (at least 8), `confirm` (equal). Errors: status **200**, form again, each message in `<p class="error">`, the username kept, **no password** in the HTML. Taken name: error `That username is taken` (catch `IntegrityError`, **rollback**). Success: hash the password, flash `Account created. Please log in.`, redirect to `/auth/login`. |
| `GET/POST /auth/login` | wrong user **or** password: **401**, the same single `<p class="error">Invalid username or password</p>` (check a dummy hash for unknown users). Success: `session.clear()`, `session["user_id"]`, flash `Welcome, <name>!`, redirect to `?next=` **only if it is a local path** (else `/`). |
| `POST /auth/logout` | clear the session, redirect to `/`. |
| `GET /` | posts newest first, `PER_PAGE` per page (`page` argument; a page past the end → 404), each as `<li class="post"><a href="/post/ID">title</a> by <span class="author">name</span></li>`; none: `<li class="empty">No posts yet.</li>`; links `<a class="prev">` and `<a class="next">` built with `url_for`. **At most 3 SQL statements** for the page. |
| `GET /post/<int:id>` | `<h1>` title, `<span class="author">`, `<div class="body">`; missing → 404. The **author** also sees `<a class="edit">` and `<form class="delete">`. |
| `GET/POST /new` | login required (anonymous → redirect to `/auth/login?next=/new`). Title 1 to 100 characters after stripping (else `<p class="error">`, form again with status 200 and the typed values). Success: flash, redirect to the new post. |
| `GET/POST /post/<id>/edit`, `POST /post/<id>/delete` | login required; missing → **404**; not the author → **403**; one helper `get_post_for_edit(id)` for both. After editing: redirect to the post; after deleting: redirect to `/`. |
| `GET /api/posts` | JSON `{"items": [{"id", "title", "author"}]}`, newest first, at most 20. |
| Errors | every `HTTPException` and any other exception: under `/api/` JSON `{"error": {"code": "not_found", "message": "Not Found"}}`; elsewhere an HTML page with `<h1>404 Not Found</h1>` and a link home. Unexpected exceptions are logged and answered as a plain 500 (no details). |

The navigation (in `base.html`) shows `Log in` / `Register` for visitors, and for a logged-in user `<span class="nav-user">name</span>`, a `New post` link and a logout **form** (with CSRF token). Flash messages appear in `<p class="flash">`.

User text is **escaped** everywhere (never `|safe`).

## How to work

Follow the build order of chapter section 24.2: factory and config, models, security helpers, `auth`, `blog`, errors and API, and run the tests after each step. The tests are in `test_solution.py`; read them like a specification.
