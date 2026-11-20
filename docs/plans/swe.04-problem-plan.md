# Problem plan: swe.04 Flask (40 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.04.p001`…`p040`.

**Mix:** 14 drill, 14 applied, 10 deep, 2 challenge. **Kinds:** 31 code, 5 trace, 4 explain.
**assessment:** explain = p029, trace = p013, fix = p031, build = p040.
**★ core set:** p002, p006, p013, p015, p017, p021, p023, p024, p029, p030, p031, p032, p034, p035, p040 (outcome: a multi-page app with login from an empty folder).

**Testing notes**
- Every code problem exposes **`create_app(test_config=None)`** (the factory of Ch. 11); the test builds a fresh app per test with `{"TESTING": True, "SECRET_KEY": "test", "SQLALCHEMY_DATABASE_URI": "sqlite://", "WTF..."}` and uses `app.test_client()`. Never a module-level app shared between tests.
- **Templates live inside `solution.py`.** The runner does not copy `.html` files from `my-work/` (R1), so problems put templates in a dict `TEMPLATES = {"base.html": "...", "index.html": "..."}` and the factory sets `app.jinja_loader = jinja2.DictLoader(TEMPLATES)`. `problem.md` explains this is a test convenience; the project (p040) shows the normal `templates/` folder in `solution.md`. No static files are tested.
- Uploads go to `app.config["UPLOAD_FOLDER"]`, set by the test to `tmp_path`.
- Logged-in tests use a `login(client, user, password)` helper in `conftest.py` that does the real POST (with the CSRF token read from the form when the problem has CSRF, Ch. 21.3).
- HTML assertions use simple substring checks or BeautifulSoup (installed); never compare whole pages (whitespace changes).
- Flask import ~0.3 s; each test file runs in ~1–2 s.

## A. WSGI and routing (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | A WSGI app with no framework ✅ | drill | code | `app(environ, start_response)` (Ch. 1.2): `/hello?name=Asha` → `Hello, Asha`, unknown path → 404, bytes body list; test builds `environ` with `wsgiref.util.setup_testing_defaults` |
| 2 | Routes and converters ✅ | drill | code | `/user/<username>`, `/post/<int:post_id>`, `/files/<path:subpath>`; `/post/abc` → 404 (not 500); the int view receives an `int` |
| 3 | Predict the routing ✅ | drill | trace | `⚠ HAND-TRACE` the chapter's style (Ch. 3.8): 8 requests to an app with trailing-slash rules, a redirect and `url_for`; write status code and `Location`/body for each |
| 4 | One view, two methods ✅ | drill | code | `/contact` GET shows the form, POST handles it, PUT → 405 with an `Allow` header listing GET, HEAD, OPTIONS, POST |

## B. The request and the response (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Query strings are strings ✅ | drill | code | `/items?page=2&per_page=50` with `request.args.get(..., type=int)`; defaults; `per_page` clamped to 1..100; `page=abc` falls back to 1 |
| 6 | A JSON endpoint that refuses bad input ✅ | applied | code | `POST /api/notes`: not JSON → 415, broken JSON → 400 with a JSON error body (`get_json(silent=True)`), missing `title` → 422-style 400 listing the field, success → 201 + `Location` |
| 7 | Safe file uploads ✅ | applied | code | `MAX_CONTENT_LENGTH` → 413, `secure_filename`, extension allow-list, no overwrite (adds `-1`); `../../evil.py` saved safely inside `UPLOAD_FOLDER` |
| 8 | What does this return value send? ✅ | drill | trace | `⚠ HAND-TRACE` five views (Ch. 5.1: string, tuple with status, tuple with headers, dict, `("", 204)`); write status, `Content-Type` and body |
| 9 | Hooks for every response ✅ | applied | code | `after_request` adds `X-Content-Type-Options`, `X-Frame-Options` and an `X-Request-ID` (incoming one reused if valid, else `uuid4`); `before_request` stores it in `g` |
| 10 | The request lifecycle, in order ✅ | deep | trace | `⚠ HAND-TRACE` an app whose `before_request`, view, `after_request`, `teardown_request` and an error handler append to a list; write the list for a normal request, a 404 and a view that raises |

## C. Templates (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | A list page with loops and filters ✅ | drill | code | render posts with `{% for %}`, `{% else %}` for "no posts", `|title`, `|truncate(40)`, a date with `strftime`; test parses the HTML |
| 12 | Stop the XSS ✅ | drill | code | the starter marks user comments `|safe`; a comment `<script>alert(1)</script>` must appear escaped; trusted admin HTML uses `Markup` only after `bleach`-free allow-list escaping (keep it to escaping) |
| 13 | Predict the inherited page ✅ | applied | trace | `assessment = "trace"`. `⚠ HAND-TRACE` `base.html` with 3 blocks, a child that overrides two and calls `super()` in one, and a grandchild; write the rendered text lines (whitespace rules pinned with `-` trims) |
| 14 | A macro for form fields ✅ | applied | code | `render_field(name, label, value, errors)` macro; errors shown in a list, value kept after a failed POST, `aria-invalid` set when there are errors |

## D. Forms, validation and CSRF (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Post/Redirect/Get with flash ✅ | applied | code | valid POST → 302 to `/thanks`, flash shown once then gone; invalid → 200 with errors and the typed values kept; refreshing `/thanks` does not resubmit |
| 16 | Validate a signup form ✅ | drill | code | `validate_signup(form)` → `{field: message}`: email shape, password ≥ 10 chars, passwords match, username `[a-z0-9_]{3,20}`; values stripped |
| 17 | A hand-rolled CSRF check ✅ | deep | code | token stored in `session`, put in every form, checked on every POST with `hmac.compare_digest`; missing/wrong → 400; a GET never changes data (Ch. 9.3) |
| 18 | Why CSRF tokens work ✅ | applied | explain | what the attacker's page can and cannot do (send cookies: yes; read the token: no), where `SameSite=Lax` helps and where it does not; checklist from Ch. 9.2 |

## E. Contexts, the factory, configuration, blueprints (Ch. 10–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | One connection per request with `g` ✅ | applied | code | `get_db()` opens lazily, stores in `g`, `teardown_appcontext` closes; the test counts opens: 0 for a page that does not use it, 1 for a page that calls it 3 times |
| 20 | Which line needs a context? ✅ | deep | trace | `⚠ HAND-TRACE` 7 lines using `current_app`, `request`, `url_for`, `g` inside and outside `app_context()` / `test_request_context()`; write `ok` or `RuntimeError` for each |
| 21 | Config classes and a factory ✅ | applied | code | `create_app("testing" | "development" | "production")`; production refuses the default `SECRET_KEY` with `RuntimeError`; two apps in one process do not share config (Ch. 11.3) |
| 22 | Config from the environment ✅ | drill | code | `app.config.from_prefixed_env("BLOG")`; `BLOG_DEBUG=false` becomes `False`, `BLOG_PER_PAGE=20` an int; tests use `monkeypatch.setenv` |
| 23 | Split the app into blueprints ✅ | applied | code | `auth` (`/auth/login`, `/auth/logout`) and `blog` (`/`, `/post/<id>`) blueprints; `url_for("blog.index")`; each blueprint has its own 404 for its prefix |

## F. Flask-SQLAlchemy (Ch. 14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Posts with CRUD and `get_or_404` ✅ | drill | code | `Post` model; create/list/show/delete views; missing id → 404 page, not a 500 |
| 25 | Paginate the post list ✅ | applied | code | `db.paginate(select(Post).order_by(...), page=, per_page=, max_per_page=20)`; next/prev links; page past the end → 404; newest first |
| 26 | The N+1 on the home page ✅ | deep | code | the home page shows each post's author name and comment count; with the conftest query counter the page must run ≤ 3 queries for 30 posts |
| 27 | A duplicate must not break the next request ✅ | deep | code | registering a taken username → 409 with a message, `db.session.rollback()` so the next request works (the starter forgets; second request 500s) (Ch. 14.7) |

## G. Passwords, sessions and authorisation (Ch. 15–17)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 28 | Store passwords properly ✅ | drill | code | `set_password`/`check_password` with `werkzeug.security`; the same password twice gives different hashes; the plain password appears nowhere in the database row |
| 29 | What is inside the session cookie? ✅ | deep | explain | `assessment = "explain"`. Decode a given Flask session cookie by hand (base64 payload, signature) and explain why it is **signed, not encrypted**, what that allows and forbids, and why `session.clear()` at login matters; checklist from Ch. 16.2 and 16.6 |
| 30 | `login_required`, by hand ✅ | applied | code | decorator with `functools.wraps`; anonymous → 302 to `/auth/login?next=/path`; logged in → view runs; `g.user` loaded in `before_app_request` |
| 31 | Fix the login view ✅ | deep | code | `assessment = "fix"`. Three bugs: different messages for "no such user" and "wrong password" (enumeration), no `session.clear()` before setting the user (fixation), redirects to any `next` URL (open redirect to `https://evil.example`). Tests check each, plus a normal login still works |
| 32 | Only the author may edit ✅ | applied | code | edit/delete another user's post → 403; own post → works; the check lives in one helper `get_post_for_edit(id)` (Ch. 17.2); a test logs in as two users |
| 33 | Cookie flags and remember-me ✅ | drill | code | `SESSION_COOKIE_HTTPONLY`, `SECURE`, `SAMESITE="Lax"`, `PERMANENT_SESSION_LIFETIME` 14 days only when "remember me" is ticked; the test reads the `Set-Cookie` header |

## H. REST APIs, errors and CORS (Ch. 18–20)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 34 | A JSON API for posts ✅ | applied | code | `GET /api/posts`, `POST` (201 + `Location`), `PATCH /api/posts/<id>` (only given fields), `DELETE` (204); errors as `{"error": {"code", "message"}}`; owner checks reused from p032 |
| 35 | Errors: JSON for the API, HTML for pages ✅ | deep | code | `register_error_handler` for 404/405/500 that answers JSON under `/api/` and HTML elsewhere; a view that raises gives 500 with no traceback text in the body |
| 36 | CORS by hand ✅ | deep | code | `OPTIONS` preflight answered for allowed origins only, `Access-Control-Allow-Origin` echoes the allowed origin (never `*` with credentials), `Vary: Origin`; unknown origin gets no CORS headers |

## I. Testing and running (Ch. 21–23)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 37 | Tests that catch the bugs ✅ | challenge | code | the learner writes `check_login_flow(client)`, `check_owner_only(client_factory)` etc. as plain functions with asserts; the test runs them against the correct app (must pass) and against 3 broken apps (each must fail), so weak tests are caught |
| 38 | What does a framework remove? ✅ | drill | explain | compare the raw-socket server of swe.02 with the Flask app: routing, parsing, responses, errors, testing; checklist from Ch. 1.1 |
| 39 | Never in production ✅ | deep | explain | why `debug=True` and the development server must not face the internet (the Werkzeug console runs code), what replaces them (Gunicorn behind a proxy); checklist from Ch. 22.2–22.3 |

## J. Project (Ch. 24)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 40 | A blog platform with login ✅ | challenge | code | `assessment = "build"`. `create_app` with `auth` and `blog` blueprints, `User`/`Post` models, register/login/logout, CSRF on every form, create/edit/delete own posts, paginated home, JSON error pages for `/api`. Tests: full flow register → login → post → edit → logout; another user gets 403; POST without CSRF → 400; anonymous create → redirect to login; home page ≤ 3 queries |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 8, 11, 12, 16, 22, 24, 28, 33, 38 (14); applied 6, 7, 9, 13, 14, 15, 18, 19, 21, 23, 25, 30, 32, 34 (14); deep 10, 17, 20, 26, 27, 29, 31, 35, 36, 39 (10); challenge 37, 40 (2). Total 40.
Kinds: trace 3, 8, 10, 13, 20 (5); explain 18, 29, 38, 39 (4); code 31.

## Risks and open questions

- Flask's `session` cookie format (p029) is stable but tied to `itsdangerous`; the problem gives a ready cookie string and asks for reasoning, not for exact bytes.
- Flask-SQLAlchemy with `sqlite://` keeps one in-memory database per app because it uses a static pool for in-memory SQLite; if a future version changes that, switch the test config to a `tmp_path` file.
- p037's broken apps must each break exactly one rule, or a learner's test can fail for the wrong reason; describe each break in `solution.md`.

Written 2026-11-19 (Sonnet, main session, no subagents). All 40 validated. Deviations from the table: no shared `conftest.py` (each test file carries its own few lines of helpers, so a problem folder is self-contained); templates live in a `TEMPLATES` dict with `app.jinja_loader = jinja2.DictLoader(...)`; Flask-WTF is not installed, so every CSRF problem uses the hand-rolled check; the trace answers (p003, p008, p010, p013, p020) come from real runs (p003's trailing-slash 308 shows the absolute `http://localhost/about/`); p006 answers 422 for field errors (the plan said "422-style 400"); p014's macro never prints a password value; p016 returns `(clean, errors)`; p017 compares tokens as bytes (`compare_digest` raises `TypeError` on a non-ASCII `str`, which the tests send); p019 wraps `sqlite3.connect` with a counting spy; p021 deep-copies the config values (`from_object` shares mutable ones); p023: a blueprint 404 handler only sees errors raised by its own views, so a URL that matches no route is answered by the app handler (the plan's "own 404 for its prefix" is not possible, and the problem teaches exactly that); p027: the failed session shows up when the view queries for name suggestions and, inside a long app context, in the next request; p030's `Location` is `next=/dashboard` (Werkzeug 3 does not escape slashes in a query value); p031 also counts `check_password_hash` calls to prove the unknown-user path does the same work; p037 has four broken apps (two CSRF bugs, so a test that only sends a missing token is caught); p040 adds a `HASH_METHOD` config (the tests use a fast hash) and 26 tests; p029's cookie timestamp is Unix seconds.
