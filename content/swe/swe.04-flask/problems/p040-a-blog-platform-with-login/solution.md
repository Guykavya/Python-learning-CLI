## Approach

Build the app layer by layer, as in the chapter, and let the tests tell you what is missing. The finished file is `reference.py` (about 300 lines). Its parts:

```text
config + extensions     create_app: defaults, test_config, DictLoader, db.init_app, blueprints
security helpers        csrf_token(), CSRF check in before_request, safe_next(), login_required, get_post_for_edit()
models                  User(username unique, password_hash), Post(title, body, user_id, author relationship)
auth blueprint          register (validate, hash, rollback on duplicate), login (generic error, session.clear, safe next), logout (POST)
blog blueprint          index (paginate + joinedload), show, new, edit, delete, /api/posts
errors                  one handler for HTTPException, one for Exception; JSON under /api/, HTML elsewhere
```

Two excerpts that carry most of the security of the app:

```python
@app.before_request
def load_user_and_check_csrf():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        sent = request.form.get("csrf_token", "")
        expected = session.get("csrf_token", "")
        if not sent or not expected or not hmac.compare_digest(sent.encode(), expected.encode()):
            abort(400, description="Bad or missing CSRF token.")
```

```python
session.clear()                       # at login: new session, no fixation
session["user_id"] = user.id          # only the id: roles and names come from the database
return redirect(safe_next(request.args.get("next")))
```

Example (the whole story in the first test): register, log in, create a post, read it, edit it, delete it, see the 404 afterwards. Each step is a browser-like request: the test reads the CSRF token from the page, as a real browser would send it back.

How the earlier problems appear here: p016 (validation), p017 (CSRF), p021 and p022 (config), p023 (blueprints), p025 and p026 (paging, no N+1), p027 (rollback), p028 (hashing), p030 to p033 (login, ownership, cookies), p035 (errors).

## Complexity

The home page costs two statements (the page with its authors, and the count); every other page costs a constant number of statements.

## Another way

Move the templates to a real `templates/` folder (`base.html` with `{% extends %}` and `{% block %}` exactly as here), the models into `models.py`, and the blueprints into a package, as in section 24.1. Use Flask-Migrate for schema changes and Gunicorn to run it (problem 39).

## Not covered

Comments, user profiles, search, avatars (the chapter's stretch goals), a production database, and rate limiting on the login route.
