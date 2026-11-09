# Chapter 4 (SWE): Flask

In the networking chapter you built an HTTP server from raw sockets and saw how much work lives between "bytes arrive" and "the right function runs": parsing the request line, reading headers, finding the body, building a response with the correct `Content-Length`. In the database chapter you learned how an application stores its state. This chapter joins the two. **Flask** is the thin layer that turns an HTTP request into a Python function call and a return value into an HTTP response, and it gives you the places to plug in templates, a database, logins and tests.

Flask is called a **micro-framework**. That does not mean it is only for small apps. It means the core is small (routing, request and response objects, templates, sessions) and everything else is a separate package you add when you need it. This is a good way to learn: you can see every piece, and nothing is hidden behind magic.

By the end you reach three outcomes:

- You can **build a multi-page web app with registration and login from an empty folder**, using routes, templates, forms and a database.
- You can **structure it so it grows**: application factory, blueprints, configuration that changes per environment.
- You can **test it without a browser or a server**, with the test client and pytest fixtures.

The project at the end is a blog platform (users, posts, comments, login, a JSON API, tests), built step by step.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux, **Flask 3.1**, **Flask-SQLAlchemy 3.1**, **SQLAlchemy 2.x** and **Werkzeug 3.1**. The output you see is the real output. Values that differ between machines or runs (password hashes, random tokens, timestamps) are either avoided or labelled.

**Offline by design.** Everything you must *run* needs **no server and no internet**. Flask ships a **test client** that calls your app directly, so we can send requests and read responses without opening a port. Where we need a real server we start it on `127.0.0.1` in a thread, exactly as in the networking chapter. Anything that needs a browser, Gunicorn, Docker or an extra package (Flask-Login, Flask-WTF, Flask-Migrate) is in a clearly marked **"Try it on your machine"** box. In those boxes the commands are exact, but the output is *described*, because it was not captured while writing the chapter.

**Check your tools first.**

```python
import sys
from importlib.metadata import version

print("python", sys.version.split()[0])
for name in ("flask", "werkzeug", "jinja2", "flask-sqlalchemy", "sqlalchemy", "pytest"):
    print(name, version(name))
```
```text
python 3.14.4
flask 3.1.3
werkzeug 3.1.9
jinja2 3.1.6
flask-sqlalchemy 3.1.1
sqlalchemy 2.1.8
pytest 9.1.1
```

Your versions may be a little different. That is fine; everything here is written in the style of Flask 3.x and SQLAlchemy 2.x.

**What this chapter does not repeat.** HTTP methods, status codes, headers, cookies and sessions are in **swe.02**; read sections 8 to 12 there if "idempotent", `Set-Cookie` or `302` are unfamiliar. SQL, the ORM `Session`, lazy loading, N+1 and migrations are in **swe.03**. Here we only show how they connect to Flask.

## Table of contents

1. [Why a framework, and WSGI in one page](#1-why-a-framework-and-wsgi-in-one-page)
2. [The smallest app, and how to run it](#2-the-smallest-app-and-how-to-run-it)
3. [Routing](#3-routing)
4. [The request object](#4-the-request-object)
5. [Responses](#5-responses)
6. [Templates with Jinja2](#6-templates-with-jinja2)
7. [Template inheritance, macros and static files](#7-template-inheritance-macros-and-static-files)
8. [Forms by hand: GET, POST, redirect and flash](#8-forms-by-hand-get-post-redirect-and-flash)
9. [Validation and CSRF](#9-validation-and-csrf)
10. [Contexts: application, request, `g`](#10-contexts-application-request-g)
11. [The application factory](#11-the-application-factory)
12. [Configuration and secrets](#12-configuration-and-secrets)
13. [Blueprints](#13-blueprints)
14. [Flask-SQLAlchemy](#14-flask-sqlalchemy)
15. [Passwords and hashing](#15-passwords-and-hashing)
16. [Session-based authentication](#16-session-based-authentication)
17. [Authorisation and ownership](#17-authorisation-and-ownership)
18. [REST APIs in Flask](#18-rest-apis-in-flask)
19. [Error handling](#19-error-handling)
20. [CORS in one page](#20-cors-in-one-page)
21. [Testing Flask apps](#21-testing-flask-apps)
22. [Logging, the debugger and running for real](#22-logging-the-debugger-and-running-for-real)
23. [Extensions you will meet](#23-extensions-you-will-meet)
24. [Project: a blog platform, step by step](#24-project-a-blog-platform-step-by-step)
25. [Common traps](#25-common-traps)
26. [Summary](#26-summary)

## 1. Why a framework, and WSGI in one page

### 1.1 What a framework removes

In the raw-socket server of swe.02 section 15 you wrote code to split the request line, collect headers, honour `Content-Length`, and format the response. None of that is about *your* application. A framework does it once, correctly, and gives you a clean shape:

```text
  bytes from the socket
          |
          v
  +----------------------+
  |  web server          |   Gunicorn, Werkzeug's dev server: sockets, threads/processes
  +----------+-----------+
             |  WSGI call:  app(environ, start_response)
             v
  +----------------------+
  |  Flask               |   routing, request/response objects, sessions, templates
  +----------+-----------+
             |  calls YOUR view function
             v
  +----------------------+
  |  your code           |   def show_post(post_id): ... return "..."
  +----------------------+
```

### 1.2 WSGI: the contract between server and framework

**WSGI** (Web Server Gateway Interface) is a tiny agreement. A WSGI application is any callable that takes two arguments and returns an iterable of bytes:

```python
def app(environ, start_response):
    # environ: a dict describing the request. start_response: call it with status and headers.
    body = f"You asked for {environ['PATH_INFO']} with {environ['REQUEST_METHOD']}\n".encode()
    start_response("200 OK", [("Content-Type", "text/plain"), ("Content-Length", str(len(body)))])
    return [body]


# Call it by hand, the way a server would.
captured = {}
def start_response(status, headers):
    captured["status"], captured["headers"] = status, headers

result = app({"PATH_INFO": "/hello", "REQUEST_METHOD": "GET"}, start_response)
print(captured["status"])
print(b"".join(result).decode().strip())
```
```text
200 OK
You asked for /hello with GET
```

That is the whole idea. **A Flask object *is* a WSGI application**: `app(environ, start_response)` works on it. Because the contract is so small, any WSGI server (Gunicorn, uWSGI, Waitress, Werkzeug's built-in) can run any WSGI framework (Flask, Django, Bottle). You will rarely write a WSGI function yourself; knowing it exists explains two things later: why the **test client** can call your app with no network (it builds an `environ` dict and calls the app), and why deployment guides say "point Gunicorn at `module:app`" (it needs the callable).

## 2. The smallest app, and how to run it

### 2.1 Hello, Flask

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, Flask!"


client = app.test_client()
response = client.get("/")
print(response.status)
print(response.headers["Content-Type"])
print(response.get_data(as_text=True))
```
```text
200 OK
text/html; charset=utf-8
Hello, Flask!
```

Three things happened:

- `Flask(__name__)` created the application. The name tells Flask where to find templates and static files (the folder of that module).
- `@app.route("/")` registered `home` in a **URL map**: "requests for `/` go to `home`".
- The function returned a `str`. Flask turned it into a full response: status `200 OK`, `Content-Type: text/html; charset=utf-8`, the body.

The line `client = app.test_client()` is how this chapter "makes requests". It never opens a port. The same code in a file `hello.py` would be run like this:

> ### Try it on your machine: the development server
> Save the app (without the three test-client lines) as `hello.py` and run:
>
> ```text
> flask --app hello run
> ```
>
> You should see a few log lines saying it is a development server, and `Running on http://127.0.0.1:5000`. Open that address in a browser to see the text. Stop it with Ctrl+C. Add `--debug` to turn on the reloader and the in-browser debugger (development only, see section 22). On macOS port 5000 may be taken by AirPlay; use `--port 5001`.

### 2.2 A real server in a thread, once

To prove the test client is not cheating, the same app on a real socket (port 0: the OS picks a free port), called with `requests`:

```python
import logging, threading
import requests
from flask import Flask
from werkzeug.serving import make_server

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask!"

logging.getLogger("werkzeug").setLevel(logging.ERROR)   # hide the per-request log line
server = make_server("127.0.0.1", 0, app)          # port 0: the OS chooses
port = server.server_port
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()

r = requests.get(f"http://127.0.0.1:{port}/", timeout=5)
print(r.status_code, r.headers["Content-Type"], r.text)
print("Server header starts with:", r.headers["Server"].split("/")[0])

server.shutdown()
thread.join()
```
```text
200 text/html; charset=utf-8 Hello, Flask!
Server header starts with: Werkzeug
```

Same answer. From now on we use the test client: it is faster, needs no port, and gives easier access to what the app did (cookies, redirects, the session).

### 2.3 What `__name__` is for

`Flask(__name__)` tells Flask where the **root path** is: the folder that holds `templates/` and `static/`. If you meet `TemplateNotFound`, print `app.root_path` first.

## 3. Routing

### 3.1 A route maps a URL pattern and a method to a function

The decorator `@app.route(rule, methods=[...])` records a **rule**. When a request arrives, Flask matches the path against the rules, checks the method, and calls the function. Shortcuts exist for each method: `@app.get`, `@app.post`, `@app.put`, `@app.delete`.

```python
from flask import Flask

app = Flask(__name__)

@app.get("/about")
def about():
    return "About us"

@app.post("/subscribe")
def subscribe():
    return "Subscribed", 201

c = app.test_client()
print(c.get("/about").status_code)
print(c.get("/missing").status_code)          # no rule: 404 Not Found
print(c.post("/about").status_code)           # rule exists, wrong method: 405
print(sorted(c.post("/about").headers["Allow"].split(", ")))   # which methods are allowed
print(c.post("/subscribe").status_code)
```
```text
200
404
405
['GET', 'HEAD', 'OPTIONS']
201
```

A `404` means "no rule matches this URL". A `405` means "a rule matches, but not for this method". The `Allow` header (swe.02 section 11) lists the methods that would work. `GET` also gives you `HEAD` and `OPTIONS` automatically.

### 3.2 Variable rules and converters

Parts of the URL in angle brackets become function arguments. A **converter** before the colon checks and converts the text.

```python
from flask import Flask

app = Flask(__name__)

@app.get("/user/<username>")
def profile(username):                 # default converter: string without slashes
    return f"profile of {username}"

@app.get("/post/<int:post_id>")
def post(post_id):                     # int converter: you get a real int
    return f"post {post_id} is {type(post_id).__name__}"

@app.get("/files/<path:subpath>")
def files(subpath):                    # path converter: may contain slashes
    return f"file {subpath}"

c = app.test_client()
for url in ["/user/kavya", "/post/42", "/post/abc", "/post/-1", "/files/a/b/c.txt"]:
    r = c.get(url)
    print(f"{url:20} {r.status_code} {r.get_data(as_text=True)[:30]!r}")
```
```text
/user/kavya          200 'profile of kavya'
/post/42             200 'post 42 is int'
/post/abc            404 '<!doctype html>\n<html lang=en>'
/post/-1             404 '<!doctype html>\n<html lang=en>'
/files/a/b/c.txt     200 'file a/b/c.txt'
```

Notice `/post/abc` is a `404`, not an error inside your function: the converter refused to match, so the rule did not match. That is good design: **the URL pattern is the first validation layer**. Built-in converters: `string` (default), `int`, `float`, `path`, `uuid`. A negative number fails `int` too (use a custom converter or check inside if you need it).

### 3.3 `url_for`: never hard-code URLs

`url_for("function_name", **values)` builds a URL from the *endpoint name* (by default the function name). If you later change `/post/<int:post_id>` to `/p/<int:post_id>`, every `url_for` call is still right. Extra keyword arguments that are not in the rule become the query string.

```python
from flask import Flask, url_for

app = Flask(__name__)

@app.get("/post/<int:post_id>")
def show_post(post_id):
    return "..."

@app.get("/")
def index():
    return "..."

with app.test_request_context():       # url_for needs a context (section 10)
    print(url_for("show_post", post_id=7))
    print(url_for("index", page=2, sort="new"))
    print(url_for("show_post", post_id=7, _external=True))
    print(url_for("index", _anchor="top"))
```
```text
/post/7
/?page=2&sort=new
http://localhost/post/7
/#top
```

`_external=True` gives the full URL including the host (needed in emails). `_anchor` adds `#top`.

### 3.4 Methods and one function for GET and POST

Forms use the same URL to show the form (`GET`) and to process it (`POST`). List both methods and branch on `request.method`:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return f"thanks, {request.form['name']}"
    return "<form>...</form>"

c = app.test_client()
print(c.get("/contact").get_data(as_text=True))
print(c.post("/contact", data={"name": "Asha"}).get_data(as_text=True))
```
```text
<form>...</form>
thanks, Asha
```

### 3.5 Trailing slashes

Flask follows the rule you wrote, and is strict in a way that surprises beginners:

- Rule `"/projects/"` (with slash): visiting `/projects` **redirects** (308) to `/projects/`.
- Rule `"/about"` (no slash): visiting `/about/` is a **404**.

```python
from flask import Flask

app = Flask(__name__)

@app.get("/projects/")
def projects():
    return "projects"

@app.get("/about")
def about():
    return "about"

c = app.test_client()
r = c.get("/projects")
print(r.status_code, r.headers["Location"])
print(c.get("/projects/").status_code)
print(c.get("/about/").status_code)
```
```text
308 http://localhost/projects/
200
404
```

Pick one style (the common one for APIs is **no** trailing slash) and keep it everywhere.

### 3.6 Redirects and `url_for` together

```python
from flask import Flask, redirect, url_for

app = Flask(__name__)

@app.get("/")
def index():
    return "home"

@app.get("/old-home")
def old_home():
    return redirect(url_for("index"))              # 302 by default

c = app.test_client()
r = c.get("/old-home")
print(r.status_code, r.headers["Location"])
r = c.get("/old-home", follow_redirects=True)      # the client follows, like a browser
print(r.status_code, r.get_data(as_text=True))
```
```text
302 /
200 home
```

Pass `code=301` only for URLs that moved forever (browsers cache them hard); use `302/303` for "after this action, go there".

### 3.8 Predict the output

```python
from flask import Flask
app = Flask(__name__)

@app.get("/n/<int:n>/")
def n(n): return str(n * 2)

c = app.test_client()
print(c.get("/n/4/").get_data(as_text=True))
print(c.get("/n/4").status_code)
print(c.get("/n/x/").status_code)
print(c.post("/n/4/").status_code)
```

<details><summary>Answer</summary>

```text
8
308
404
405
```

`/n/4/` matches and returns `8`. `/n/4` lacks the slash the rule has, so Flask redirects (308). `x` is not an `int`, so no rule matches (404). `POST` finds the rule but the rule only allows `GET`/`HEAD`/`OPTIONS` (405).
</details>

## 4. The request object

### 4.1 `request` is the incoming message, parsed

Inside a view you import `request` from `flask`. It looks like a global but always refers to the request being handled right now (how that works is section 10). It is the parsed form of the text you saw in swe.02.

| You want | Use | Type |
|---|---|---|
| Method, path | `request.method`, `request.path` | `str` |
| Query string `?a=1&b=2` | `request.args` | `MultiDict` |
| HTML form fields | `request.form` | `MultiDict` |
| JSON body | `request.get_json()` | `dict`/`list` |
| Uploaded files | `request.files` | `MultiDict` of `FileStorage` |
| Headers | `request.headers` | case-insensitive mapping |
| Cookies | `request.cookies` | `dict` |
| Raw body | `request.get_data()` | `bytes` |
| Client address | `request.remote_addr` | `str` |

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/inspect", methods=["GET", "POST"])
def inspect():
    return {
        "method": request.method,
        "path": request.path,
        "args": request.args.to_dict(),
        "tags": request.args.getlist("tag"),
        "form": request.form.to_dict(),
        "user_agent": request.headers.get("User-Agent"),
        "cookie_theme": request.cookies.get("theme"),
        "content_type": request.content_type,
    }

c = app.test_client()
c.set_cookie("theme", "dark")
r = c.post("/inspect?tag=a&tag=b&page=2", data={"name": "Asha"}, headers={"User-Agent": "demo/1.0"})
import json
print(json.dumps(r.get_json(), sort_keys=True))
```
```text
{"args": {"page": "2", "tag": "a"}, "content_type": "application/x-www-form-urlencoded", "cookie_theme": "dark", "form": {"name": "Asha"}, "method": "POST", "path": "/inspect", "tags": ["a", "b"], "user_agent": "demo/1.0"}
```

Returning a `dict` from a view makes Flask send JSON (section 5.4).

### 4.2 Query strings are strings: use `type=` and defaults

`request.args.get("page")` is a `str` or `None`. Converting by hand invites `ValueError`. Pass `type=int` and a default; a bad value quietly falls back to the default.

```python
from flask import Flask, request

app = Flask(__name__)

@app.get("/list")
def list_items():
    page = request.args.get("page", 1, type=int)
    return f"page={page!r}"

c = app.test_client()
for qs in ["", "?page=3", "?page=abc", "?page=", "?page=2&page=9"]:
    print(f"{qs or '(none)':16}", c.get("/list" + qs).get_data(as_text=True))
```
```text
(none)           page=1
?page=3          page=3
?page=abc        page=1
?page=           page=1
?page=2&page=9   page=2
```

For form data the difference between `request.form["name"]` and `request.form.get("name")` is important:

- `request.form["name"]` raises `BadRequestKeyError`, which Flask turns into **400 Bad Request**, if the field is missing. Fine when the field is required.
- `request.form.get("name")` returns `None` for a missing field; you then decide what to do.

### 4.3 JSON bodies

`request.get_json()` parses the body if `Content-Type` is `application/json`. If it is not JSON, or the JSON is broken, Flask raises 415 or 400 by default. `get_json(silent=True)` returns `None` instead, so you can send your own error body.

```python
from flask import Flask, request

app = Flask(__name__)

@app.post("/echo")
def echo():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return {"error": "send a JSON object"}, 400
    return {"you_sent": data, "keys": sorted(data)}

c = app.test_client()
print(c.post("/echo", json={"b": 1, "a": [1, 2]}).get_json())
print(c.post("/echo", data="not json", content_type="application/json").status_code)
print(c.post("/echo", json=[1, 2]).get_json())
```
```text
{'keys': ['a', 'b'], 'you_sent': {'a': [1, 2], 'b': 1}}
400
{'error': 'send a JSON object'}
```

`json=` in the test client sets the header and encodes the body for you.

### 4.4 File uploads

Uploaded files arrive in `request.files`, each a `FileStorage` with `.filename`, `.read()` and `.save(path)`. **Never trust the filename**: it is chosen by the client and can contain `../../etc/passwd`. Use `werkzeug.utils.secure_filename`, or better, generate your own name.

```python
import io
from flask import Flask, request
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024            # reject bodies over 1 KiB (413)

@app.post("/upload")
def upload():
    f = request.files.get("photo")
    if f is None or f.filename == "":
        return "no file", 400
    data = f.read()
    return {"claimed": f.filename, "safe": secure_filename(f.filename), "size": len(data)}

c = app.test_client()
r = c.post("/upload", data={"photo": (io.BytesIO(b"hello"), "../../evil name.png")},
           content_type="multipart/form-data")
print(r.get_json())
big = c.post("/upload", data={"photo": (io.BytesIO(b"x" * 5000), "big.bin")},
             content_type="multipart/form-data")
print(big.status_code)
```
```text
{'claimed': '../../evil name.png', 'safe': 'evil_name.png', 'size': 5}
413
```

`MAX_CONTENT_LENGTH` is your protection against someone uploading gigabytes. Always set it on apps that accept uploads.

### 4.5 Headers and cookies

`request.headers` is case-insensitive. Behind a proxy `request.remote_addr` is the *proxy's* address; Flask does not trust `X-Forwarded-For` by default. Use `werkzeug.middleware.proxy_fix.ProxyFix` with the exact number of proxies you have, never blindly.

## 5. Responses

### 5.1 What a view may return

Flask accepts several shapes and builds a `Response` object from them:

| Return value | Result |
|---|---|
| `"text"` | 200, HTML |
| `("text", 201)` | status |
| `("text", 201, {"X-A": "b"})` | status + headers |
| `{"a": 1}` or a `list` | 200, JSON |
| a `Response` object | used as is |
| `None` | error: a view must return something |

```python
from flask import Flask

app = Flask(__name__)

@app.get("/a")
def a(): return "plain"

@app.get("/b")
def b(): return "created", 201, {"Location": "/b/1"}

@app.get("/c")
def c_(): return {"ok": True, "items": [1, 2]}

@app.get("/d")
def d(): return ["list", "works", "too"]

@app.get("/e")
def e(): return "", 204

c = app.test_client()
for path in "abcde":
    r = c.get("/" + path)
    print(path, r.status_code, r.content_type, r.headers.get("Location"), r.get_data(as_text=True)[:25])
```
```text
a 200 text/html; charset=utf-8 None plain
b 201 text/html; charset=utf-8 /b/1 created
c 200 application/json None {"items":[1,2],"ok":true}
d 200 application/json None ["list","works","too"]

e 204 text/html; charset=utf-8 None 
```

### 5.2 `make_response` for cookies and headers

When you need to modify the response (set a cookie, add headers), build it with `make_response`:

```python
from flask import Flask, make_response

app = Flask(__name__)

@app.get("/set-theme/<name>")
def set_theme(name):
    resp = make_response(f"theme set to {name}")
    resp.set_cookie("theme", name, max_age=3600, httponly=True, samesite="Lax")
    resp.headers["Cache-Control"] = "no-store"
    return resp

c = app.test_client()
r = c.get("/set-theme/dark")
print([p.strip().split("=")[0] if p.strip().startswith("Expires") else p.strip() for p in r.headers["Set-Cookie"].split(";")])
print(r.headers["Cache-Control"])
```
```text
['theme=dark', 'Expires', 'Max-Age=3600', 'HttpOnly', 'Path=/', 'SameSite=Lax']
no-store
```

(`Expires` has a date that depends on when you run it, so we print only its name.) The cookie attributes (`HttpOnly`, `SameSite`, `Max-Age`) are the ones from swe.02 section 12; we come back to them for login cookies in section 16.

### 5.3 `abort` stops the request with an HTTP error

`abort(404)` raises an exception that Flask turns into the right response. Use it for "stop right here" situations; it never returns, so no `else` is needed.

```python
from flask import Flask, abort

app = Flask(__name__)
POSTS = {1: "First post"}

@app.get("/post/<int:post_id>")
def show(post_id):
    if post_id not in POSTS:
        abort(404, description="No such post.")
    return POSTS[post_id]

@app.get("/admin")
def admin():
    abort(403)

c = app.test_client()
r = c.get("/post/9")
print(r.status_code, "|", "No such post." in r.get_data(as_text=True))
print(c.get("/admin").status_code)
print(c.get("/post/1").get_data(as_text=True))
```
```text
404 | True
403
First post
```

### 5.4 `jsonify` and returning dicts

Returning a dict is the same as `jsonify(dict)`. Use `jsonify(...)` when you need to build the response and set a status: `return jsonify(error="x"), 404`. Both set `Content-Type: application/json`. `jsonify` knows `datetime`, `date`, `UUID` and `Decimal`, but not your own classes: convert to dicts yourself (a `to_dict()` method is the simplest way, used in the project).

```python
from datetime import date
from flask import Flask, jsonify

app = Flask(__name__)

@app.get("/d")
def d():
    return jsonify(day=date(2026, 1, 31), n=3, tags=["a", "b"])

r = app.test_client().get("/d")
print(r.content_type)
print(r.get_json())
```
```text
application/json
{'day': 'Sat, 31 Jan 2026 00:00:00 GMT', 'n': 3, 'tags': ['a', 'b']}
```

### 5.5 Before and after hooks for responses

Sometimes every response needs the same header. `@app.after_request` runs after each view and receives the response:

```python
from flask import Flask

app = Flask(__name__)

@app.after_request
def add_security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp                      # you MUST return the response

@app.get("/")
def home(): return "hi"

print(dict(app.test_client().get("/").headers))
```
```text
{'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '2', 'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY'}
```

The mirror image is `@app.before_request`, which runs before every view. If it returns a value, that value is the response and the view is skipped; we use this for login loading and CSRF checks.

### 5.6 The request lifecycle

```text
  request arrives (environ)
        |
        v
  build Request object, push contexts (section 10)
        |
        v
  before_request hooks ----- one returns a value? ----> skip the view
        |
        v
  URL matching: rule + converters  --no match--> 404 / 405 -> error handler
        |
        v
  your view function  --raises--> error handler (section 19)
        |
        v
  make_response(return value)
        |
        v
  after_request hooks (response in, response out)
        |
        v
  save session cookie, pop contexts, teardown_request hooks
        |
        v
  response sent
```

Keep this picture in mind. Almost every "why did my code not run?" or "where does this value come from?" question is answered by finding the box in this diagram.

### 5.7 Try it

What does this print? (Think about which hooks run, and in which order.)

```python
from flask import Flask
app = Flask(__name__)
log = []

@app.before_request
def b(): log.append("before")

@app.after_request
def a(resp):
    log.append("after")
    return resp

@app.get("/")
def home():
    log.append("view")
    return "x"

c = app.test_client()
c.get("/"); c.get("/nothing")
print(log)
```

<details><summary>Answer</summary>

```text
['before', 'view', 'after', 'before', 'after']
```

For `/`: before, view, after. For `/nothing`: before still runs (it runs before URL matching fails the request into the 404 handler), there is no view, and after runs on the 404 response.
</details>


## 6. Templates with Jinja2

### 6.1 Why templates

You could build HTML with f-strings. Do it once and you will find three problems: the HTML is buried in Python, designers cannot edit it, and **every value you insert must be escaped by hand or you have a security hole** (section 6.5). A **template engine** keeps HTML in `.html` files, with small holes for values, and escapes by default. Flask uses **Jinja2**.

A template is text with three kinds of markers:

| Marker | Meaning | Example |
|---|---|---|
| `{{ ... }}` | print an expression | `{{ user.name }}` |
| `{% ... %}` | a statement (loop, if, block) | `{% for p in posts %}` |
| `{# ... #}` | a comment, not sent to the browser | `{# todo #}` |

### 6.2 `render_template` and the `templates/` folder

`render_template("page.html", **values)` finds `templates/page.html` next to your app, renders it with the values, and returns a string. The next block creates a tiny project in a temporary folder so you can see the real file layout:

```python
from pathlib import Path
from flask import Flask, render_template

Path("templates").mkdir()
Path("templates/hello.html").write_text(
    "<h1>Hello, {{ name }}!</h1>\n"
    "<p>You have {{ items|length }} item{{ 's' if items|length != 1 }}.</p>\n"
)

app = Flask(__name__)

@app.get("/hello/<name>")
def hello(name):
    return render_template("hello.html", name=name, items=["a", "b"])

print(app.test_client().get("/hello/Asha").get_data(as_text=True))
```
```text
<h1>Hello, Asha!</h1>
<p>You have 2 items.</p>
```

If you see `TemplateNotFound`, check three things: the folder is called `templates` (plural), it sits next to the module that created `Flask(__name__)`, and the name in `render_template` matches the path.

### 6.3 Variables, attributes and filters

`{{ user.name }}` works for a dict key *and* an attribute: Jinja tries `user["name"]` and `user.name` for you. A missing variable renders as an empty string (not an error) unless you configure strict mode, so **typos fail silently**; an easy first debugging step is to print the variable on its own.

**Filters** transform a value, written with a pipe. You can chain them.

```python
from flask import render_template_string, Flask
from datetime import datetime

app = Flask(__name__)
tpl = """\
{{ "kavya baghel"|title }}
{{ name|upper }} | {{ name|length }} | {{ missing|default("(none)") }}
{{ items|join(", ") }} | first={{ items|first }} | last={{ items|last }}
{{ 3.14159|round(2) }} | {{ 1234567|string|reverse|join("") }}
{{ when.strftime("%d %b %Y") }}
{{ "  padded  "|trim }}|
{{ long_text|truncate(20) }}
{{ users|map(attribute="name")|join(" + ") }}
{{ users|selectattr("active")|list|length }} active
"""
with app.app_context():
    print(render_template_string(
        tpl, name="asha", items=["x", "y", "z"], when=datetime(2026, 3, 9),
        long_text="This sentence is much too long to show",
        users=[{"name": "A", "active": True}, {"name": "B", "active": False}]))
```
```text
Kavya Baghel
ASHA | 4 | (none)
x, y, z | first=x | last=z
3.14 | 7654321
09 Mar 2026
padded|
This sentence is...
A + B
1 active
```

Useful filters to remember: `default`, `length`, `join`, `upper/lower/title`, `round`, `truncate`, `trim`, `first/last`, `map`, `selectattr`, `sort`, `safe` (careful, see below), `tojson` (puts a value into a `<script>` safely), `urlencode`.

### 6.4 Control flow

```python
from flask import render_template_string, Flask

app = Flask(__name__)
tpl = """\
{% for p in posts -%}
  {{ loop.index }}. {{ p.title }}{% if loop.last %} (last){% endif %}
{% else -%}
  No posts.
{% endfor -%}
{% if user and user.admin %}admin{% elif user %}member{% else %}guest{% endif %}
{% set total = posts|sum(attribute="views") %}total views: {{ total }}
"""
with app.app_context():
    print(render_template_string(tpl, posts=[{"title": "A", "views": 3}, {"title": "B", "views": 4}], user={"admin": False}))
    print("---")
    print(render_template_string(tpl, posts=[], user=None))
```
```text
1. A
2. B (last)
member
total views: 7
---
No posts.
guest
total views: 0
```

Key points:

- `{% for %}` has an `{% else %}` branch that runs when the sequence is empty. That replaces an `if posts` check.
- Inside a loop you get `loop.index` (from 1), `loop.index0`, `loop.first`, `loop.last`, `loop.length`.
- The dash in `{%- ... -%}` strips the whitespace on that side. Whitespace rarely matters in HTML; it matters in plain-text output.
- Keep **logic out of templates**. A template decides how to show things; the view decides what to show. If a template needs a complicated condition, compute a variable in the view.

### 6.5 Autoescaping and XSS

This is the most important thing in the template chapter. Suppose a user registers with the name `<script>steal(document.cookie)</script>` and your page shows `Hello, {name}`. If you paste that text into the HTML, the browser sees a script tag and **runs it, with your site's authority**. That attack is **XSS** (cross-site scripting). The defence: before inserting a value into HTML, turn the characters `< > & " '` into harmless entities. Jinja in Flask does this **automatically** for templates ending in `.html`, `.htm`, `.xml`, `.xhtml` and for `render_template_string`.

```python
from flask import Flask, render_template_string
from markupsafe import Markup, escape

app = Flask(__name__)
evil = '<script>steal(document.cookie)</script>'

with app.app_context():
    print("1:", render_template_string("<p>Hello, {{ name }}</p>", name=evil))
    print("2:", render_template_string("<p>Hello, {{ name|safe }}</p>", name=evil))
    print("3:", render_template_string('<a title="{{ t }}">x</a>', t='" onmouseover="alert(1)'))

# The f-string version: the hole.
print("4:", f"<p>Hello, {evil}</p>")
print("5:", escape(evil))
print("6:", type(Markup("<b>ok</b>")).__name__)
```
```text
1: <p>Hello, &lt;script&gt;steal(document.cookie)&lt;/script&gt;</p>
2: <p>Hello, <script>steal(document.cookie)</script></p>
3: <a title="&#34; onmouseover=&#34;alert(1)">x</a>
4: <p>Hello, <script>steal(document.cookie)</script></p>
5: &lt;script&gt;steal(document.cookie)&lt;/script&gt;
6: Markup
```

Read the results:

1. Autoescape on: `<` becomes `&lt;`. The browser *shows* the text; it does not run it. Safe.
2. `|safe` tells Jinja "this is already safe HTML, do not escape". With user data, that **re-opens the hole**. Only use `|safe` on HTML *you* produced from trusted pieces.
3. Autoescape also protects attribute values (the quote became `&#34;`).
4. A plain f-string has no protection. Never build HTML for users this way. (Line 5 shows `escape()` doing by hand what autoescape does for you.)

`Markup` is a `str` subclass that means "already safe". `escape()` returns a `Markup`. When you combine `Markup` with a normal string, the normal string is escaped, so Markup composition stays safe.

Three more XSS rules:

- A value inside a `<script>` block or an `onclick="..."` needs **`|tojson`**, not just HTML escaping: `<script>var user = {{ user|tojson }};</script>`.
- A user-supplied URL in `href` can be `javascript:alert(1)`. Escaping does not stop it. Check that the scheme is `http` or `https` before showing it as a link.
- Rendering Markdown from users into HTML needs a sanitiser (for example the `bleach` or `nh3` package). Markdown libraries pass raw HTML through by default.

### 6.6 Context processors

Values every template needs (the current user, a CSRF token function) are injected with `@app.context_processor`, which returns a dict. You can also register your own filter with `@app.template_filter("name")`. The project uses a context processor for `csrf_token`.

## 7. Template inheritance, macros and static files

### 7.1 Inheritance: one layout, many pages

Almost every page of a site shares a header, a navigation bar and a footer. Copying them into each template means a change in 40 files. **Inheritance** fixes this. A **base template** defines the skeleton with named `{% block %}` holes; a **child** says `{% extends "base.html" %}` and fills the blocks.

```text
   base.html                         index.html (child)
   +------------------------+        {% extends "base.html" %}
   | <nav> ... </nav>       |        {% block title %}Home{% endblock %}
   | {% block title %}      |  <---  {% block content %}
   | {% block content %}    |          <h1>Posts</h1> ...
   | <footer> ... </footer> |        {% endblock %}
   +------------------------+
```

```python
from pathlib import Path
from flask import Flask, render_template

Path("templates").mkdir()
Path("templates/base.html").write_text("""\
<html><head><title>{% block title %}Site{% endblock %} - Blog</title></head>
<body>
<nav><a href="{{ url_for('index') }}">Home</a></nav>
{% block content %}{% endblock %}
<footer>(c) 2026</footer>
</body></html>
""")
Path("templates/index.html").write_text("""\
{% extends "base.html" %}
{% block title %}Home{% endblock %}
{% block content %}<h1>Welcome</h1>{% endblock %}
""")
Path("templates/about.html").write_text("""\
{% extends "base.html" %}
{% block title %}About{% endblock %}
{% block content %}
<h1>About</h1>
<p>{{ super() }}extra</p>
{% endblock %}
""")

app = Flask(__name__)

@app.get("/")
def index(): return render_template("index.html")

@app.get("/about")
def about(): return render_template("about.html")

c = app.test_client()
print(c.get("/").get_data(as_text=True))
print(c.get("/about").get_data(as_text=True))
```
```text
<html><head><title>Home - Blog</title></head>
<body>
<nav><a href="/">Home</a></nav>
<h1>Welcome</h1>
<footer>(c) 2026</footer>
</body></html>
<html><head><title>About - Blog</title></head>
<body>
<nav><a href="/">Home</a></nav>

<h1>About</h1>
<p>extra</p>

<footer>(c) 2026</footer>
</body></html>
```

Notes: a child contains *only* `extends` and block definitions, because content outside blocks is ignored. `{{ super() }}` includes the parent's version of the block. `{% include "partial.html" %}` pastes another template in place (good for small repeated pieces like a pager).

### 7.2 Macros: functions for HTML

A **macro** is a reusable template function. Put macros in their own file and import them:

```python
from flask import Flask, render_template_string
from jinja2 import DictLoader

app = Flask(__name__)
app.jinja_loader = DictLoader({
    "_macros.html": """\
{% macro field(name, label, type="text", value="") -%}
<label>{{ label }} <input name="{{ name }}" type="{{ type }}" value="{{ value }}"></label>
{%- endmacro %}""",
})

with app.app_context():
    print(render_template_string("""\
{% from "_macros.html" import field %}
{{ field("username", "Name", value=old) }}
{{ field("password", "Password", type="password") }}""", old='Asha "A"'))
```
```text

<label>Name <input name="username" type="text" value="Asha &#34;A&#34;"></label>
<label>Password <input name="password" type="password" value=""></label>
```

The `value` is escaped inside the macro (`&#34;`). Macros are the right tool for form fields, buttons and cards. (Here we used `DictLoader` to keep the demo in memory; in a real project the macros live in `templates/_macros.html`.)

### 7.3 Static files and `url_for('static', ...)`

Flask serves the `static/` folder at `/static/<path>`. In templates, never write `/static/style.css`; use `url_for`, so the URL stays right if the app is mounted under a prefix or you change the static URL.

In a template: `<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">`.

```python
from pathlib import Path
from flask import Flask

Path("static").mkdir()
Path("static/style.css").write_text("body { margin: 0 }\n")
app = Flask(__name__)

with app.test_request_context():
    from flask import url_for
    print(url_for("static", filename="style.css"))

r = app.test_client().get("/static/style.css")
print(r.status_code, r.content_type, r.get_data(as_text=True).strip())
print(app.test_client().get("/static/../app.py").status_code)
```
```text
/static/style.css
200 text/css; charset=utf-8 body { margin: 0 }
404
```

The built-in static route is meant for development. In production a web server such as nginx serves `static/` directly, and the Python process never sees those requests. Flask refuses `..` path tricks (the last line).

### 7.4 Predict the output

```python
from flask import Flask, render_template_string
app = Flask(__name__)
with app.app_context():
    print(render_template_string("{{ a }}|{{ a|safe }}|{{ b|default('x') }}|{{ c|length }}",
                                 a="<i>", b=None, c=[1, 2, 3]))
```

<details><summary>Answer</summary>

```text
&lt;i&gt;|<i>|None|3
```

`a` is escaped, `a|safe` is not. The surprise is `b`: `default` replaces only **undefined** variables, and `b` is defined (it is `None`), so `None` prints as the text `None`. Use `b|default('x', true)` to replace any falsy value.
</details>


## 8. Forms by hand: GET, POST, redirect and flash

### 8.1 The shape of every form handler

Browsers send forms as `application/x-www-form-urlencoded` (or `multipart/form-data` with files). The standard handler has four parts:

```text
   GET  /new        -> show an empty form                         (200)
   POST /new        -> read request.form
                       invalid?  -> show the form again + errors   (400 or 200)
                       valid?    -> change state, then REDIRECT    (302/303)
   GET  /thing/5    -> the page the redirect pointed to           (200)
```

That last arrow, redirecting after a successful POST, has a name.

### 8.2 Post/Redirect/Get (PRG)

If a `POST` handler returns a page directly and the user presses *refresh*, the browser asks "send the form again?" and a second click creates a second order. If instead the handler answers `303 See Other` (or `302`) with a `Location`, the browser follows with a harmless `GET`; refresh then repeats only the `GET`. **Always redirect after a successful state change.** The flash message (next section) tells the user what happened.

### 8.3 Flash messages

`flash("text")` stores a message in the **session** (a signed cookie, section 16); `get_flashed_messages()` in a template reads and *removes* them, so each message shows once, on the next page.

```python
from flask import Flask, flash, redirect, render_template_string, request, url_for

app = Flask(__name__)
app.secret_key = "demo-only"                 # sessions need a secret (section 12)
NOTES = []

PAGE = """\
{% for m in get_flashed_messages() %}FLASH: {{ m }}
{% endfor %}notes: {{ notes|join(', ') }}
<form method="post">...</form>"""

@app.route("/notes", methods=["GET", "POST"])
def notes():
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if not text:
            flash("Write something first.")
            return render_template_string(PAGE, notes=NOTES), 400
        NOTES.append(text)
        flash("Saved.")
        return redirect(url_for("notes"))            # PRG
    return render_template_string(PAGE, notes=NOTES)

c = app.test_client()
r = c.post("/notes", data={"text": "buy milk"})
print(r.status_code, r.headers["Location"])
print(c.get("/notes").get_data(as_text=True))
print(c.get("/notes").get_data(as_text=True))        # the flash is gone
r = c.post("/notes", data={"text": "  "})
print(r.status_code)
```
```text
302 /notes
FLASH: Saved.
notes: buy milk
<form method="post">...</form>
notes: buy milk
<form method="post">...</form>
400
```

Two things to notice. After the `POST` the *next* `GET` shows `FLASH: Saved.`, and the one after shows nothing. And the failed POST returned `400` with the form again, without a redirect: when the input is **invalid** we want to show the user's input and the errors on the same response.

The `flash` call also accepts a category (`flash("x", "error")`) which you read with `get_flashed_messages(with_categories=True)` to choose a CSS class.

After a validation error, put the submitted values back in the form (`value="{{ request.form.get('title', '') }}"`), but never the password.

### 8.4 Try it

Predict the status codes and bodies:

```python
from flask import Flask, request, redirect
app = Flask(__name__)

@app.post("/vote")
def vote():
    if "choice" not in request.form:
        return "missing", 400
    return redirect("/thanks", code=303)

@app.get("/thanks")
def thanks(): return "thanks"

c = app.test_client()
r = c.post("/vote", data={"choice": "a"})
print(r.status_code, r.headers["Location"])
r = c.post("/vote", data={"choice": "a"}, follow_redirects=True)
print(r.status_code, r.get_data(as_text=True), len(r.history))
print(c.post("/vote").status_code)
```

<details><summary>Answer</summary>

```text
303 /thanks
200 thanks 1
400
```

The first call stops at the redirect. With `follow_redirects=True` the client makes the follow-up `GET /thanks`; `r.history` holds the redirect response, so its length is 1.
</details>

## 9. Validation and CSRF

### 9.1 Validation rules of thumb

1. **The browser's checks (`required`, `type="email"`) are a convenience, not security.** Anyone can send a request with `curl`. The server must check everything again.
2. Validate *shape* first (is it present, a string, the right length), then *business rules* (is the username free).
3. Collect **all** errors and show them together, instead of stopping at the first.
4. Return `400` or `422` for invalid input, not `200`, so tests and API clients can tell.
5. Strip whitespace on text fields; do not silently "fix" values that carry meaning (passwords are never stripped).
6. Use the database for uniqueness (a `UNIQUE` constraint), because two requests can pass your "is it free?" check at the same moment (swe.03 sections 6 and 7). The check gives a friendly message; the constraint gives the guarantee.

```python
from flask import Flask, request

app = Flask(__name__)
TAKEN = {"admin", "root"}

def validate_signup(form):
    errors = {}
    username = form.get("username", "").strip()
    email = form.get("email", "").strip()
    password = form.get("password", "")
    if not 3 <= len(username) <= 20:
        errors["username"] = "3 to 20 characters"
    elif username.lower() in TAKEN:
        errors["username"] = "already taken"
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        errors["email"] = "looks wrong"
    if len(password) < 8:
        errors["password"] = "at least 8 characters"
    return errors

@app.post("/signup")
def signup():
    errors = validate_signup(request.form)
    if errors:
        return {"errors": errors}, 422
    return {"ok": True}, 201

c = app.test_client()
r = c.post("/signup", data={"username": "ad", "email": "nope", "password": "x"})
print(r.status_code, r.get_json())
r = c.post("/signup", data={"username": "Admin", "email": "a@b.c", "password": "longenough"})
print(r.status_code, r.get_json())
r = c.post("/signup", data={"username": "asha", "email": "a@b.c", "password": "longenough"})
print(r.status_code, r.get_json())
```
```text
422 {'errors': {'email': 'looks wrong', 'password': 'at least 8 characters', 'username': '3 to 20 characters'}}
422 {'errors': {'username': 'already taken'}}
201 {'ok': True}
```

For larger apps people use libraries (WTForms through Flask-WTF for forms, `pydantic` or `marshmallow` for JSON). Writing a validator function by hand first, as above, teaches what those libraries automate.

### 9.2 CSRF: the problem

Cookies are sent **automatically** by the browser to a site, no matter which page caused the request. Imagine you are logged in to `blog.example` (your session cookie is stored). You then open `evil.example`, which contains this hidden form:

```html
<form action="https://blog.example/post/5/delete" method="post" id="f"></form>
<script>document.getElementById("f").submit()</script>
```

Your browser sends the `POST` to the blog **with your session cookie**. The blog sees a valid logged-in user and deletes the post. This is **Cross-Site Request Forgery**. The attacker could not read anything; they only made your browser *act*. The defences:

1. **`SameSite` cookies** (section 16.5): `Lax` stops the browser sending the cookie on cross-site `POST`s. It is a strong modern default, but not universal enough to rely on alone.
2. **A CSRF token**: a random value, stored in the user's session and also placed in every form as a hidden field. The server compares them. The attacker's page cannot read the token (the browser's same-origin rule stops it) so it cannot forge a valid request.

```text
   GET /form  --->  server creates token T, stores it in session cookie, puts T in the HTML
   POST /form <---  browser sends cookie (with T inside) + hidden field T
                    server: field T == session T ?  yes -> go on   no -> 400
   evil.example POST ->  browser sends the cookie, but the attacker has no T to put in the form -> 400
```

### 9.3 A hand-rolled CSRF check

This is the same code the project uses. Safe methods (`GET`, `HEAD`, `OPTIONS`) must not change state, so they are exempt; every other method needs the token, either in the form field or in an `X-CSRF-Token` header (for JavaScript clients).

```python
import secrets
from flask import Flask, abort, request, session, render_template_string

app = Flask(__name__)
app.secret_key = "demo-only"

def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]

@app.before_request
def check_csrf():
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
    expected = session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(sent, expected):
        abort(400, description="Bad or missing CSRF token.")

app.jinja_env.globals["csrf_token"] = csrf_token       # usable in every template

@app.get("/form")
def form():
    return render_template_string(
        '<form method="post"><input type="hidden" name="csrf_token" value="{{ csrf_token() }}"></form>')

@app.post("/delete")
def delete():
    return "deleted"

c = app.test_client()
print("forged:", c.post("/delete").status_code)                    # no token at all
html = c.get("/form").get_data(as_text=True)
token = html.split('value="')[1].split('"')[0]
print("token length:", len(token))
print("wrong:", c.post("/delete", data={"csrf_token": "0" * 32}).status_code)
print("right:", c.post("/delete", data={"csrf_token": token}).status_code)
print("header:", c.post("/delete", headers={"X-CSRF-Token": token}).status_code)
```
```text
forged: 400
token length: 32
wrong: 400
right: 200
header: 200
```

Details worth knowing:

- `secrets.token_hex(16)` makes a 128-bit random value from the operating system's secure source. Never use `random` for tokens.
- `secrets.compare_digest` compares in constant time, so an attacker cannot learn the token one character at a time from response timings.
- The token lives in the **session**, so it changes when the session is cleared (login, logout). That is correct, but it means your tests must fetch a fresh token after logging in (section 21).
- Hidden-field tokens in forms need one line per form. Flask-WTF does it with `{{ form.hidden_tag() }}` (section 23).
- JSON APIs that use **tokens in the `Authorization` header** (not cookies) are not vulnerable to CSRF, because browsers do not add that header automatically. The risk exists only when the credential is a cookie.

> **When SameSite is enough.** With `SESSION_COOKIE_SAMESITE = "Lax"` modern browsers already refuse to send the session cookie on a cross-site `POST`. A token is still the standard, because it protects older browsers, and "same-site" is looser than "same-origin" (sibling subdomains count as same-site).


## 10. Contexts: application, request, `g`

### 10.1 The puzzle

In a view you write `from flask import request` and use `request.args` as if it were a global variable. But a server handles many requests at the same time, in different threads. How can one global name refer to a different request in each thread?

The answer is the **context**. Flask keeps, per thread (or per async task), a stack of "what is happening right now". `request`, `session`, `g` and `current_app` are **proxies** (stand-ins): when you use `request.args`, the proxy looks up the current request object and forwards the access to it. There are two kinds of context:

| Context | Lives for | Provides |
|---|---|---|
| **Application context** | one request, one CLI command, or a `with app.app_context()` block | `current_app`, `g` |
| **Request context** | one request | `request`, `session` (and an app context is pushed with it) |

### 10.2 Working outside a context

The most common error message of a new Flask developer is "Working outside of application context" or "of request context". It means you used a proxy when nothing was active, for example in a plain script or at import time.

```python
from flask import Flask, current_app, g, request

app = Flask(__name__)
app.config["GREETING"] = "hello"

try:
    print(current_app.config["GREETING"])
except RuntimeError as e:
    print("1:", str(e).splitlines()[0])

with app.app_context():                    # application context: current_app and g work
    print("2:", current_app.config["GREETING"])
    try:
        print(request.path)
    except RuntimeError as e:
        print("3:", str(e).splitlines()[0])

with app.test_request_context("/hello?x=1"):   # request context: request and session work too
    print("4:", request.path, request.args["x"], current_app.name == app.name)
```
```text
1: Working outside of application context.
2: hello
3: Working outside of request context.
4: /hello 1 True
```

Rules you can rely on:

- **Inside a view, a hook, a template, an error handler**: everything is available.
- **In a script, a test, a `flask shell` or a background job**: push a context yourself: `with app.app_context():` (for the database, `current_app`, `g`) or `with app.test_request_context(...):` (for `url_for`, `request`).
- The ORM session of Flask-SQLAlchemy needs an application context, which is why tests and scripts wrap database work in `with app.app_context():`.
- A **thread you start yourself does not inherit the context**. Pass plain values (not `request`) to the thread and push a context inside it.

### 10.3 `g`: per-request scratch space

`g` is an empty object created fresh for each application context. Use it to share values between code that runs during **one** request: the current user, a database connection, a start time. It is *not* storage between requests; the next request gets a new `g`.

```python
import time
from flask import Flask, g

app = Flask(__name__)
LOG = []

@app.before_request
def start():
    g.started = 1                 # (a real app would use time.perf_counter())
    g.user = "alice"

def helper():
    return f"helper sees {g.user}"      # no argument passing needed

@app.get("/")
def home():
    LOG.append(helper())
    return "ok"

@app.teardown_request
def finish(exc):                   # runs at the very end, even after errors
    LOG.append(f"teardown, started={g.started}, error={exc!r}")

app.test_client().get("/")
print(LOG)
```
```text
['helper sees alice', 'teardown, started=1, error=None']
```

Use `g` sparingly. Passing values as function arguments is clearer; use `g` for things that genuinely belong to the request as a whole, like the loaded user. A common idiom is `g.db` opened on demand and closed in `@app.teardown_appcontext`; Flask-SQLAlchemy does this for you (section 14).

### 10.4 `current_app` and teardown

In a blueprint or helper module you cannot import `app` (it may not exist yet; section 11), so use `current_app`, the proxy for "the application handling this request": `current_app.config["POSTS_PER_PAGE"]`, `current_app.logger.info(...)`. Hooks: `before_request` runs before each view (load user, check CSRF); `after_request` after it (add headers); `teardown_request` and `teardown_appcontext` always run at the end (release resources; Flask-SQLAlchemy closes its session there).

## 11. The application factory

### 11.1 The problem with `app = Flask(__name__)` at module level

In a one-file app you create `app` when the module is imported. As the app grows, this creates three problems:

1. **Circular imports.** `models.py` needs `db`, which needs `app`; `views.py` needs `app` for the decorators and `models`; `app.py` imports `views`... Python raises `ImportError` or `NameError` depending on import order.
2. **One configuration.** Tests need an in-memory database and `TESTING=True`; production needs a real URL. With a global `app`, you must change environment variables before importing anything.
3. **One app per process.** You cannot make two differently configured apps to compare in a test.

The fix is the **application factory**: a function that builds and returns the app.

```python
def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)                      # extensions are created elsewhere, attached here
    app.register_blueprint(blog.bp)
    return app
```

### 11.2 The recipe

```text
   extensions.py   db = SQLAlchemy()            created WITHOUT an app
   models.py       from .extensions import db   no app needed to define models
   blog.py         bp = Blueprint(...)          routes attach to bp, not to app
   __init__.py     create_app():
                      app = Flask(...)
                      app.config.from_object(config)
                      db.init_app(app)           <- extension meets app here
                      app.register_blueprint(bp) <- routes meet app here
                      return app
```

Everything that needs the app is done inside `create_app`; everything else is importable without an app. Order of imports no longer matters, because nothing runs at import time.

### 11.3 Two apps, two configurations, one process

```python
from flask import Flask, current_app

class Config:
    GREETING = "hello"
    DEBUG = False

class TestConfig(Config):
    GREETING = "test hello"
    TESTING = True

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    @app.get("/")
    def home():
        return current_app.config["GREETING"]

    return app

a, b = create_app(), create_app(TestConfig)
print(a.test_client().get("/").get_data(as_text=True), "|", a.testing)
print(b.test_client().get("/").get_data(as_text=True), "|", b.testing)
```
```text
hello | False
test hello | True
```

Each call returns an independent app. This is why testing a factory-built app is easy: every test can have its own fresh app (section 21).

### 11.4 Running a factory

`flask --app app run` finds `create_app` in the package `app` and calls it with no arguments, so the config is chosen by an environment variable. For Gunicorn: `gunicorn "app:create_app()"`.

## 12. Configuration and secrets

### 12.1 What configuration is

**Configuration** is every value that differs between where the app runs (your laptop, the tests, the server) without changing the code: database URL, secret key, debug flag, page size. Flask keeps them in `app.config`, a dict with upper-case keys. The twelve-factor rule: **configuration lives in the environment, code lives in the repository**.

### 12.2 Ways to fill `app.config`

```python
import os
from flask import Flask

app = Flask(__name__)

app.config["DEBUG"] = False                              # 1. plain assignment
app.config.update(POSTS_PER_PAGE=5, SITE="Mini Blog")    # 2. update with keywords
app.config.from_mapping(SECRET_KEY="dev")                # 3. from a dict (keyword form too)

class Config:                                            # 4. from an object: only UPPER-case names count
    DATABASE = "sqlite:///blog.db"
    lowercase_ignored = 1

app.config.from_object(Config)

os.environ["BLOG_PAGE_TITLE"] = "From the environment"   # 5. from environment variables with a prefix
os.environ["BLOG_POSTS_PER_PAGE"] = "20"
app.config.from_prefixed_env("BLOG")                     # strips "BLOG_", parses values as JSON

for key in ("DEBUG", "SITE", "SECRET_KEY", "DATABASE", "POSTS_PER_PAGE", "PAGE_TITLE"):
    print(f"{key:15} {app.config.get(key)!r}")
print("lowercase_ignored" in app.config)
```
```text
DEBUG           False
SITE            'Mini Blog'
SECRET_KEY      'dev'
DATABASE        'sqlite:///blog.db'
POSTS_PER_PAGE  20
PAGE_TITLE      'From the environment'
False
```

Notice `POSTS_PER_PAGE` became the **int** `20`, not the string `"20"`: `from_prefixed_env` parses each value as JSON, so `true`, `5` and `["a"]` come through typed. With plain `os.environ.get(...)` you get strings and must convert yourself (`int(os.environ.get("X", "5"))`). A classic bug is `DEBUG = os.environ.get("DEBUG")`: the string `"False"` is truthy.

### 12.3 Config classes per environment

```python
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

class DevConfig(Config):
    DEBUG = True

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"            # in memory

class ProdConfig(Config):
    SESSION_COOKIE_SECURE = True                     # only over HTTPS

CONFIGS = {"dev": DevConfig, "test": TestConfig, "prod": ProdConfig}

def pick_config(name=None):
    return CONFIGS[name or os.environ.get("APP_ENV", "dev")]

print(pick_config().__name__)
os.environ["APP_ENV"] = "prod"
print(pick_config().__name__, pick_config().SESSION_COOKIE_SECURE)
print(pick_config("test").SQLALCHEMY_DATABASE_URI)
```
```text
DevConfig
ProdConfig True
sqlite://
```

### 12.4 The secret key

`SECRET_KEY` signs the session cookie (section 16). Whoever knows it can forge any session, including "I am user 1, the admin". So:

- Make it long and random: `python -c "import secrets; print(secrets.token_hex(32))"`.
- **Never commit it.** Not in `config.py`, not in a "private" repo; repos get shared. Put it in the environment or a file outside version control.
- Different keys per environment. Rotating the key logs everyone out, which is the correct emergency response after a leak.
- A hard-coded dev key like `"dev"` in code is fine **only if production refuses to start with it**.

> ### Try it on your machine: a `.env` file
> Many projects keep local settings in a file named `.env` (listed in `.gitignore`) and load it with `python-dotenv`. Flask's `flask run` reads `.env` and `.flaskenv` automatically if the package is installed:
>
> ```text
> pip install python-dotenv
> printf 'SECRET_KEY=%s\nDATABASE_URL=sqlite:///dev.db\n' "$(python -c 'import secrets;print(secrets.token_hex(32))')" > .env
> echo ".env" >> .gitignore
> ```
>
> Then `flask --app app run` sees `SECRET_KEY` through `os.environ`. A `.env.example` with empty values **is** committed, so teammates know which variables exist. The output is the normal start-up lines; the secret itself is never printed.

### 12.5 The instance folder

Flask can also use an **instance folder** next to your package, outside version control, for files that belong to one installation (a SQLite file, a `config.py` with secrets): `Flask(__name__, instance_relative_config=True)` then `app.config.from_pyfile("config.py", silent=True)`. On hosts with temporary disks that folder disappears on redeploy, so real data belongs in a database (swe.03). The environment works everywhere, so prefer it for secrets.

### 12.6 Predict the output

```python
from flask import Flask
app = Flask(__name__)

class C:
    A = 1
    b = 2
    C_ = 3

app.config.from_object(C)
app.config.from_mapping({"A": 10}, X=5)
print(app.config["A"], app.config.get("b"), app.config["C_"], app.config["X"])
```

<details><summary>Answer</summary>

```text
10 None 3 5
```

`from_object` copies only UPPER-case names, so `b` is ignored (`None`) and `C_` is kept (`"C_".isupper()` is true). `from_mapping` runs later and overrides `A`. Later sources win.
</details>

## 13. Blueprints

### 13.1 Why

One file with fifty routes is hard to navigate. A **blueprint** is a bundle of routes, templates and hooks that belongs to one part of the app (authentication, blog, API, admin). You write routes on the blueprint with `@bp.route`, as if it were an app, and register the blueprint on the real app in the factory. Think of it as a "mini-app" plus a **namespace**: endpoint names get the blueprint's name as a prefix.

```text
   create_app()
       |
       +-- register_blueprint(auth.bp,  url_prefix="/auth")
       |        /auth/login      endpoint  auth.login
       |        /auth/register   endpoint  auth.register
       |
       +-- register_blueprint(blog.bp)
       |        /               endpoint  blog.index
       |        /post/<id>       endpoint  blog.show
       |
       +-- register_blueprint(api.bp,   url_prefix="/api")
                /api/posts       endpoint  api.list_posts
```

### 13.2 A runnable example

```python
from flask import Blueprint, Flask, render_template_string, url_for

auth = Blueprint("auth", __name__, url_prefix="/auth")
blog = Blueprint("blog", __name__)

@auth.get("/login")
def login():
    return "login page"

@auth.get("/logout")
def logout():
    return "bye"

@blog.get("/")
def index():
    return f"home; login is at {url_for('auth.login')}; I am {url_for('.index')}"

@blog.get("/post/<int:post_id>")
def show(post_id):
    return f"post {post_id}"

def create_app():
    app = Flask(__name__)
    app.register_blueprint(auth)
    app.register_blueprint(blog)
    return app

app = create_app()
c = app.test_client()
print(c.get("/").get_data(as_text=True))
print(c.get("/auth/login").get_data(as_text=True))
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.endpoint):
    if rule.endpoint != "static":
        print(f"{rule.endpoint:14} {rule.rule}")
```
```text
home; login is at /auth/login; I am /
login page
auth.login     /auth/login
auth.logout    /auth/logout
blog.index     /
blog.show      /post/<int:post_id>
```

What to notice:

- `url_for("auth.login")` uses `blueprint.function`. Inside the *same* blueprint, `url_for(".index")` (leading dot) is a shortcut.
- The prefix is given once, at the blueprint or at registration (`app.register_blueprint(auth, url_prefix="/account")` overrides it). Moving the whole section to another URL is a one-word change.
- In a template, `url_for('blog.show', post_id=p.id)`: the endpoint name must carry the blueprint name. Forgetting it gives `BuildError: Could not build url for endpoint 'show'`.

### 13.3 What else a blueprint can own

- **Hooks only for its routes**: `@bp.before_request` runs only for this blueprint's views (an `/admin` blueprint can require a login this way). `@bp.before_app_request` runs for *all* requests.
- **Error handlers**: `@bp.errorhandler(404)` for its own routes; `@bp.app_errorhandler(404)` for the whole app.
- **Templates and static files**: `Blueprint("blog", __name__, template_folder="templates")`. Templates in a blueprint folder share a global namespace with the app's, so a common convention is `templates/blog/index.html` and `render_template("blog/index.html")` to avoid two `index.html` files colliding. The project does exactly that.
- **CLI commands**: `bp.cli.command("seed")`.

For example, an `/admin` blueprint can require a login with one `@admin.before_request` that calls `abort(403)`, and `@admin.errorhandler(403)` gives it its own error page.

### 13.4 Rule of thumb

Split by **feature** (auth, blog, api), not by layer. Shared things (`db`, security helpers, error handlers) sit at the top of the package so blueprints never import each other.


## 14. Flask-SQLAlchemy

### 14.1 What the extension adds to SQLAlchemy

swe.03 taught SQLAlchemy 2.x: engine, `Session`, `select()`, mapped classes. **Flask-SQLAlchemy** (version 3.1) does not replace any of that. It removes boilerplate for web apps:

- Creates the engine from `app.config["SQLALCHEMY_DATABASE_URI"]`.
- Provides **`db.session`**, a session scoped to the current application context, and **removes it automatically** when the request ends (so no leaked sessions or connections).
- Provides the base class `db.Model`, with a default table name (`User` becomes `user`).
- Adds helpers: `db.get_or_404`, `db.first_or_404`, `db.one_or_404`, `db.paginate`, `db.create_all()`.

Connect it like every extension: create `db` without an app, call `db.init_app(app)` in the factory.

### 14.2 Defining models

```python
from datetime import datetime, timezone
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)          # the 2.x style: you own the Base


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped[User] = relationship(back_populates="posts")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"     # in memory: gone when the process ends
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

app = create_app()
with app.app_context():
    print(User.__tablename__, Post.__tablename__)
    print(sorted(db.metadata.tables))
    print([c.name for c in Post.__table__.columns])
```
```text
user post
['post', 'user']
['id', 'title', 'author_id']
```

Points:

- `Mapped[int]` is the Python type, `mapped_column(...)` adds database details. `Mapped[str]` is `NOT NULL`; write `Mapped[str | None]` for a nullable column.
- The table name is the snake-case class name: `user`, `post`. A multi-word class `BlogPost` becomes `blog_post`. That is why the foreign key is `ForeignKey("user.id")`.
- `db.create_all()` needs an application context (it needs to know which app's engine to use) and creates **missing** tables only. It never alters existing ones, so changing a column later needs a migration (swe.03 section 13, and Flask-Migrate in section 23).
- `"sqlite://"` (no path) is an in-memory database. Flask-SQLAlchemy uses a single shared connection for it so tables survive between sessions, which is what makes in-memory test databases work.

### 14.3 Create, read, update, delete

```python
with app.app_context():
    alice = User(username="alice")
    bob = User(username="bob")
    db.session.add_all([alice, bob])
    db.session.add(Post(title="Hello", author=alice))
    db.session.add(Post(title="Second", author=alice))
    db.session.commit()                                   # one transaction

    users = db.session.scalars(select(User).order_by(User.username)).all()
    print([u.username for u in users])

    post = db.session.get(Post, 1)                        # by primary key
    print(post.title, "by", post.author.username)

    post.title = "Hello, world"                           # change an attribute...
    db.session.commit()                                   # ...commit writes the UPDATE

    found = db.session.scalar(select(User).where(User.username == "bob"))
    print(found.username, len(found.posts))

    db.session.delete(db.session.get(Post, 2))
    db.session.commit()
    print(db.session.scalar(select(db.func.count()).select_from(Post)))
```
```text
['alice', 'bob']
Hello by alice
bob 0
1
```

The same four steps as swe.03: `add`, `commit`, `select`, change-and-commit. The only difference is that `db.session` is a property of the extension and is tied to the application context.

### 14.4 The 404 helpers

A route that loads one row should answer 404 if it does not exist: `db.get_or_404(Post, post_id)` for a primary key, `db.one_or_404(select(User).filter_by(username=name))` for a query. They call `abort(404)` for you.

### 14.5 Pagination

`db.paginate(select_stmt, page=..., per_page=...)` runs a `LIMIT/OFFSET` query plus a `COUNT`, and returns a `Pagination` object that is ready for templates.

```python
with app.app_context():
    db.session.add_all(Post(title=f"P{i}", author_id=1) for i in range(1, 13))
    db.session.commit()

    p = db.paginate(select(Post).order_by(Post.id), page=2, per_page=5, error_out=False)
    print("page", p.page, "of", p.pages, "| total", p.total)
    print([post.title for post in p.items])
    print("has_prev", p.has_prev, "has_next", p.has_next, "| prev", p.prev_num, "next", p.next_num)
    print(list(p.iter_pages()))
    past = db.paginate(select(Post).order_by(Post.id), page=99, per_page=5, error_out=False)
    print(past.items, past.page)
```
```text
page 2 of 3 | total 13
['P5', 'P6', 'P7', 'P8', 'P9']
has_prev True has_next True | prev 1 next 3
[1, 2, 3]
[] 99
```

With the default `error_out=True`, a page number beyond the last gives a 404; with `False` you get an empty page. If you do not pass `page`, Flask-SQLAlchemy reads `?page=` from the request itself. Always `order_by` in a paginated query, or rows can repeat between pages (swe.03).

### 14.6 N+1, once more, in a Flask setting

Looping `for post in posts: post.author.username` in a template is the classic N+1: one query for the posts, then one per post for its author (swe.03 section 10). Count them:

```python
from sqlalchemy import event
from sqlalchemy.orm import selectinload

counter = {"n": 0}

with app.app_context():
    for name in ("carol", "dave", "erin", "frank"):          # more authors, one post each
        db.session.add(Post(title=f"By {name}", author=User(username=name)))
    db.session.commit()
    db.session.expire_all()

    @event.listens_for(db.engine, "before_cursor_execute")
    def count_queries(conn, cursor, statement, parameters, context, executemany):
        counter["n"] += 1

    counter["n"] = 0
    for post in db.session.scalars(select(Post)).all():
        post.author.username
    print("lazy loading:  ", counter["n"], "queries")
    db.session.expire_all()

    counter["n"] = 0
    for post in db.session.scalars(select(Post).options(selectinload(Post.author))).all():
        post.author.username
    print("selectinload:  ", counter["n"], "queries")
```
```text
lazy loading:   6 queries
selectinload:   2 queries
```

Lazy loading cost 1 query for the posts plus 1 per *distinct* author (the session remembers authors it already loaded, so alice is fetched once). With a thousand different authors that would be 1,001 queries; `selectinload` stays at 2. The fix is the one you know: `selectinload(Post.author)` (used in the project's `index` view).

### 14.7 Errors and rollback

If a flush fails (for example a `UNIQUE` violation), the session is in a "needs rollback" state and every further use raises an error until you call `db.session.rollback()`.

```python
from sqlalchemy.exc import IntegrityError

with app.app_context():
    db.session.add(User(username="alice"))               # duplicate!
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()                            # clean the session
        print("duplicate rejected:", type(exc.orig).__name__)
    print(db.session.scalar(select(db.func.count()).select_from(User)))
```
```text
duplicate rejected: IntegrityError
6
```

In a view, catch `IntegrityError`, roll back, and answer with a clear 409 or a form error. Do not let a database exception turn into a 500 with a stack trace for something a user can cause.

### 14.8 Predict the output

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase): pass
db = SQLAlchemy(model_class=Base)

class Note(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str]

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
db.init_app(app)

with app.app_context():
    db.create_all()
    n = Note(text="a")
    print(n.id)
    db.session.add(n)
    print(n.id)
    db.session.flush()
    print(n.id)
    db.session.rollback()
    print(db.session.scalar(db.select(db.func.count()).select_from(Note)))
```

<details><summary>Answer</summary>

```text
None
None
1
0
```

Before the `flush` there is no row, so no id, even after `add`. `flush` sends the `INSERT` (inside the still-open transaction) and the database assigns the id. `rollback` undoes it, so the table is empty.
</details>

## 15. Passwords and hashing

### 15.1 The rule

**Never store a password. Store a hash of it.** If the database leaks (it happens to large companies), the attacker has hashes, not passwords; and users who reuse passwords on other sites are not endangered.

A password hash must be:

- **One-way**: you cannot compute the password from the hash.
- **Salted**: a random value mixed in, different per user, stored with the hash. Two users with the same password get different hashes, and precomputed tables ("rainbow tables") are useless.
- **Slow on purpose**: an ordinary hash such as SHA-256 is built for speed, so a graphics card tests billions of guesses per second. Password hashes (scrypt, bcrypt, argon2, PBKDF2) are designed to use a lot of time and memory per guess, so each guess is expensive.

Do not invent your own scheme (`sha256(password + "salt")` is wrong in several ways). Use `werkzeug.security`, which is installed with Flask.

```python
from werkzeug.security import check_password_hash, generate_password_hash

h1 = generate_password_hash("correct horse battery")
h2 = generate_password_hash("correct horse battery")

print(h1.split("$")[0])                         # the algorithm and its cost settings
print(len(h1) > 60)
print("same password, different hashes:", h1 != h2)    # because the salt is random
print("good:", check_password_hash(h1, "correct horse battery"))
print("good (other hash):", check_password_hash(h2, "correct horse battery"))
print("bad:", check_password_hash(h1, "correct horse batter"))
```
```text
scrypt:32768:8:1
True
same password, different hashes: True
good: True
good (other hash): True
bad: False
```

(The hash text itself contains random salt bytes, so it is different on every run; we only print its stable parts.) The format is `method$salt$hash`: everything needed to check a password later is inside the one string you store, which is why a single `password_hash` column is enough. `check_password_hash` reads the method and salt from the stored string, hashes the candidate the same way, and compares in constant time.

### 15.2 Practical rules

- Column length: use at least 256 characters for `password_hash`; the algorithm may change and hashes grow.
- Enforce a minimum length (8 or more); long passphrases beat complex short ones. Do not truncate or strip passwords.
- Hashing is deliberately slow (tens of milliseconds): it is a deliberate cost on every login. In tests, it makes a suite slower if you create hundreds of users; create a few and reuse them.
- **Same error for "no such user" and "wrong password"** ("Wrong username or password."), otherwise your login form tells attackers which usernames exist.
- Never log passwords, never email them, never put them in a URL, and never put the hash in an API response.
- A "forgot password" flow sends a **single-use, expiring token** by email (`itsdangerous.URLSafeTimedSerializer` makes one), never the old password.

### 15.3 Try it

Why is `hashlib.sha256(password.encode()).hexdigest()` a poor way to store passwords, even though it is "a hash"? Name two reasons.

<details><summary>Answer</summary>

1. It is **fast**, so an attacker can try billions of guesses per second against a leaked table.
2. It is **unsalted**, so identical passwords give identical hashes (visible in the table), and precomputed lists of common passwords can be matched instantly.

`generate_password_hash` fixes both: a random salt per password and a deliberately expensive algorithm.
</details>

## 16. Session-based authentication

### 16.1 The idea

HTTP forgets you between requests (swe.02 section 12). To stay logged in, the server gives the browser an **identifier** at login and the browser sends it back every time:

```text
   POST /auth/login  (username, password)
        server: check password hash; OK
        server: session["user_id"] = 7
        <--- 302  Set-Cookie: session=<signed data>; HttpOnly; SameSite=Lax

   GET /post/new   Cookie: session=<signed data>
        before_request: user = db.get(User, session["user_id"])
        view runs knowing g.user
```

Flask's `session` is a dict-like object. Its default storage is **the cookie itself**: the data is serialised to JSON, **signed** with `SECRET_KEY` (using `itsdangerous`), and sent to the browser. Nothing is stored on the server.

### 16.2 What is inside the cookie

The cookie is signed, **not encrypted**. Anyone can read it; nobody can change it without the key. Look at one:

```python
import base64, json
from flask import Flask, session

app = Flask(__name__)
app.secret_key = "demo-secret"

@app.get("/login")
def login():
    session["user_id"] = 7
    session["note"] = "visible to the user"
    return "ok"

@app.get("/me")
def me():
    return f"user_id={session.get('user_id')}"

c = app.test_client()
c.get("/login")
cookie = c.get_cookie("session").value
payload, timestamp, signature = cookie.split(".")
pad = "=" * (-len(payload) % 4)
print("readable payload:", json.loads(base64.urlsafe_b64decode(payload + pad)))
print("parts:", len(cookie.split(".")), "(payload, timestamp, signature)")
print("untouched:", c.get("/me").get_data(as_text=True))

forged = base64.urlsafe_b64encode(b'{"user_id":1}').decode().rstrip("=")
c.set_cookie("session", f"{forged}.{timestamp}.{signature}")
print("forged:   ", c.get("/me").get_data(as_text=True))

other = app.test_client()
other.set_cookie("session", cookie)
app.secret_key = "a-different-key"
print("new key:  ", other.get("/me").get_data(as_text=True))
```
```text
readable payload: {'note': 'visible to the user', 'user_id': 7}
parts: 3 (payload, timestamp, signature)
untouched: user_id=7
forged:    user_id=None
new key:   user_id=None
```

Three lessons:

1. **Never put secrets in the session** (no passwords, no private data): the user can decode it.
2. A tampered cookie is silently **ignored**: the session is empty, so the user is anonymous. Forging `user_id` needs the key.
3. Changing `SECRET_KEY` invalidates every existing session: everyone is logged out.

Limits of cookie sessions: about 4 KB maximum; the data goes up on every request; and you **cannot revoke** a session on the server (a stolen cookie keeps working until it expires). When you need revocation ("log out everywhere") use server-side sessions (extension Flask-Session, data in Redis or the database) or keep a `session_version` number on the user and compare it on each request.

### 16.3 Login and logout

The whole login flow is: look the user up, check the hash, put `user_id` in the session. Logout clears it.

```python
from flask import Flask, g, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "demo-secret"
USERS = {1: {"id": 1, "name": "alice", "hash": generate_password_hash("s3cret-pass")}}

def find_by_name(name):
    return next((u for u in USERS.values() if u["name"] == name), None)

@app.before_request
def load_user():
    g.user = USERS.get(session.get("user_id"))          # None when not logged in

@app.post("/login")
def login():
    user = find_by_name(request.form.get("username", ""))
    if user is None or not check_password_hash(user["hash"], request.form.get("password", "")):
        return "Wrong username or password.", 401
    session.clear()                  # drop any old session data (section 16.6)
    session["user_id"] = user["id"]
    return redirect(url_for("home"))

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.get("/")
def home():
    return f"hello {g.user['name']}" if g.user else "hello stranger"

c = app.test_client()
print(c.get("/").get_data(as_text=True))
r = c.post("/login", data={"username": "alice", "password": "wrong"})
print(r.status_code, r.get_data(as_text=True))
r = c.post("/login", data={"username": "nobody", "password": "x"})
print(r.status_code, r.get_data(as_text=True))           # same message for unknown user
r = c.post("/login", data={"username": "alice", "password": "s3cret-pass"})
print(r.status_code, r.headers["Location"])
print(c.get("/").get_data(as_text=True))
c.post("/logout")
print(c.get("/").get_data(as_text=True))
```
```text
hello stranger
401 Wrong username or password.
401 Wrong username or password.
302 /
hello alice
hello stranger
```

The user is loaded in a `before_request` hook and put on `g`, so every view and template can use `g.user`. We store only the **id** in the session, never the whole user: the id is small, and the data is read fresh each request (a deleted user is immediately anonymous).

### 16.4 `login_required`, written by hand

A **decorator** (core.13 in the course) wraps a view with a check. This is the essential piece of every authentication system, and it fits in a dozen lines:

```python
from functools import wraps
from flask import Flask, flash, g, redirect, request, session, url_for

app = Flask(__name__)
app.secret_key = "demo-secret"

@app.before_request
def load_user():
    g.user = session.get("user")

def login_required(view):
    @wraps(view)                                   # keep the view's name (endpoint names!)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please log in first.")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped

@app.get("/login")
def login():
    session["user"] = "alice"
    return "logged in"

@app.get("/secret")
@login_required                                    # the route decorator goes OUTSIDE (on top)
def secret():
    return f"secret for {g.user}"

c = app.test_client()
r = c.get("/secret")
print(r.status_code, r.headers["Location"])
c.get("/login")
print(c.get("/secret").get_data(as_text=True))
print(secret.__name__)
```
```text
302 /login?next=/secret
secret for alice
secret
```

Order matters: `@app.get(...)` must be the **outer** decorator, because it registers the function it receives; if `login_required` were outside, the route would register the *unprotected* function. And `@wraps(view)` copies the original name; without it every wrapped view would be called `wrapped`, and registering two of them raises `AssertionError: View function mapping is overwriting an existing endpoint function: wrapped`.

The `next` parameter remembers where the user wanted to go, so after login you send them there. **Validate it**: a link such as `/login?next=https://evil.example/` would otherwise turn your site into an open redirect for phishing. The project's `safe_next` function accepts only a relative path that starts with a single `/` and has no scheme or host.

For API requests, an unauthenticated user should get **401 JSON**, not a redirect to an HTML login page (section 18).

### 16.5 Cookie flags: HttpOnly, Secure, SameSite

These three attributes of `Set-Cookie` (swe.02 section 12) matter most for the session cookie:

| Flag | Effect | Defends against |
|---|---|---|
| `HttpOnly` | JavaScript cannot read the cookie (`document.cookie` hides it) | an XSS bug stealing the session |
| `Secure` | the browser sends it only over HTTPS | stealing it on open networks |
| `SameSite=Lax` | not sent on cross-site `POST`s and embedded requests | CSRF (section 9) |

In Flask they are configuration:

```python
from flask import Flask, session

app = Flask(__name__)
app.secret_key = "demo"
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,       # already the default
    SESSION_COOKIE_SAMESITE="Lax",      # default is None (no SameSite attribute): set it
    SESSION_COOKIE_SECURE=True,         # default False: turn on when you serve HTTPS
    SESSION_COOKIE_NAME="blog_session",
)

@app.get("/")
def home():
    session["x"] = 1
    return "ok"

# Secure cookies are only returned by a client that talks https, so ask for an https URL:
r = app.test_client().get("/", base_url="https://localhost/")
header = r.headers["Set-Cookie"]
print([part.strip() for part in header.split(";")][1:])
```
```text
['Secure', 'HttpOnly', 'Path=/', 'SameSite=Lax']
```

(The first part of the header is the signed value, different for each session, so we print only the flags.) `Secure` is the one you cannot test on `http://localhost`: during local development leave it `False`, and turn it on in the production config class (as the project's `ProdConfig` does).

### 16.6 Session fixation and `session.clear()`

In a **session fixation** attack the attacker obtains a valid session identifier (or sets one in the victim's browser), waits for the victim to log in under it, and then uses the same identifier. The defence is to **issue a new session at login**. With Flask's cookie sessions the identifier is the signed data itself, so `session.clear()` before `session["user_id"] = ...` does the job (the cookie value changes, and so does the CSRF token). It also removes any stale data from the anonymous visit. The same on logout: `session.clear()`, not `session.pop("user_id")`.

### 16.7 "Remember me" and session lifetime

By default the session cookie is a **browser-session cookie**: no expiry, gone when the browser closes. For "remember me", mark the session permanent; it then lives for `PERMANENT_SESSION_LIFETIME` (default 31 days):

```python
from datetime import timedelta
from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = "demo"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)

@app.post("/login")
def login():
    session["user_id"] = 1
    session.permanent = bool(request.form.get("remember"))
    return "ok"

c = app.test_client()
for form in ({}, {"remember": "on"}):
    header = c.post("/login", data=form).headers["Set-Cookie"]
    attrs = [p.strip().split("=")[0] for p in header.split(";")][1:]
    print("remember" if form else "default ", attrs)
```
```text
default  ['HttpOnly', 'Path']
remember ['Expires', 'HttpOnly', 'Path']
```

Choose the lifetime by risk: a banking app uses minutes; a blog can use weeks. The honest trade-off of "remember me" is that a longer-lived cookie is a longer-lived target. Flask-Login (section 23) packages this as a separate "remember" cookie.

### 16.8 Brute force

A login form invites guessing. Defences, cheapest first: a slow hash (section 15), the same message for unknown user and wrong password, **rate limiting** per IP and per username (Flask-Limiter or the proxy), HTTPS everywhere, and an optional second factor.

> **Try it on your machine: seeing the cookie in a browser.** Start the project app (section 24), log in, open the browser developer tools, find *Application* (Chrome) or *Storage* (Firefox), then *Cookies*. You should see a cookie named `session`, flagged `HttpOnly`, with `SameSite` set to `Lax`. In the console, `document.cookie` should **not** list it, because of `HttpOnly`. The exact cookie value is different on every login (it contains a timestamp and signature).

## 17. Authorisation and ownership

### 17.1 Authentication is not authorisation

**Authentication**: who are you? **Authorisation**: what may you do? A logged-in user must not edit someone else's post. The commonest serious web bug is a missing ownership check: the page `/post/5/delete` works for any logged-in user who types the number. This family is called **IDOR** (insecure direct object reference), and it is the top of OWASP's "broken access control" list.

| Situation | Status |
|---|---|
| Not logged in | `401 Unauthorized` (APIs) or a redirect to login (web pages) |
| Logged in, not allowed | `403 Forbidden` |
| Logged in, resource exists but you must not even know | `404 Not Found` |

Using 404 instead of 403 is a good choice when the existence of the resource is itself private (another user's drafts).

### 17.2 A small ownership helper

Write the check **once**, as a function used by every view that changes a resource, so you cannot forget it in one of them. The project's `owned_post_or_403` is:

```python
def owned_post_or_403(post_id):
    post = get_post_or_404(post_id)          # 404 first: no such post
    if post.author_id != g.user.id:
        abort(403, description="You can only change your own posts.")
    return post
```

```python
from flask import Flask, abort, g, request

app = Flask(__name__)
NOTES = {1: {"owner": "alice", "text": "alice's note"}, 2: {"owner": "bob", "text": "bob's note"}}

@app.before_request
def who():
    g.user = request.headers.get("X-User")              # stand-in for the session

def own_note_or_error(note_id):
    note = NOTES.get(note_id) or abort(404)
    if note["owner"] != g.user:
        abort(403)
    return note

@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    if g.user is None:
        abort(401)
    own_note_or_error(note_id)
    del NOTES[note_id]
    return "", 204

c = app.test_client()
print("anonymous delete:", c.delete("/notes/1").status_code)
print("bob deletes alice's:", c.delete("/notes/1", headers={"X-User": "bob"}).status_code)
print("bob deletes missing:", c.delete("/notes/9", headers={"X-User": "bob"}).status_code)
print("bob deletes his own:", c.delete("/notes/2", headers={"X-User": "bob"}).status_code)
```
```text
anonymous delete: 401
bob deletes alice's: 403
bob deletes missing: 404
bob deletes his own: 204
```

### 17.3 Checklist

Every route that changes data needs login **and** an ownership or role check; hiding a button is not a check. Never trust ids or roles from the request body (`user_id=1`): take the user from the session. Use `POST`/`DELETE` for changes, never `GET`. Test the forbidden cases (section 21).


## 18. REST APIs in Flask

swe.02 section 14 covered what a good JSON API looks like. Here is how it is written in Flask. The rules to follow in every endpoint:

- Resources are **nouns in the URL** (`/api/notes/3`); the HTTP **method** is the verb.
- Return the right **status**: `200` read, `201` created (with a `Location` header), `204` deleted/no body, `400` malformed, `401` not logged in, `403` not allowed, `404` missing, `422` valid JSON but invalid data.
- Every error has **one shape**, so clients write one handler.
- Lists are **paginated** and bounded (`per_page` has a maximum).
- Validate input strictly; never trust types in JSON (`"title": 5`).

```python
from flask import Flask, jsonify, request

app = Flask(__name__)
NOTES = {}
NEXT_ID = 1

def error(status, code, message):
    return jsonify(error={"code": code, "message": message}), status

@app.get("/api/notes")
def list_notes():
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 2, type=int), 1), 50)   # clamp
    items = sorted(NOTES.values(), key=lambda n: n["id"])
    start = (page - 1) * per_page
    return jsonify(items=items[start:start + per_page], page=page, per_page=per_page, total=len(items))

@app.get("/api/notes/<int:note_id>")
def get_note(note_id):
    note = NOTES.get(note_id)
    return jsonify(note) if note else error(404, "not_found", f"No note {note_id}.")

@app.post("/api/notes")
def create_note():
    global NEXT_ID
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error(400, "bad_json", "Send a JSON object.")
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        return error(422, "validation_failed", "text must be a non-empty string.")
    note = {"id": NEXT_ID, "text": text.strip()}
    NOTES[NEXT_ID] = note
    NEXT_ID += 1
    return jsonify(note), 201, {"Location": f"/api/notes/{note['id']}"}

@app.patch("/api/notes/<int:note_id>")
def update_note(note_id):
    note = NOTES.get(note_id)
    if note is None:
        return error(404, "not_found", f"No note {note_id}.")
    data = request.get_json(silent=True) or {}
    if "text" in data:
        note["text"] = str(data["text"]).strip()
    return jsonify(note)

@app.delete("/api/notes/<int:note_id>")
def delete_note(note_id):
    if NOTES.pop(note_id, None) is None:
        return error(404, "not_found", f"No note {note_id}.")
    return "", 204

c = app.test_client()
r = c.post("/api/notes", json={"text": "  first  "})
print(r.status_code, r.headers["Location"], r.get_json())
for t in ("second", "third", "fourth"):
    c.post("/api/notes", json={"text": t})
print(c.post("/api/notes", json={"text": 5}).get_json())
print(c.post("/api/notes", data="{oops", content_type="application/json").get_json()["error"]["code"])
page2 = c.get("/api/notes?page=2&per_page=2").get_json()
print(page2["page"], [n["text"] for n in page2["items"]], page2["total"])
print(c.patch("/api/notes/1", json={"text": "edited"}).get_json())
print(c.delete("/api/notes/1").status_code, c.get("/api/notes/1").status_code)
print(c.get("/api/notes?per_page=9999").get_json()["per_page"])
```
```text
201 /api/notes/1 {'id': 1, 'text': 'first'}
{'error': {'code': 'validation_failed', 'message': 'text must be a non-empty string.'}}
bad_json
2 ['third', 'fourth'] 4
{'id': 1, 'text': 'edited'}
204 404
50
```

Points worth copying:

- `request.get_json(silent=True)` plus an `isinstance(data, dict)` check handles missing body, wrong content type, broken JSON and `[1, 2]` in one place.
- The shape of the page response (`items`, `page`, `total`) is the same for every list endpoint. Offset pagination is simple; for very large tables cursor pagination (`?after=<id>`) is faster and stable (swe.03).
- `PATCH` changes some fields; `PUT` replaces the whole resource. Both are fine; be consistent.
- **Idempotency** matters: `DELETE` twice gives `204` then `404`; some APIs make the second also `204`. Document what you pick.

### 18.1 Authentication for APIs

An API called from your own pages (same site) can use the same session cookie, but then **CSRF applies** (the project requires the `X-CSRF-Token` header). An API called by *other programs* usually uses a **token** in the `Authorization: Bearer <token>` header: not sent automatically by browsers, so no CSRF risk, and revocable if stored server-side. Unauthenticated API calls get a **JSON 401**, never a redirect to an HTML page.

### 18.2 Class-based views, briefly

`flask.views.MethodView` groups the methods of one resource in a class (`def get(self, item_id)`, `def delete(self, item_id)`) and is registered with `app.add_url_rule("/items/<int:item_id>", view_func=ItemAPI.as_view("item"))`. Methods you do not define answer 405. Functions with `@bp.get` and `@bp.delete` are enough for most projects.

## 19. Error handling

### 19.1 Where errors come from

Three sources: **HTTP errors** you raise on purpose (`abort(404)`), HTTP errors Flask raises (no route: 404, wrong method: 405, body too large: 413), and **unexpected exceptions** (bugs, database down). Without handlers, Flask answers with a plain HTML page. A good app registers handlers so that users see a branded page, API clients see JSON in the usual shape, and bugs are logged.

### 19.2 Handlers by status code, by exception class

```python
import logging, sys
from flask import Flask, abort, jsonify, request
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.logger.handlers = [logging.StreamHandler(sys.stdout)]       # show the log in this demo
app.logger.setLevel(logging.ERROR)

class ApiError(Exception):                      # our own exception for expected failures
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message

@app.errorhandler(ApiError)
def handle_api_error(e):
    return jsonify(error={"code": e.code, "message": e.message}), e.status

@app.errorhandler(HTTPException)                # every abort() and every Flask-raised 4xx
def handle_http(e):
    if request.path.startswith("/api/"):
        return jsonify(error={"code": e.name.lower().replace(" ", "_"), "message": e.description}), e.code
    return f"<h1>{e.code} {e.name}</h1>", e.code

@app.errorhandler(Exception)                    # anything else: a bug
def handle_unexpected(e):
    app.logger.error("unhandled %s: %s", type(e).__name__, e)
    return jsonify(error={"code": "server_error", "message": "Something went wrong."}), 500

@app.get("/api/ok")
def ok(): return {"ok": True}

@app.get("/api/limit")
def limit(): raise ApiError(429, "rate_limited", "Slow down.")

@app.get("/api/bug")
def bug(): return {"x": 1 / 0}

@app.get("/page")
def page(): abort(403)

c = app.test_client()
for method, url in [("get", "/api/ok"), ("get", "/api/missing"), ("post", "/api/ok"),
                    ("get", "/api/limit"), ("get", "/api/bug"), ("get", "/page"), ("get", "/nowhere")]:
    r = getattr(c, method)(url)
    print(f"{method.upper():5}{url:14}{r.status_code}  {r.get_data(as_text=True).strip()[:70]}")
```
```text
GET  /api/ok       200  {"ok":true}
GET  /api/missing  404  {"error":{"code":"not_found","message":"The requested URL was not foun
POST /api/ok       405  {"error":{"code":"method_not_allowed","message":"The method is not all
GET  /api/limit    429  {"error":{"code":"rate_limited","message":"Slow down."}}
unhandled ZeroDivisionError: division by zero
GET  /api/bug      500  {"error":{"code":"server_error","message":"Something went wrong."}}
GET  /page         403  <h1>403 Forbidden</h1>
GET  /nowhere      404  <h1>404 Not Found</h1>
```

Rules to take from the output:

- The **most specific** handler wins: `ApiError` before `HTTPException` before `Exception`.
- The user sees a **safe, generic message** for a bug (`Something went wrong.`); the real exception goes to the **log** (the line `unhandled ZeroDivisionError...` above, printed because of our demo handler). Never send exception text or a traceback to users: it leaks file paths, SQL and secrets.
- `e.description` is the message you gave to `abort(404, description=...)`.
- In `TESTING` mode with no generic handler, Flask re-raises unexpected exceptions so your test fails loudly. A generic `Exception` handler changes that: your test then sees a 500 response. Decide on purpose.
- A handler registered on a blueprint (`@bp.errorhandler`) covers only that blueprint's routes; `@bp.app_errorhandler` covers the app (section 13).

## 20. CORS in one page

A web page may freely send a request to another origin (scheme + host + port), but the browser **refuses to let the page read the response** unless the other server agrees. This is the **same-origin policy**, relaxed by **CORS** (cross-origin resource sharing): the API says, in headers, which origins may read it.

```text
   page on https://app.example  ---->  https://api.example/data
   browser adds   Origin: https://app.example
   API answers    Access-Control-Allow-Origin: https://app.example     -> page may read it
   (no such header) -> the request happened, but the page's JavaScript cannot see the answer
```

For "non-simple" requests (JSON `Content-Type`, custom headers, `PUT`/`DELETE`) the browser first sends a **preflight**: `OPTIONS` with `Access-Control-Request-Method`. The server replies with what is allowed. Hand-written, with an allow-list:

```python
from flask import Flask, request

app = Flask(__name__)
ALLOWED = {"https://app.example"}

@app.after_request
def cors(resp):
    origin = request.headers.get("Origin")
    if origin in ALLOWED:                                    # never reflect an arbitrary origin
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-CSRF-Token"
    return resp

@app.get("/api/data")
def data(): return {"n": 1}

c = app.test_client()
for origin in ("https://app.example", "https://evil.example"):
    r = c.get("/api/data", headers={"Origin": origin})
    print(origin, "->", r.headers.get("Access-Control-Allow-Origin"))
r = c.options("/api/data", headers={"Origin": "https://app.example", "Access-Control-Request-Method": "DELETE"})
print(r.status_code, r.headers["Access-Control-Allow-Methods"])
```
```text
https://app.example -> https://app.example
https://evil.example -> None
200 GET, POST, DELETE
```

Important truths:

- CORS protects **users' browsers**, not your server. `curl` ignores it. It is not authentication.
- Never answer `Access-Control-Allow-Origin: *` together with cookies (`Allow-Credentials: true`); browsers reject it, and reflecting any origin would be a security hole.
- If the page and the API share one origin (as in this chapter's blog), you do not need CORS at all.
- In real projects use the **Flask-CORS** extension (section 23) with an explicit origin list.

## 21. Testing Flask apps

### 21.1 The test client

You have used `app.test_client()` all chapter. It builds the WSGI `environ` (section 1.2), calls the app, and returns a response; there is no server and no network, so a test takes milliseconds. It also **keeps cookies between calls**, like a browser, so a login persists across later requests on the same client.

| You want to test | Use |
|---|---|
| Status, body | `r.status_code`, `r.get_data(as_text=True)` / `r.data` |
| JSON | `client.post(url, json=...)`, `r.get_json()` |
| A redirect | `r.status_code == 302`, `r.headers["Location"]`, or `follow_redirects=True` and `r.history` |
| A flash message | follow the redirect and look in the body, or read `session["_flashes"]` |
| The session | `with client.session_transaction() as s:` (read or **write**) |
| Cookies | `client.get_cookie("session")` |
| A form with CSRF | send the token (section 21.3) |

### 21.2 Fixtures: an app per test

pytest **fixtures** (core.17 in the course) build what tests need. With an application factory the pattern is: a fresh app with an in-memory database for every test, a client from it, a helper for login. Run it for real: the next block writes a tiny project and runs `pytest` on it.

```python
import subprocess, sys, textwrap
from pathlib import Path

Path("tests").mkdir()
Path("tiny.py").write_text(textwrap.dedent('''
    from flask import Flask, jsonify, redirect, request, session, flash, get_flashed_messages
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    class Base(DeclarativeBase): pass
    db = SQLAlchemy(model_class=Base)

    class Item(db.Model):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]

    def create_app(config=None):
        app = Flask(__name__)
        app.config.update(SQLALCHEMY_DATABASE_URI="sqlite://", SECRET_KEY="t")
        app.config.update(config or {})
        db.init_app(app)
        with app.app_context():
            db.create_all()

        @app.post("/items")
        def add():
            data = request.get_json(silent=True) or {}
            if not data.get("name"):
                return jsonify(error="name required"), 422
            item = Item(name=data["name"]); db.session.add(item); db.session.commit()
            flash("added")
            return jsonify(id=item.id, name=item.name), 201

        @app.get("/items")
        def items():
            return jsonify([i.name for i in db.session.scalars(db.select(Item).order_by(Item.id))])

        @app.get("/flashes")
        def flashes():
            return jsonify(get_flashed_messages())

        @app.get("/old")
        def old(): return redirect("/items")
        return app
'''))
Path("tests/conftest.py").write_text(textwrap.dedent('''
    import pytest
    from tiny import create_app, db

    @pytest.fixture
    def app():
        app = create_app({"TESTING": True})          # a brand-new app and empty database per test
        yield app
        with app.app_context():
            db.session.remove(); db.drop_all()

    @pytest.fixture
    def client(app):
        return app.test_client()
'''))
Path("tests/test_tiny.py").write_text(textwrap.dedent('''
    def test_add_and_list(client):
        r = client.post("/items", json={"name": "pen"})
        assert r.status_code == 201 and r.get_json()["name"] == "pen"
        assert client.get("/items").get_json() == ["pen"]

    def test_isolated_from_previous_test(client):
        assert client.get("/items").get_json() == [], "each test must start with an empty database"

    def test_validation(client):
        r = client.post("/items", json={})
        assert r.status_code == 422, "empty name must be rejected with 422"

    def test_redirect(client):
        r = client.get("/old")
        assert r.status_code == 302 and r.headers["Location"] == "/items"
        assert client.get("/old", follow_redirects=True).get_json() == []

    def test_flash_is_in_the_session(client):
        client.post("/items", json={"name": "pen"})
        assert client.get("/flashes").get_json() == ["added"]
        assert client.get("/flashes").get_json() == [], "flash shows once"

    def test_session_transaction_can_write(client):
        with client.session_transaction() as s:
            s["user_id"] = 5
        with client.session_transaction() as s:
            assert s["user_id"] == 5
'''))
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                   capture_output=True, text=True)
import re
print(re.sub(r" in [0-9.]+s", "", r.stdout).strip())
```
```text
......                                                                   [100%]
6 passed
```

Things to take from this:

- The **`app` fixture creates a new app each time** (`create_app({"TESTING": True})`) with `sqlite://`, so tests cannot affect each other. Order independence is the first quality of a test suite. If a test passes alone and fails in the suite, shared state is leaking: a module-level app, a global list, a file database.
- `TESTING=True` makes Flask re-raise unexpected exceptions so the traceback shows in pytest, and sets sensible defaults.
- A fixture with `yield` runs its cleanup after the test, even when it failed.
- `client.session_transaction()` opens the cookie session so a test can *set up* state (log in, set the CSRF token) without going through the form.
- Test the **forbidden** and **invalid** paths as carefully as the happy path.

### 21.3 Logged-in tests and CSRF

Two helpers keep login tests short (the project's `tests/conftest.py` has both): a function that creates a user directly in the database, and an `Auth` class whose `login()` posts to the login route. CSRF needs one trick: the token lives in the session, so the test seeds a known value with `session_transaction`, then sends it in every `POST`. And, as section 9 warned, **login clears the session**, so the token vanishes and the helper must seed it again. This is one of the most common reasons a test that "should be 302" gets a 400.

```python
def seed_token(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "test-token"
```

### 21.4 Limits

The test client does not run JavaScript or render CSS; browser-level checks (Playwright, Selenium) belong in a few end-to-end tests (swe.01, the test pyramid).

### 21.5 Try it

A test does `client.post("/auth/login", data={...})`, expects 302, and gets 400. Name the two most likely causes in this chapter's app.

<details><summary>Answer</summary>

1. The CSRF token is missing or wrong: the form data lacks `csrf_token`, or the test client's session has none (fixture not seeding it). The `before_request` check answers 400 before the view runs.
2. The token was seeded, but a previous login/logout call cleared the session and nothing re-seeded it.

Read the response body: `abort(400, description="Bad or missing CSRF token.")` puts the reason in the page.
</details>

## 22. Logging, the debugger and running for real

### 22.1 Logging

Flask gives you `app.logger`, a standard `logging.Logger` (core.14). Use levels: `debug` for developer detail, `info` for normal events ("user logged in"), `warning` for odd but handled cases, `error` and `exception` for failures (`exception` adds the traceback). **Never log passwords, tokens or full cookies.** In production, log to stdout and let the platform collect it.

```python
import logging, sys
from flask import Flask, request

app = Flask("blog")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
app.logger.handlers = [handler]
app.logger.setLevel(logging.INFO)

@app.post("/login")
def login():
    user = request.form.get("username", "")
    if request.form.get("password") != "ok":
        app.logger.warning("failed login for %r", user)        # the username, never the password
        return "no", 401
    app.logger.info("login ok for %r", user)
    return "yes"

c = app.test_client()
c.post("/login", data={"username": "alice", "password": "bad"})
c.post("/login", data={"username": "alice", "password": "ok"})
app.logger.debug("this line is below INFO and is not shown")
```
```text
WARNING blog: failed login for 'alice'
INFO blog: login ok for 'alice'
```

### 22.2 The debugger: development only

With `flask --app app run --debug` (or `FLASK_DEBUG=1`) you get an auto-reloader and an interactive **in-browser debugger** on every exception: a stack trace where you can run Python in each frame. That is wonderful on your laptop and **remote code execution on a server**. If a production site shows the Werkzeug traceback page with a console, anyone who reaches it can run code on your machine (the PIN is a weak barrier).

Rules: never `app.run(debug=True)` in code that is deployed; control it from the environment; production config has `DEBUG = False`.

```python
from flask import Flask
app = Flask(__name__)
print("default debug:", app.debug, "| default testing:", app.testing)
```
```text
default debug: False | default testing: False
```

### 22.3 The development server is not the production server

`flask run` uses Werkzeug's server: single process, little hardening. Production runs a real WSGI server (Gunicorn on Linux, Waitress on Windows) with several worker processes, usually behind a reverse proxy (nginx, Caddy, a cloud load balancer) that terminates HTTPS, serves static files and applies timeouts.

```text
   browser --https--> nginx (TLS, static files, timeouts) --http--> Gunicorn (4 workers) --> create_app()
```

> ### Try it on your machine: Gunicorn
> This is a tutorial only; it needs a package that is not part of the course environment.
>
> ```text
> pip install gunicorn
> gunicorn --workers 2 --bind 127.0.0.1:8000 "app:create_app()"
> ```
>
> Expected: lines saying `Starting gunicorn`, `Listening at: http://127.0.0.1:8000` and one `Booting worker with pid ...` per worker (the pids are machine-specific). Check it with `curl -i http://127.0.0.1:8000/`. Workers are separate processes, so **in-memory state (a global list, an in-memory SQLite database) is not shared between them**: another reason state belongs in the database. Rule of thumb for the worker count: `2 x cores + 1`. Stop with Ctrl+C.


Before deploying: `DEBUG` off; a real `SECRET_KEY` from the environment; `SESSION_COOKIE_SECURE=True`; HTTPS; a real database (not SQLite in a container's temp disk); migrations run; logs going to stdout; a health endpoint (`/health` returns `200`) for the platform to poll.


## 23. Extensions you will meet

Everything in this chapter was written by hand on purpose, so that nothing below is magic. In real projects you will often use an extension for the parts that are easy to get subtly wrong. They all follow the `ext.init_app(app)` pattern from section 11.

| Extension | Replaces what we wrote by hand | Notes |
|---|---|---|
| **Flask-Login** | `load_user`, `login_required`, the "remember me" cookie | `login_user(user)`, `logout_user()`, `current_user`, `@login_required`; you provide a `user_loader` |
| **Flask-WTF** (WTForms) | form classes, validators, `csrf_token()` and the check | `form.validate_on_submit()`, `{{ form.hidden_tag() }}` |
| **Flask-Migrate** (Alembic) | `db.create_all()` for schema changes | `flask db init / migrate / upgrade`; swe.03 section 13 explains the engine |
| **Flask-CORS** | the hand-written `after_request` of section 20 | `CORS(app, origins=[...])` |
| **Flask-Limiter** | login throttling | per-route and per-IP limits |
| **Flask-Session** | cookie sessions | server-side sessions in Redis or a database (revocable) |

> ### Try it on your machine: Flask-Login, Flask-WTF and Flask-Migrate
> These packages are not in the course environment, so nothing here was run for this chapter.
>
> ```text
> pip install flask-login flask-wtf flask-migrate
> ```
>
> Then: `from flask_migrate import Migrate; migrate = Migrate(app, db)` inside `create_app`, and run `flask --app app db init`, `flask --app app db migrate -m "first"`, `flask --app app db upgrade`. You should see a new `migrations/` folder with a generated revision file, and `upgrade` should log that it ran the revision (the revision id is a random hex string, machine-specific). Replace the hand-written `login_required` with Flask-Login's, and compare: the decorator you wrote in section 16.4 is, in spirit, the same one.

Rule of thumb: write authentication by hand once to understand it; in a team project, prefer the well-reviewed extension for security-sensitive code, and read its source to see it is the same idea.

## 24. Project: a blog platform, step by step

**Goal.** A multi-page blog with accounts: people register and log in; logged-in users write, edit and delete **their own** posts and comment on any post; the home page lists posts with pagination; a small JSON API reads and creates posts; a pytest suite covers all of it. The code uses nothing outside the packages installed in the course environment.

### 24.1 The final file tree

```text
blog/
    pytest.ini
    app/
        __init__.py
        api.py
        auth.py
        blog.py
        config.py
        errors.py
        extensions.py
        models.py
        security.py
        static/
            style.css
        templates/
            base.html
            error.html
            auth/
                login.html
                register.html
            blog/
                edit.html
                index.html
                show.html
    tests/
        conftest.py
        test_api.py
        test_auth.py
        test_blog.py
```

The folder `blog/` is the project root (the folder you run `flask` and `pytest` from). `app/` is the package, `tests/` is next to it, `pytest.ini` sets `pythonpath = .` so tests can `import app`. `blog.db` (SQLite) would appear next to it when you run the dev server; it is not committed.

### 24.2 Build order

Build from the bottom up, running the tests (or the app) after each step:

| Step | You write | What you prove |
|---|---|---|
| 1 | `config.py`, `extensions.py`, `__init__.py` with `create_app` | `create_app(TestConfig)` returns an app |
| 2 | `models.py` | `db.create_all()` works; a `User` can have `Post`s |
| 3 | `security.py`: `load_user`, `login_required`, CSRF | the building blocks, unit-testable |
| 4 | `auth.py` + `base.html`, login and register templates | register, login, logout work |
| 5 | `blog.py` + templates | create, show, edit, delete, comment, paginate |
| 6 | `errors.py` + `error.html` | 404/403/500 pages and JSON errors |
| 7 | `api.py` | JSON list/get/create/delete |
| 8 | `tests/` | every step above, including the forbidden cases |

Steps 1 to 3 below are shown in full; the pattern repeats for the rest.

### 24.3 The factory (step 1)

**`app/__init__.py`**

```python
from flask import Flask

from .config import Config
from .errors import register_error_handlers
from .extensions import db
from .security import check_csrf, csrf_token, load_user


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    from . import api, auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    app.register_blueprint(api.bp)

    app.before_request(load_user)
    app.before_request(check_csrf)
    app.context_processor(lambda: {"csrf_token": csrf_token})
    register_error_handlers(app)

    with app.app_context():
        db.create_all()
    return app
```

Read it as the recipe from section 11: create the app, load config, attach the extension, register the three blueprints, add two `before_request` hooks, expose `csrf_token()` to templates, register error handlers, create tables. `config.py` has the three classes of section 12.3 plus `POSTS_PER_PAGE`, and `extensions.py` is the five-line `db = SQLAlchemy(model_class=Base)` of section 14.2. The imports of `api`, `auth`, `blog` sit **inside** the function, because they import models and `db`, and only need to be loaded once the app exists (this avoids the circular-import trap of section 11).

### 24.4 Models (step 2)

**`app/models.py`**

```python
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40), unique=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(default=utcnow)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    author: Mapped[User] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan",
        order_by="Comment.id",
    )

    def to_dict(self):
        return {"id": self.id, "title": self.title, "body": self.body,
                "author": self.author.username}


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    created: Mapped[datetime] = mapped_column(default=utcnow)
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    post: Mapped[Post] = relationship(back_populates="comments")
    author: Mapped[User] = relationship()
```

Design decisions worth saying out loud: the password is stored as `password_hash` only; `cascade="all, delete-orphan"` on `Post.comments` deletes a post's comments with it (swe.03 section 4); `created` stores a timezone-aware UTC time; `to_dict` keeps the JSON shape in one place.

### 24.5 Security helpers (step 3)

**`app/security.py`**

```python
import secrets
from functools import wraps

from flask import abort, flash, g, redirect, request, session, url_for

from .extensions import db
from .models import User


def load_user():
    """before_request hook: put the logged-in user (or None) on g."""
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please log in first.")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]


def check_csrf():
    """before_request hook: every unsafe request must carry the token."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token", "")
    expected = session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(sent, expected):
        abort(400, description="Bad or missing CSRF token.")
```

This is sections 9, 16 and 17 in 39 lines. `load_user` runs before every request and sets `g.user`; `login_required` guards a view; `check_csrf` rejects any unsafe request without the token.

### 24.6 Authentication blueprint (step 4)

**`app/auth.py`** (lines 10 to 65)

```python
bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not 3 <= len(username) <= 40:
            errors.append("Username must be 3 to 40 characters.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not errors and db.session.scalar(select(User).filter_by(username=username)):
            errors.append("That username is taken.")
        if not errors:
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please log in.")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", errors=errors), (400 if errors else 200)


def safe_next(target):
    """Allow only same-site relative paths (no open redirect)."""
    if not target:
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    return target


@bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = db.session.scalar(select(User).filter_by(username=username))
        if user is None or not user.check_password(password):
            error = "Wrong username or password."   # same text for both cases
        else:
            session.clear()                          # new session, new csrf token
            session["user_id"] = user.id
            return redirect(safe_next(request.args.get("next")) or url_for("blog.index"))
    return render_template("auth/login.html", error=error), (401 if error else 200)


@bp.post("/logout")
def logout():
    session.clear()
    flash("You are logged out.")
    return redirect(url_for("blog.index"))
```

Check each habit from the chapter: validation collects all errors; the unique check is friendly while the `unique=True` column is the guarantee; the same error text for unknown user and wrong password; `session.clear()` before storing the id (fixation, and a fresh CSRF token); `safe_next` blocks open redirects; logout is a `POST` with CSRF, not a link.

### 24.7 Blog blueprint (step 5)

Only the first part is shown; edit, delete and comment follow the same pattern.

**`app/blog.py`** (lines 9 to 57)

```python

bp = Blueprint("blog", __name__)


def get_post_or_404(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404, description="No such post.")
    return post


def owned_post_or_403(post_id):
    post = get_post_or_404(post_id)
    if post.author_id != g.user.id:
        abort(403, description="You can only change your own posts.")
    return post


@bp.get("/")
def index():
    page = request.args.get("page", 1, type=int)
    stmt = (select(Post).options(selectinload(Post.author))
            .order_by(Post.id.desc()))
    pagination = db.paginate(stmt, page=page, per_page=5, error_out=False)
    return render_template("blog/index.html", pagination=pagination)


@bp.get("/post/<int:post_id>")
def show(post_id):
    return render_template("blog/show.html", post=get_post_or_404(post_id))


@bp.route("/post/new", methods=["GET", "POST"])
@login_required
def create():
    error = None
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not body:
            error = "Title and body are required."
        else:
            post = Post(title=title, body=body, author=g.user)
            db.session.add(post)
            db.session.commit()
            flash("Post published.")
            return redirect(url_for("blog.show", post_id=post.id))
    return render_template("blog/edit.html", post=None, error=error), (400 if error else 200)
```

The two helpers are the heart of authorisation: `get_post_or_404` gives a 404 for a missing post, `owned_post_or_403` adds the ownership check. `edit` and `delete` call it first, so the check cannot be forgotten. The `index` view uses `selectinload` (no N+1) and `db.paginate`.

The templates follow section 7: `base.html` has the navigation (it shows different links when `g.user` is set), the flashed messages and `{% block content %}`; each page extends it. User text is printed with plain `{{ ... }}`, so autoescaping protects every page. Every `<form method="post">` includes `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.

### 24.8 Errors and API (steps 6 and 7)

`errors.py` is section 19 almost unchanged: an `ApiError` class, a handler for it, one for `HTTPException` (JSON when the path starts with `/api/`, the `error.html` template otherwise) and one for `Exception` that logs and shows a generic 500.

`api.py` is the style of section 18: `GET /api/posts` (paginated), `GET /api/posts/<id>`, `POST /api/posts` (201 + `Location`), `DELETE /api/posts/<id>` (204), all raising `ApiError` with the same JSON shape; the create and delete routes check `g.user` and return a **JSON 401**, not a redirect.

### 24.9 Tests (step 8)

**`tests/conftest.py`** (lines 1 to 50)

```python
import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import User

TOKEN = "test-token"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


def seed_token(client):
    """Give the session a known CSRF token (login/logout clear the session)."""
    with client.session_transaction() as sess:
        sess["csrf_token"] = TOKEN


@pytest.fixture
def client(app):
    client = app.test_client()
    seed_token(client)
    return client


def make_user(app, username="alice", password="s3cret-pass"):
    with app.app_context():
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user.id


class Auth:
    def __init__(self, client):
        self.client = client

    def login(self, username="alice", password="s3cret-pass"):
        response = self.client.post("/auth/login", data={
            "username": username, "password": password, "csrf_token": TOKEN})
        seed_token(self.client)             # login made a fresh session
        return response
```

`app` gets a fresh in-memory database for every test; `client` seeds a known CSRF token; `Auth.login()` re-seeds it after the session is cleared; `alice` and `bob` create users with a password hash. Then tests read like sentences:

**`tests/test_blog.py`** (lines 29 to 41)

```python

def test_only_the_owner_can_edit(client, auth, alice, bob):
    auth.login("alice", "s3cret-pass")
    location = create_post(client).headers["Location"]
    auth.logout()
    auth.login("bob", "bobs-password")
    assert client.get(location + "/edit").status_code == 403
    r = client.post(location + "/delete", data={"csrf_token": TOKEN})
    assert r.status_code == 403


def test_post_text_is_escaped(client, auth, alice):
    auth.login()
```

Run the whole suite (the 19 tests live in `test_auth.py`, `test_blog.py` and `test_api.py`; the time line is removed so the output is stable):

```text
$ pytest -q
...................                                                      [100%]
19 passed
```

### 24.10 A session with the finished app

Here is the finished app driven like a user would: register, log in, write a post with hostile text, comment, view, and call the API. (It runs against an in-memory database; run it from the project folder.)

```python
import re
from app import create_app
from app.config import TestConfig

app = create_app(TestConfig)
c = app.test_client()

def token(url):
    html = c.get(url).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([0-9a-f]+)"', html).group(1)

r = c.post("/auth/register", data={"username": "kavya", "password": "long-password", "csrf_token": token("/auth/register")})
print("register:", r.status_code, r.headers["Location"])
r = c.post("/auth/login", data={"username": "kavya", "password": "long-password", "csrf_token": token("/auth/login")})
print("login:   ", r.status_code, r.headers["Location"])

r = c.post("/post/new", data={"title": "<b>Hi</b>", "body": "first post", "csrf_token": token("/post/new")})
print("create:  ", r.status_code, r.headers["Location"])
page = c.get(r.headers["Location"]).get_data(as_text=True)
print("flash shown:", "Post published." in page, "| escaped title:", "&lt;b&gt;Hi&lt;/b&gt;" in page)

c.post("/post/1/comment", data={"body": "Nice one", "csrf_token": token("/post/1")})
print("comments:", "Comments (1)" in c.get("/post/1").get_data(as_text=True))

print("api list:", c.get("/api/posts").get_json())
t = token("/")
print("api create:", c.post("/api/posts", json={"title": "via API", "body": "b"}, headers={"X-CSRF-Token": t}).status_code)
print("api bad:   ", c.post("/api/posts", json={"title": ""}, headers={"X-CSRF-Token": t}).get_json())
print("no csrf:   ", c.post("/post/1/delete").status_code)
c.post("/auth/logout", data={"csrf_token": t})
print("after logout:", c.get("/post/new").status_code)
```
```text
register: 302 /auth/login
login:    302 /
create:   302 /post/1
flash shown: True | escaped title: True
comments: True
api list: {'items': [{'author': 'kavya', 'body': 'first post', 'id': 1, 'title': '<b>Hi</b>'}], 'page': 1, 'pages': 1, 'total': 1}
api create: 201
api bad:    {'error': {'code': 'validation_failed', 'message': 'title and body must be non-empty strings.'}}
no csrf:    400
after logout: 302
```

### 24.11 Try it on your machine: run it in a browser

```text
cd blog
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
flask --app app run --debug
```

Open `http://127.0.0.1:5000/`. Expected: the page "Posts" with "No posts yet." and links Home, Log in, Register. Register, log in, write a post, then try `http://127.0.0.1:5000/post/1/edit` while logged in as a second user (a second browser profile): you should get the 403 page. A file `blog.db` appears in the folder (it holds your data; delete it to start over). `--debug` is for your laptop only.

### 24.12 Stretch goals

Add tags (many-to-many), comment editing with the same ownership helper, a Flask-Migrate migration that adds `Post.updated`, a `/health` route, and rate limiting on login.

## 25. Common traps

Collected from the chapter. Each is a real mistake with the symptom you will see.

1. **`TemplateNotFound`.** The folder must be `templates/` next to the module of `Flask(__name__)`; with blueprints use the full name `blog/index.html`. Check `app.root_path`.
2. **`BuildError: Could not build url for endpoint 'show'`.** Inside blueprints the endpoint is `blog.show`; arguments must match the rule (`post_id=`).
3. **Working outside of application/request context.** Wrap scripts and tests in `with app.app_context():`; do not use `request` in a thread you started.
4. **Circular imports.** Create `db` in `extensions.py`, never import `app`; import blueprints inside `create_app`.
5. **`@login_required` above `@app.route`.** The route registers the unprotected function. The route decorator goes on top. Forgetting `@wraps` gives duplicate endpoint `wrapped`.
6. **Missing `SECRET_KEY`.** `RuntimeError: The session is unavailable because no secret key was set.` And a key committed to Git is a leaked key.
7. **`debug=True` in production.** Remote code execution through the debugger. Control it by environment.
8. **Trusting the browser.** HTML `required` is not validation. Re-check on the server.
9. **`|safe` on user data, or HTML built with f-strings.** XSS. Let autoescape do its job; use `|tojson` inside scripts.
10. **State change on `GET`**, or a `POST` handler that renders instead of redirecting (double submit on refresh). Use PRG.
11. **No CSRF token** on cookie-authenticated `POST`s. And tests that forget that login clears the session and the token with it.
12. **Different error for "no such user"** and "wrong password"; plaintext or fast-hash passwords; skipping `session.clear()` at login.
13. **Authentication without authorisation.** Every changing route needs an ownership/role check (IDOR); hiding the button is not a check.
14. **Open redirect** through an unchecked `next` parameter.
15. **`request.form["x"]` for optional fields** (400 `BadRequestKeyError`) or `request.args.get("page")` without `type=int` (string `"2"` used as a number).
17. **N+1 queries** in a template loop; **no `order_by`** under pagination; **forgetting `commit()`**; **forgetting `rollback()`** after an `IntegrityError`.
18. **`db.create_all()` as a migration tool.** It never changes existing tables. Use migrations (swe.03, Flask-Migrate).
19. **Global state in the process** (a module-level list, in-memory SQLite) in an app served by several workers: each worker has its own copy. State belongs in the database.
20. **Tests that share an app or a file database**, so order matters; no tests for the forbidden/invalid cases.
21. **Unexpected exceptions leaking** to users (tracebacks, SQL) because no `Exception` handler exists, or an API that returns HTML error pages to JSON clients.

## 26. Summary

- Flask is a WSGI application: a callable `app(environ, start_response)`. The test client calls it without a network, which is why almost all Flask code can be tested offline and fast.
- **Routing** maps URL patterns and methods to functions; converters validate parts of the URL; `url_for` builds URLs; `404` means no rule, `405` wrong method.
- **Request** (`args`, `form`, `get_json`, `files`, `headers`, `cookies`) in, **response** (string, dict, tuple, `make_response`, `redirect`, `abort`) out. Hooks (`before_request`, `after_request`, `teardown_*`) wrap every request.
- **Jinja2** templates escape by default, which is your XSS defence; `|safe` and f-strings undo it. Use inheritance (`extends`/`block`), macros and `url_for` in templates.
- Forms: validate on the server, redirect after a successful `POST`, flash messages, and **a CSRF token** on every cookie-authenticated unsafe request.
- **Contexts** make `request`, `session`, `g` and `current_app` work like globals. Outside a request, push one yourself.
- **Application factory + blueprints + config classes**: no work at import time, one app per test, settings from the environment, secrets never in Git.
- **Flask-SQLAlchemy** gives `db.session` per app context, `db.Model`, `get_or_404`, `paginate`. Mind N+1, commit and rollback; use migrations for schema changes.
- **Authentication**: hash passwords (`werkzeug.security`), put only the user id in the signed session cookie, `session.clear()` at login, `HttpOnly`/`Secure`/`SameSite`, a hand-written `login_required`. **Authorisation**: check ownership in every route that changes data.
- **REST APIs**: nouns in URLs, correct status codes, one error shape, bounded pagination, JSON 401 not redirects; CORS is a browser rule, not security.
- **Testing**: factory + in-memory SQLite + fixtures; `client.session_transaction`, `follow_redirects`, test the forbidden paths; login clears the CSRF token.
- **Operations**: log to stdout, never log secrets, never `debug=True` in production, use Gunicorn behind a proxy, keep state in the database.

**Where next.** swe.05 and later modules reuse this app shape for deployment, background jobs and caching. Practise by rebuilding the blog from an empty folder without looking, then add a feature (tags, avatars, search) and its tests first.

