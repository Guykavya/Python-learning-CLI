# Chapter 5 (SWE): FastAPI

In the Flask chapter you built web apps where you checked every input by hand: `request.get_json()`, then `isinstance(text, str)`, then a hand-made error shape. In the core chapter on type hints you learned that hints *describe* your data but Python never enforces them. **FastAPI** closes that gap. You write a function with type hints, and the framework reads those hints and does three jobs for you: it **validates** every request against them, it **converts** the data into the right Python types, and it **documents** the API automatically. One piece of information (the hint) does three jobs.

FastAPI is built on two libraries. **Starlette** is the web toolkit (routing, requests, responses, middleware, WebSockets). **Pydantic** is the validation engine (models, constraints, error messages). FastAPI is the thin layer that connects them and adds dependency injection and OpenAPI generation. Knowing this split explains many things later: some behaviour is Starlette's, some is Pydantic's, and the docs of those two projects answer most "how do I..." questions.

By the end you reach two outcomes:

- You can **build a validated, documented, tested API from an empty folder**: typed endpoints, Pydantic models, a database, login with tokens, tests, and a clean project layout.
- You can **explain where validation happens and what a 422 response means**, by reading a real error body and pointing to the exact field and rule that failed.

Prerequisites: swe.02 (HTTP, REST), swe.03 (SQLAlchemy, async section, N+1), core.09 (type hints) and core.21 (`asyncio`). They are referenced, not re-taught. swe.04 (Flask) is not required, but we compare to it.

> **Offline rule for this chapter.** Every runnable example uses FastAPI's `TestClient`, which calls the app **in the same process** with no network and no server, and SQLite databases that are in memory or in a temporary file. Nothing here needs the internet. The `uvicorn` server is *not* installed in this course environment, so the few places that show a real server are marked **Try it on your machine** with exact commands; their outputs are described, never claimed as captured.

Every output block in this chapter was produced by actually running the code above it, with these versions (your patch versions may differ; the behaviour described is stable):

```bash run
python -c "
import sys, fastapi, pydantic, starlette, sqlalchemy, sqlmodel, httpx
print('python    ', sys.version.split()[0])
for m in (fastapi, starlette, pydantic, sqlalchemy, sqlmodel, httpx):
    print(f'{m.__name__:10}', m.__version__)
"
```
```text
python     3.14.4
fastapi    0.162.0
starlette  1.10.0
pydantic   2.14.3
sqlalchemy 2.1.8
sqlmodel   0.0.48
httpx      0.28.1
```

## Table of contents

1. [Why FastAPI, and ASGI versus WSGI](#1-why-fastapi-and-asgi-versus-wsgi)
2. [The smallest app, and how to run it](#2-the-smallest-app-and-how-to-run-it)
3. [Path, query, header and cookie parameters](#3-path-query-header-and-cookie-parameters)
4. [Request bodies](#4-request-bodies)
5. [Pydantic v2 in depth](#5-pydantic-v2-in-depth)
6. [Where validation happens: the 422 response](#6-where-validation-happens-the-422-response)
7. [Responses: response_model and status codes](#7-responses-response_model-and-status-codes)
8. [Error handling](#8-error-handling)
9. [Dependency injection](#9-dependency-injection)
10. [async def versus def](#10-async-def-versus-def)
11. [Async database access](#11-async-database-access)
12. [Authentication and authorisation](#12-authentication-and-authorisation)
13. [Middleware and CORS](#13-middleware-and-cors)
14. [Background tasks](#14-background-tasks)
15. [WebSockets](#15-websockets)
16. [File uploads and raw bodies](#16-file-uploads-and-raw-bodies)
17. [Routers and project structure](#17-routers-and-project-structure)
18. [Settings from the environment](#18-settings-from-the-environment)
19. [OpenAPI and the interactive docs](#19-openapi-and-the-interactive-docs)
20. [Testing FastAPI apps](#20-testing-fastapi-apps)
21. [Running for real](#21-running-for-real)
22. [Project: a task-management API, step by step](#22-project-a-task-management-api-step-by-step)
23. [Flask, FastAPI and Django compared](#23-flask-fastapi-and-django-compared)
24. [Common traps](#24-common-traps)
25. [Collected traps](#25-collected-traps)
26. [Summary](#26-summary)

## 1. Why FastAPI, and ASGI versus WSGI

### 1.1 What Flask could not do well

Flask (swe.04 section 1) sits on **WSGI**: the server calls `app(environ, start_response)`, your code runs, and it returns the whole response. That call is **synchronous and one-shot**. It has two limits:

1. **One request ties up one worker thread for its whole life.** If a handler waits 2 seconds for a slow API, that thread does nothing for 2 seconds. To serve many slow requests you need many threads or processes.
2. **There is no place for long-lived connections.** A WebSocket stays open for minutes. A WSGI call that returns a finished response cannot model "send a message now, another one later".

**ASGI** (Asynchronous Server Gateway Interface) is the newer contract that removes both limits. An ASGI app is an `async` callable that takes **three** arguments:

```text
async def app(scope, receive, send):
    scope    # a dict: what kind of connection this is ("http", "websocket", "lifespan"), path, headers...
    receive  # an async function: await it to get the next incoming message (e.g. the request body)
    send     # an async function: await it to send a message out (response start, body chunks)
```

Because every step is `await`-able, one thread running the **event loop** (core.21) can have thousands of requests "in flight" at once: whenever one is waiting (for the network, a database), the loop runs another. And because `receive` and `send` can be called many times, a connection can carry many messages: that is what a WebSocket is.

```text
              WSGI                                   ASGI
   server calls app(environ, start_response)   server calls await app(scope, receive, send)
   one call = one request = one response       one call = one connection (many messages)
   blocking                                    awaitable, can interleave with other connections
   HTTP only                                   HTTP, WebSocket, lifespan events
```

### 1.2 A hand-written ASGI app, run in-process

You will almost never write this yourself, but seeing it once removes the magic. Here is a complete ASGI application and a tiny "fake server" that calls it, exactly as a real server (uvicorn) does:

```python run
import asyncio


async def app(scope, receive, send):
    assert scope["type"] == "http"
    body = f"You asked for {scope['path']} with {scope['method']}\n".encode()
    await send({
        "type": "http.response.start",
        "status": 200,
        "headers": [(b"content-type", b"text/plain"), (b"content-length", str(len(body)).encode())],
    })
    await send({"type": "http.response.body", "body": body})


async def fake_server():
    sent = []

    async def receive():                     # a real server would read the socket here
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):                 # a real server would write to the socket here
        sent.append(message)

    scope = {"type": "http", "method": "GET", "path": "/hello", "headers": []}
    await app(scope, receive, send)
    return sent


for message in asyncio.run(fake_server()):
    print(message["type"], {k: v for k, v in message.items() if k != "type"})
```
```text
http.response.start {'status': 200, 'headers': [(b'content-type', b'text/plain'), (b'content-length', b'30')]}
http.response.body {'body': b'You asked for /hello with GET\n'}
```

Read the output: a response is **two messages**, `http.response.start` (status and headers) then `http.response.body`. A streaming response could send the body in many pieces. A WebSocket app would loop `await receive()` and `await send(...)` for as long as the client stays.

A **FastAPI object is an ASGI application**: `await app(scope, receive, send)` works on it. Let us prove it by calling FastAPI with our fake server, with no `TestClient` at all:

```python run
import asyncio
from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
async def hello():
    return {"msg": "hi"}


async def call(app, path):
    sent = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "GET",
             "path": path, "raw_path": path.encode(), "query_string": b"", "headers": [],
             "scheme": "http", "server": ("test", 80), "client": ("test", 1), "root_path": ""}
    await app(scope, receive, send)
    return sent


start, body = asyncio.run(call(app, "/hello"))
print(start["status"], dict(start["headers"])[b"content-type"])
print(body["body"])
```
```text
200 b'application/json'
b'{"msg":"hi"}'
```

FastAPI is *Starlette plus extras*, and Starlette is the ASGI toolkit; the layers look like this:

```text
  bytes from the socket
          |
          v
  +-----------------------+
  | ASGI server           |  uvicorn (or hypercorn): sockets, HTTP parsing, event loop
  +----------+------------+
             |  await app(scope, receive, send)
             v
  +-----------------------+
  | Middleware stack      |  your middleware, CORS, error handling (Starlette)
  +----------+------------+
             v
  +-----------------------+
  | Router                |  match path + method (Starlette)
  +----------+------------+
             v
  +-----------------------+
  | FastAPI request logic |  read params -> Pydantic validation -> dependencies
  +----------+------------+
             v
  +-----------------------+
  | YOUR endpoint         |  def / async def  -> return value
  +----------+------------+
             v
  +-----------------------+
  | Response building     |  response_model filtering -> JSON -> Response
  +-----------------------+
```

You can run a WSGI app under ASGI and the other way round with adapters, but in practice you pick one. The mental model to keep: **ASGI is the contract, uvicorn is the server, Starlette is the toolkit, Pydantic is the validator, FastAPI is the glue.**

## 2. The smallest app, and how to run it

### 2.1 Hello, FastAPI

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}


client = TestClient(app)
response = client.get("/")
print(response.status_code)
print(response.headers["content-type"])
print(response.json())
```
```text
200
application/json
{'message': 'Hello, FastAPI!'}
```

Four things happened that you did not write:

1. `@app.get("/")` registered a route for method GET and path `/`.
2. The returned `dict` was turned into JSON, and `Content-Type: application/json` was set. (Flask 2.2+ does this too; older frameworks make you call `jsonify`.)
3. The status defaulted to 200.
4. `TestClient` called the ASGI app in-process. It is built on an `httpx`-compatible client (swe.02 section 19), so its API is the `httpx` API you already know: `.get`, `.post(json=...)`, `.status_code`, `.json()`.

### 2.4 Running a real server

`TestClient` is for tests. To serve real traffic you need an ASGI server. The standard one is **uvicorn**. In this course environment uvicorn is not installed, so we check honestly:

```bash run error
python -c "import uvicorn" 2>&1 | tail -1
```
```text
ModuleNotFoundError: No module named 'uvicorn'
```

> **Try it on your machine**
>
> ```bash
> pip install uvicorn
> uvicorn main:app --reload        # main.py contains the app; "app" is the variable name
> ```
>
> Expected: uvicorn prints a line like `Uvicorn running on http://127.0.0.1:8000` and `Application startup complete.` Open `http://127.0.0.1:8000/` in a browser to see the JSON, and `http://127.0.0.1:8000/docs` for the interactive documentation. `--reload` restarts the server when you save a file (development only). Press Ctrl+C to stop. (Port numbers and process ids in the log are machine-specific.)

The string `main:app` means "import module `main`, take its attribute `app`". This is the same convention as Gunicorn's `module:app` in swe.04.

## 3. Path, query, header and cookie parameters

### 3.1 The rule: where does each parameter come from?

FastAPI decides where to read a function parameter by looking at the function signature, not at a `request` object:

| The parameter... | is read from |
|---|---|
| appears in the path as `{name}` | the **path** |
| has a simple type (`int`, `str`, `bool`, `float`...) and is not in the path | the **query string** |
| has a Pydantic model (or `BaseModel`) type | the JSON **body** |
| is declared with `Header(...)` | an HTTP **header** |
| is declared with `Cookie(...)` | a **cookie** |

This is the single most important rule of the chapter. The *type* and the *name* in your signature are the specification of the API.

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/users/{user_id}/posts")
def user_posts(user_id: int, limit: int = 10, draft: bool = False, tag: str | None = None):
    return {"user_id": user_id, "limit": limit, "draft": draft, "tag": tag}


client = TestClient(app)
print(client.get("/users/7/posts").json())
print(client.get("/users/7/posts?limit=3&draft=yes&tag=py").json())
```
```text
{'user_id': 7, 'limit': 10, 'draft': False, 'tag': None}
{'user_id': 7, 'limit': 3, 'draft': True, 'tag': 'py'}
```

What the framework did:

- `user_id` is in the path, so it comes from the URL, and `"7"` became the integer `7`.
- `limit` has a default, so it is **optional** in the query. `"3"` became `3`.
- `draft: bool` accepted `yes`: query values are *lax-converted*: `true`, `1`, `yes`, `on` become `True`; `false`, `0`, `no`, `off` become `False`.
- `tag: str | None = None` is an optional query parameter.

A parameter **without a default** and not in the path is **required**; leaving it out gives a `422` with `loc: ["query", "q"]` and `msg: "Field required"` (anatomy in section 6).

### 3.3 Constraints with `Query`, `Path` and `Annotated`

A type alone says "an int". Real APIs need "an int from 1 to 100". The tools are `Query(...)`, `Path(...)`, `Header(...)`, `Cookie(...)`. The modern way to attach them is `typing.Annotated`:

```text
name: Annotated[<type>, <extra metadata>] = <default>
```

`Annotated[int, Query(ge=1, le=100)]` means "an `int`, and here is extra information for the framework". Python itself ignores the metadata (core.09), but FastAPI and Pydantic read it.

```python run
from typing import Annotated
from fastapi import FastAPI, Path, Query
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/products/{product_id}")
def search(
    product_id: Annotated[int, Path(ge=1, description="Database id of the product")],
    q: Annotated[str | None, Query(min_length=2, max_length=20, pattern="^[a-z]+$")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=50)] = 10,
    tags: Annotated[list[str] | None, Query()] = None,
):
    return {"product_id": product_id, "q": q, "page": page, "size": size, "tags": tags}


client = TestClient(app)
print(client.get("/products/5?q=shoe&tags=a&tags=b").json())

for url in ["/products/0", "/products/5?size=500", "/products/5?q=Shoe", "/products/5?q=x"]:
    err = client.get(url).json()["detail"][0]
    print(f"{url:24} -> {err['loc']}  {err['msg']}")
```
```text
{'product_id': 5, 'q': 'shoe', 'page': 1, 'size': 10, 'tags': ['a', 'b']}
/products/0              -> ['path', 'product_id']  Input should be greater than or equal to 1
/products/5?size=500     -> ['query', 'size']  Input should be less than or equal to 50
/products/5?q=Shoe       -> ['query', 'q']  String should match pattern '^[a-z]+$'
/products/5?q=x          -> ['query', 'q']  String should have at least 2 characters
```

Points worth remembering:

- A **list in the query** needs `Query()` explicitly: `?tags=a&tags=b` repeats the key. Without `Query()`, a `list[str]` parameter would be read from the *body*.
- Constraint names: numbers use `gt`, `ge`, `lt`, `le`; strings use `min_length`, `max_length`, `pattern`. They are Pydantic's and work in models too.
- The old style `q: str = Query(None, min_length=3)` still works but mixes the default with the metadata. Prefer `Annotated`; you can also name a constrained type once (`PageSize = Annotated[int, Query(ge=1, le=50)]`) and reuse it as `size: PageSize = 10`.

### 3.4 Headers and cookies

HTTP headers use dashes (`User-Agent`); Python names cannot. FastAPI converts underscores to dashes for you, and header names are case-insensitive (swe.02 section 11):

```python run
from typing import Annotated
from fastapi import Cookie, FastAPI, Header
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/whoami")
def whoami(
    user_agent: Annotated[str | None, Header()] = None,
    x_request_id: Annotated[str | None, Header()] = None,
    session: Annotated[str | None, Cookie()] = None,
):
    return {"user_agent": user_agent, "x_request_id": x_request_id, "session": session}


client = TestClient(app)
print(client.get("/whoami", headers={"X-Request-ID": "abc-1", "User-Agent": "demo"}, cookies={"session": "s123"}).json())
```
```text
{'user_agent': 'demo', 'x_request_id': 'abc-1', 'session': 's123'}
```

`user_agent` was matched to the header `User-Agent`, and `x_request_id` to `X-Request-ID`. To receive the real dashed name keep the Python name and pass `Header(alias="X-Request-ID")`; to keep underscores on the wire, set `convert_underscores=False`.

A repeated header (`X-Token` twice) is read with `list[str]`.

### Try it: constrain a parameter

Write an endpoint `GET /square/{n}` where `n` is an integer between 1 and 20, and returns `{"n": n, "square": n*n}`. What does `/square/21` return?

<details><summary>Answer</summary>

```python
from typing import Annotated
from fastapi import FastAPI, Path
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/square/{n}")
def square(n: Annotated[int, Path(ge=1, le=20)]):
    return {"n": n, "square": n * n}

client = TestClient(app)
print(client.get("/square/4").json())
for url in ("/square/21", "/square/abc"):
    e = client.get(url).json()["detail"][0]
    print(url, client.get(url).status_code, e["loc"], e["msg"])
```

```text
{'n': 4, 'square': 16}
/square/21 422 ['path', 'n'] Input should be less than or equal to 20
/square/abc 422 ['path', 'n'] Input should be a valid integer, unable to parse string as an integer
```

</details>

## 4. Request bodies

### 4.1 A Pydantic model as the body

For `POST`, `PUT` and `PATCH` the data usually travels as JSON in the body (swe.02 section 14). You describe its shape with a **Pydantic model**, which is a class whose attributes are type hints:

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


class TaskIn(BaseModel):
    title: str
    done: bool = False
    priority: int = 3


@app.post("/tasks")
def create_task(task: TaskIn):
    # By the time this line runs, `task` is a real TaskIn object with correct types.
    return {"received": task.title, "type": type(task).__name__, "priority_plus_1": task.priority + 1}


client = TestClient(app)
print(client.post("/tasks", json={"title": "write chapter"}).json())
print(client.post("/tasks", json={"title": "write chapter", "priority": "5"}).json())
```
```text
{'received': 'write chapter', 'type': 'TaskIn', 'priority_plus_1': 4}
{'received': 'write chapter', 'type': 'TaskIn', 'priority_plus_1': 6}
```

Three important facts:

1. The parameter `task: TaskIn` is a model, so FastAPI reads it from the **body**.
2. The JSON `"priority": "5"` (a string) was **converted** to the integer 5 (this is Pydantic's default *lax* mode, section 5.4).
3. Inside the function there is **no checking code**. If the body were wrong, the function would never have been called. That is the contract.

### 4.2 Several body parts and `Body`

If you declare **two** models, FastAPI expects a JSON object with one key per parameter name:

```python run
from typing import Annotated
from fastapi import Body, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str

class User(BaseModel):
    username: str

@app.put("/items/{item_id}")
def update(item_id: int, item: Item, user: User, importance: Annotated[int, Body(ge=1)] = 1):
    return {"item_id": item_id, "item": item, "user": user, "importance": importance}

client = TestClient(app)
body = {"item": {"name": "lamp"}, "user": {"username": "kavya"}, "importance": 2}
print(client.put("/items/9", json=body).json())
```
```text
{'item_id': 9, 'item': {'name': 'lamp'}, 'user': {'username': 'kavya'}, 'importance': 2}
```

### 4.3 Invalid JSON versus invalid data

Two different failures, two different messages:

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()

class TaskIn(BaseModel):
    title: str

@app.post("/tasks")
def create(task: TaskIn):
    return task

client = TestClient(app)
r = client.post("/tasks", content=b'{"title": ', headers={"content-type": "application/json"})
print(r.status_code, r.json()["detail"][0]["type"])
r = client.post("/tasks", json={"title": 123})
print(r.status_code, r.json()["detail"][0]["type"])
```
```text
422 json_invalid
422 string_type
```

Broken JSON gives `json_invalid`; valid JSON with the wrong shape gives a field error. Both are `422` here (Flask-style apps often use 400 for the first; you can override it, section 8).

## 5. Pydantic v2 in depth

Pydantic is the heart of FastAPI. It deserves its own section, and it is useful far outside web apps (config files, parsing API responses, CLI tools).

### 5.1 Hints describe; Pydantic enforces

Recall core.09: Python ignores type hints at runtime. ```python run
(`def double(n: int)` called as `double("ab")` just returns `"abab"`; no error.)

A Pydantic `BaseModel` reads the hints and **checks them at runtime**, when you create an object:

```python run
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str
    active: bool = True

u = User(id="42", name="Asha")           # "42" is converted to 42
print(u)
print(repr(u.id), type(u.id).__name__)

try:
    User(id="forty-two", name=None)
except ValidationError as e:
    print(e.error_count(), "errors")
    print(e)
```
```text
id=42 name='Asha' active=True
42 int
2 errors
2 validation errors for User
id
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='forty-two', input_type=str]
    For further information visit https://errors.pydantic.dev/2.14/v/int_parsing
name
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.14/v/string_type
```

Study the error text: it lists **every** problem at once (not just the first), each with the field name, a human message, the input value and a docs link. This "collect all errors" behaviour is what makes API validation friendly: the client fixes everything in one round trip.

### 5.2 Defaults, optional and required

In Pydantic v2 the rules are strict and simple:

- `x: int`: required, must be an int.
- `x: int = 5`: optional, defaults to 5.
- `x: int | None` (no default): **required**, but the value may be `None`. This is a v2 change.
- `x: int | None = None`: optional; may be omitted or `None`.
- `x: list[int] = []`: optional, and **safe**: Pydantic copies the default for each instance.

The third line catches many people: in v2 `int | None` without a default is still *required*. Mutable defaults are copied for you, unlike a plain Python function default (core.07).

Mutable defaults are copied for you, unlike a plain function default (core.07).

### 5.3 `Field`: constraints, descriptions, aliases

`Field(...)` attaches rules and metadata to one attribute. The constraint names are the same as `Query` (section 3.3):

```python run
from typing import Annotated
from pydantic import BaseModel, Field, ValidationError

class Product(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="Shown to customers")
    price: float = Field(gt=0, examples=[9.99])
    tags: list[str] = Field(default_factory=list, max_length=5)
    sku: Annotated[str, Field(pattern=r"^[A-Z]{3}-\d{4}$")]

p = Product(name="Lamp", price=19.5, sku="LMP-0001")
print(p)

try:
    Product(name="L", price=0, sku="bad", tags=list("abcdefg"))
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], "|", err["msg"])
```
```text
name='Lamp' price=19.5 tags=[] sku='LMP-0001'
('name',) | String should have at least 2 characters
('price',) | Input should be greater than 0
('tags',) | List should have at most 5 items after validation, not 7
('sku',) | String should match pattern '^[A-Z]{3}-\d{4}$'
```

`default_factory=list` means "call `list()` for each new object". `examples` and `description` show up in the generated docs (section 19).

### 5.4 Lax versus strict mode, and coercion

By default Pydantic is **lax**: it converts values when the conversion is unambiguous and lossless.

```python run
from pydantic import BaseModel, ConfigDict, ValidationError

class Lax(BaseModel):
    n: int
    f: float
    b: bool

print(Lax(n="7", f="2.5", b="yes"))
print(Lax(n=7.0, f=1, b=0))

try:
    Lax(n=7.5, f=1, b=True)
except ValidationError as e:
    print(e.errors()[0]["msg"])

class Strict(BaseModel):
    model_config = ConfigDict(strict=True)
    n: int

try:
    Strict(n="7")
except ValidationError as e:
    print(e.errors()[0]["msg"])
```
```text
n=7 f=2.5 b=True
n=7 f=1.0 b=False
Input should be a valid integer, got a number with a fractional part
Input should be a valid integer
```

Use the rule of thumb: for **JSON bodies** lax is usually fine, because JSON has few types. For **internal data you control**, or where `"1"` silently becoming `1` hides a client bug, use strict (per model with `ConfigDict(strict=True)`, per field with `Field(strict=True)`).

### 5.5 Field validators

When a rule is not expressible as a constraint, write a validator. `field_validator` runs for one field, by default **after** the type conversion ("after" mode), so you work with a clean value:

```python run
from pydantic import BaseModel, ValidationError, field_validator

class Signup(BaseModel):
    username: str
    email: str

    @field_validator("username")
    @classmethod
    def clean_username(cls, v: str) -> str:
        v = v.strip().lower()
        if not v.isidentifier():
            raise ValueError("username must be letters, digits and underscores")
        return v

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        if "@" not in v or v.startswith("@") or v.endswith("@"):
            raise ValueError("not a valid email address")
        return v.lower()

print(Signup(username="  Kavya_B ", email="K@Example.COM"))
try:
    Signup(username="bad name", email="nope")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], err["msg"])
```
```text
username='kavya_b' email='k@example.com'
('username',) Value error, username must be letters, digits and underscores
('email',) Value error, not a valid email address
```

Rules for validators:

- `@field_validator("name")` goes **above** `@classmethod`.
- Raise `ValueError` (or `AssertionError`) for a user error; Pydantic turns it into an error entry and prefixes `Value error, `.
- **Return the value.** Forgetting `return v` makes the field `None`. This is the classic validator bug.
- `mode="before"` runs *before* conversion, on raw input, useful to accept `"1,2,3"` for a `list[int]`.

### 5.6 Model validators: rules across fields

A rule that involves several fields needs `model_validator`:

```python run
from datetime import date
from pydantic import BaseModel, ValidationError, model_validator

class Booking(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def check_order(self):
        if self.end < self.start:
            raise ValueError("end must not be before start")
        return self

print(Booking(start="2026-01-10", end="2026-01-12"))
try:
    Booking(start="2026-01-10", end="2026-01-01")
except ValidationError as e:
    err = e.errors()[0]
    print(err["loc"], err["msg"])
```
```text
start=datetime.date(2026, 1, 10) end=datetime.date(2026, 1, 12)
() Value error, end must not be before start
```

Note `loc` is empty (`()`): the problem belongs to the whole object, not a field. In an API this shows as `["body"]`.

### 5.7 Dumping and loading: `model_dump`, `model_validate`

Models convert both ways (in v1 these were `.dict()` and `.parse_obj()`, now deprecated):

```python run
from datetime import datetime
from pydantic import BaseModel

class Event(BaseModel):
    name: str
    at: datetime
    note: str | None = None

e = Event.model_validate({"name": "launch", "at": "2026-03-01T09:30:00"})
print(e.model_dump())
print(e.model_dump(mode="json"))
print(e.model_dump(exclude_none=True))
print(e.model_dump_json())
print(Event.model_validate_json('{"name": "x", "at": "2026-03-01T00:00:00"}').at.year)
```
```text
{'name': 'launch', 'at': datetime.datetime(2026, 3, 1, 9, 30), 'note': None}
{'name': 'launch', 'at': '2026-03-01T09:30:00', 'note': None}
{'name': 'launch', 'at': datetime.datetime(2026, 3, 1, 9, 30)}
{"name":"launch","at":"2026-03-01T09:30:00","note":null}
2026
```

- `model_dump()` gives Python values (a real `datetime`).
- `model_dump(mode="json")` gives only JSON-safe values (the date becomes a string). FastAPI uses this behaviour when it writes responses.
- `exclude_none`, `exclude_unset`, `include`, `exclude` filter the output. `exclude_unset=True` means "only fields the caller actually sent", which is the key to correct `PATCH` (section 7.5).
- `model_validate_json` parses and validates JSON text in one fast step.

### 5.8 Nested models, lists and unions

```python run
from pydantic import BaseModel, ValidationError

class Address(BaseModel):
    city: str
    zip: str

class Customer(BaseModel):
    name: str
    address: Address
    phones: list[str] = []
    meta: dict[str, int] = {}

c = Customer.model_validate({"name": "A", "address": {"city": "Pune", "zip": "411001"}, "meta": {"visits": "3"}})
print(c.address.city, c.meta)

try:
    Customer.model_validate({"name": "A", "address": {"city": "Pune"}, "phones": ["1", 2]})
except ValidationError as e:
    for err in e.errors():
        print(err["loc"], err["msg"])
```
```text
Pune {'visits': 3}
('address', 'zip') Field required
('phones', 1) Input should be a valid string
```

Look at the `loc` tuples: they are **paths** into the structure (`('address', 'zip')`, `('phones', 1)`). That path is what makes errors in deep JSON bodies easy to find.

A **union** (`int | str`) tries each member and, in v2 "smart mode", prefers an exact type match (`"5"` stays a string, `5` stays an int).

### 5.9 Discriminated unions

Suppose a payload is *either* a card or a bank payment. A plain union tries every option and errors are noisy. A **discriminated union** looks at one tag field and picks the right model directly:

```python run
from typing import Annotated, Literal
from pydantic import BaseModel, Field, ValidationError

class Card(BaseModel):
    kind: Literal["card"]
    number: str

class Bank(BaseModel):
    kind: Literal["bank"]
    iban: str

class Payment(BaseModel):
    method: Annotated[Card | Bank, Field(discriminator="kind")]

print(Payment.model_validate({"method": {"kind": "bank", "iban": "DE00"}}))
try:
    Payment.model_validate({"method": {"kind": "bank", "number": "4111"}})
except ValidationError as e:
    err = e.errors()[0]
    print(err["loc"], err["msg"])
```
```text
method=Bank(kind='bank', iban='DE00')
('method', 'bank', 'iban') Field required
```

The error points straight at `('method', 'bank', 'iban')`: only the `Bank` model was checked. A tag that matches no member gives `union_tag_invalid`. Use a discriminator whenever a tag field exists.

### 5.10 Computed fields and serialization aliases

A `computed_field` is a property that is included when the model is dumped (and shown in the docs):

```python run
from pydantic import BaseModel, Field, computed_field

class Rect(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height

print(Rect(width=3, height=4).model_dump())
```
```text
{'width': 3.0, 'height': 4.0, 'area': 12.0}
```

**Aliases** let the Python name and the wire name differ. Python wants `snake_case`; many JSON APIs use `camelCase`:

```python run
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class Profile(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
    first_name: str
    due_date: str | None = None

p = Profile.model_validate({"firstName": "Asha", "dueDate": "tomorrow"})
print(p.first_name)
print(p.model_dump())
print(p.model_dump(by_alias=True))
print(Profile(first_name="B"))                       # populate_by_name allows the Python name too
```
```text
Asha
{'first_name': 'Asha', 'due_date': 'tomorrow'}
{'firstName': 'Asha', 'dueDate': 'tomorrow'}
first_name='B' due_date=None
```

Without `by_alias=True` the dump uses Python names. FastAPI's `response_model_by_alias` defaults to **True**, so a response model with an alias generator emits camelCase automatically (checked in section 7).

### 5.11 `from_attributes`: models from ORM objects

An ORM object (swe.03) is not a dict. By default Pydantic refuses to read attributes from arbitrary objects. `ConfigDict(from_attributes=True)` allows it; that is how a SQLAlchemy row becomes a response:

```python run
from pydantic import BaseModel, ConfigDict

class FakeOrmUser:                     # imagine a SQLAlchemy model
    def __init__(self):
        self.id, self.name, self.password_hash = 1, "Asha", "pbkdf2$secret"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str                          # only these fields are copied; the hash is not

print(UserOut.model_validate(FakeOrmUser()))
```
```text
id=1 name='Asha'
```

Notice what happened to `password_hash`: `UserOut` does not declare it, so it is **left out**. This is the mechanism behind "never leak a password hash" (section 7.2).

## 6. Where validation happens: the 422 response

### 6.1 The request lifecycle

Here is the path of one request through FastAPI, with the places where things can be rejected:

```text
  HTTP request
      |
      v
  +-----------------------------+
  | 1. Routing                  |--- no path match ------------> 404
  |    path + method            |--- path ok, wrong method -----> 405
  +--------------+--------------+
                 v
  +-----------------------------+
  | 2. Read raw pieces          |
  |    path, query, headers,    |--- body not valid JSON ------> 422 (json_invalid)
  |    cookies, body            |
  +--------------+--------------+
                 v
  +-----------------------------+
  | 3. Pydantic validation      |
  |    every parameter + body   |--- any rule broken ----------> 422
  |    + sub-dependencies       |        (ALL errors collected, then one response)
  +--------------+--------------+
                 v
  +-----------------------------+
  | 4. YOUR endpoint runs       |--- raise HTTPException -------> 4xx/5xx you choose
  |    (only if 1-3 passed)     |--- bug / unhandled error -----> 500
  +--------------+--------------+
                 v
  +-----------------------------+
  | 5. response_model filter    |--- return value does not fit --> 500 (ResponseValidationError)
  |    + JSON serialisation     |
  +--------------+--------------+
                 v
              HTTP response
```

The key idea: **steps 2 and 3 happen before your function is called.** So a `422` means "your request was understood as HTTP, but the data did not satisfy the declared types and constraints". It is a *client* error. The server code did not run.

### 6.2 The anatomy of a 422

Every 422 body has the shape `{"detail": [ error, error, ... ]}` with one entry per problem. Let us make several problems at once, in a path, a query parameter, a header and a body field:

```python run
import json
from typing import Annotated
from fastapi import FastAPI, Header, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

class TaskIn(BaseModel):
    title: str = Field(min_length=3)
    priority: int = Field(ge=1, le=5)

app = FastAPI()

@app.post("/projects/{project_id}/tasks")
def create(
    project_id: int,
    task: TaskIn,
    notify: Annotated[bool, Query()] = False,
    x_client: Annotated[str, Header()] = "web",
):
    return {"ok": True}

client = TestClient(app)
r = client.post(
    "/projects/abc/tasks?notify=maybe",
    json={"title": "x", "priority": 9},
)
print(r.status_code)
print(json.dumps(r.json()['detail'][0], indent=2))
print(json.dumps(r.json()['detail'][3], indent=2))
print(len(r.json()['detail']), 'errors in total:', [e['loc'][-1] for e in r.json()['detail']])
```
```text
422
{
  "type": "int_parsing",
  "loc": [
    "path",
    "project_id"
  ],
  "msg": "Input should be a valid integer, unable to parse string as an integer",
  "input": "abc"
}
{
  "type": "less_than_equal",
  "loc": [
    "body",
    "priority"
  ],
  "msg": "Input should be less than or equal to 5",
  "input": 9,
  "ctx": {
    "le": 5
  }
}
4 errors in total: ['project_id', 'notify', 'title', 'priority']
```

Read each entry. The fields are:

| Key | Meaning |
|---|---|
| `type` | A stable **machine-readable** code (`int_parsing`, `bool_parsing`, `string_too_short`, `less_than_equal`, `missing`...). Clients should switch on this, not on `msg`. |
| `loc` | **Where**: first item is the source (`path`, `query`, `header`, `cookie`, `body`), the rest is the path inside it. For a body field: `["body", "priority"]`. |
| `msg` | A **human** sentence. May be shown to users, but its wording can change between versions. |
| `input` | The value the client actually sent (useful for debugging; consider whether echoing it is safe for secrets). |
| `ctx` | Extra details such as the limit: `{"le": 5}`. Present only for some errors. |

Notice that **all four problems were reported together**. The client does not need four round trips.

### 6.3 What a 422 is NOT

- It is **not** a server bug. Do not alert on it like a 500; do count it in metrics, because a sudden spike usually means a client shipped a broken release.
- It is **not** 400. FastAPI uses 422 ("Unprocessable Content") for "well-formed request, semantically invalid data". Some APIs prefer 400; section 8.2 shows how to change it.
- Business-rule failures (username taken, balance too low) are **not** validation errors in this sense. They are decided inside your endpoint, using the database, and should be `409`, `403` or a custom `4xx` via `HTTPException`.


## 7. Responses: response_model and status codes

### 7.1 Returning a model, and `response_model`

You can return a dict, a list, a Pydantic model, or an ORM-like object. To control the **shape of the output**, declare a response model. FastAPI then (1) validates and filters what you returned against it, (2) serialises to JSON, (3) documents it.

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

class TaskOut(BaseModel):
    id: int
    title: str
    done: bool

app = FastAPI()

@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int):
    # We return MORE than TaskOut declares; the extra key is dropped.
    return {"id": task_id, "title": "write", "done": False, "internal_note": "do not show"}

print(TestClient(app).get("/tasks/1").json())
```
```text
{'id': 1, 'title': 'write', 'done': False}
```

A return **annotation** does the same job in modern FastAPI: `def get_task(task_id: int) -> TaskOut:`. Use `response_model=` when the function returns something that is *not* literally the model (a dict, an ORM object, a subclass), as above.

### 7.2 Never leak a password hash

This is the most important use of response models. Keep **separate models** for input, storage and output:

```text
   UserCreate            UserDB                 UserOut
   (what clients send)   (what is stored)       (what clients get back)
   - email               - id                   - id
   - password  ------->  - email   ---------->  - email
                         - password_hash        (no hash, no password)
```

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=8)

class UserDB(BaseModel):                 # stands in for the database row
    id: int
    email: str
    password_hash: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str

app = FastAPI()
FAKE_DB: dict[int, UserDB] = {}

@app.post("/users", response_model=UserOut, status_code=201)
def register(data: UserCreate):
    row = UserDB(id=len(FAKE_DB) + 1, email=data.email, password_hash="pbkdf2$" + data.password[::-1])
    FAKE_DB[row.id] = row
    return row                           # we return the FULL row on purpose

r = TestClient(app).post("/users", json={"email": "a@b.co", "password": "longpassword"})
print(r.status_code, r.json())
print("stored row still has:", sorted(FAKE_DB[1].model_dump()))
```
```text
201 {'id': 1, 'email': 'a@b.co'}
stored row still has: ['email', 'id', 'password_hash']
```

The endpoint returned the whole `UserDB` including the hash, and the response still had only `id` and `email`. The **filter is a safety net**: even if a later change returns the wrong object, the secret field cannot escape, because the response model does not declare it. (Compare Flask in swe.04 section 18, where you must remember to leave the field out of every `jsonify` by hand.)

> **Rule.** Never use the same Pydantic class for input and output when they differ, and never use the database class as the response model.

### 7.5 Partial updates with `PATCH`

With `PUT` the client sends everything. With `PATCH` it sends only what changes. To tell "the client did not send `title`" from "the client sent `title: null`", use `model_dump(exclude_unset=True)`:

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

class TaskPatch(BaseModel):
    title: str | None = None
    done: bool | None = None
    note: str | None = None

app = FastAPI()
TASK = {"title": "old", "done": False, "note": "keep me"}

@app.patch("/task")
def patch(data: TaskPatch):
    changes = data.model_dump(exclude_unset=True)       # only what the client really sent
    TASK.update(changes)
    return {"changes": changes, "task": TASK}

c = TestClient(app)
print(c.patch("/task", json={"done": True}).json())
print(c.patch("/task", json={"note": None}).json())
```
```text
{'changes': {'done': True}, 'task': {'title': 'old', 'done': True, 'note': 'keep me'}}
{'changes': {'note': None}, 'task': {'title': 'old', 'done': True, 'note': None}}
```

Without `exclude_unset=True` the second call would also have overwritten `title` and `done` with `None`. That is a very common data-loss bug.

### 7.6 Status codes

Set the success status on the decorator. Use the named constants from `fastapi.status` for readability, or plain numbers:

```python run
from fastapi import FastAPI, Response, status
from fastapi.testclient import TestClient

app = FastAPI()
ITEMS = {}

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create(response: Response):
    ITEMS[1] = "x"
    response.headers["Location"] = "/items/1"           # tell the client where it lives
    return {"id": 1}

c = TestClient(app)
r = c.post("/items")
print(r.status_code, r.headers["location"], r.json())
```
```text
201 /items/1 {'id': 1}
```

The `Response` parameter is a "scratch" response: you set headers, cookies and the status on it, and FastAPI merges them into the real one. For a 204 the body must be empty; FastAPI handles that when you declare `status_code=204` and return nothing.

If you need full control, return a `Response` object yourself (`JSONResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`). Returning a response object **skips** `response_model` filtering; that is the trade-off.

### Try it: the leaky response

An output model accidentally declares `password_hash: str`. Does `response_model` still protect you? Check what a test should assert.

<details><summary>Answer</summary>

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    password_hash: str          # the mistake

app = FastAPI()

@app.get("/u", response_model=UserOut)
def u():
    return {"id": 1, "password_hash": "secret"}

body = TestClient(app).get("/u").json()
print(body)
print("leaked:", "password_hash" in body)
```

```text
{'id': 1, 'password_hash': 'secret'}
leaked: True
```

</details>

The filter only removes what is **not declared**, so a declared secret passes straight through. The habit that catches it: keep output models in one `schemas` module where each field is a deliberate choice, and test `assert "password_hash" not in response.json()`.

## 8. Error handling

### 8.1 `HTTPException`

Business-level failures (not found, forbidden, conflict) are raised inside the endpoint with `HTTPException`. Raising stops the function immediately, and FastAPI turns it into a response:

```python run
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

app = FastAPI()
TASKS = {1: "write chapter"}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in TASKS:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found")
    return {"id": task_id, "title": TASKS[task_id]}

c = TestClient(app)
r = c.get("/tasks/9"); print(r.status_code, r.json())
```
```text
404 {'detail': 'Task 9 not found'}
```

`detail` can be any JSON-able value, not only a string. Use the right code (swe.02 section 10): 404 missing, 403 not allowed, 409 conflict (duplicate), 401 not authenticated.

> **Trap.** Use `HTTPException` from `fastapi`, not from `starlette.exceptions`, in your endpoints. FastAPI's one is a subclass that adds the `headers` argument. Handlers for the Starlette class catch both.

### 8.2 One error shape for your whole API

The default shapes differ: HTTP errors give `{"detail": "..."}`, validation errors give `{"detail": [ ... ]}`. A consistent API (swe.04 section 19) wants one envelope. Register **exception handlers**:

```python run
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

def envelope(status, code, message, details=None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(body, status_code=status)

@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    return envelope(exc.status_code, "http_error", str(exc.detail))

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "problem": e["msg"]} for e in exc.errors()]
    return envelope(400, "validation_failed", "Request data is invalid", details)

class In(BaseModel):
    title: str
    priority: int

@app.post("/tasks")
def create(task: In):
    return task

@app.get("/boom")
def boom():
    raise HTTPException(404, "no such thing")

c = TestClient(app)
print(c.post("/tasks", json={"priority": "x"}).json())
print(c.get("/boom").json())
print(c.get("/not-a-route").json())
```
```text
{'error': {'code': 'validation_failed', 'message': 'Request data is invalid', 'details': [{'field': 'title', 'problem': 'Field required'}, {'field': 'priority', 'problem': 'Input should be a valid integer, unable to parse string as an integer'}]}}
{'error': {'code': 'http_error', 'message': 'no such thing'}}
{'error': {'code': 'http_error', 'message': 'Not Found'}}
```

Three things to notice:

- Overriding `RequestValidationError` is how you **change a 422 into a 400** (or any shape). Many teams do so to match a company convention.
- We registered the handler for the **Starlette** exception class, so it also catches the automatic 404 for unknown routes (the third line).
- `exc.errors()` is the same list of dicts you saw in the 422 body, so you can reshape it freely.

### 8.4 Unhandled exceptions are 500s

Any exception you do not handle becomes `500 Internal Server Error`. In production the body is a plain `Internal Server Error` with no traceback (never expose tracebacks). `TestClient` re-raises server exceptions by default so your test fails loudly; to see the 500 response instead, construct it with `raise_server_exceptions=False`:

```python run
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/bug")
def bug():
    return 1 / 0

r = TestClient(app, raise_server_exceptions=False).get("/bug")
print(r.status_code, r.text)
```
```text
500 Internal Server Error
```

## 9. Dependency injection

### 9.1 The problem it solves

Almost every endpoint needs the same things: a database session, the logged-in user, pagination parameters, settings. Without a pattern you copy the same four lines everywhere, and tests must patch globals. **Dependency injection (DI)** inverts that: the endpoint *declares* what it needs, and the framework *provides* it.

A **dependency** is just a callable (function or class). You list it with `Depends(...)`:

```python run
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

def pagination(limit: int = 10, offset: int = 0):
    return {"limit": limit, "offset": offset}

@app.get("/a")
def list_a(page: Annotated[dict, Depends(pagination)]):
    return {"list": "a", **page}

@app.get("/b")
def list_b(page: Annotated[dict, Depends(pagination)]):
    return {"list": "b", **page}

c = TestClient(app)
print(c.get("/a?limit=2").json())
print(c.get("/b?offset=5").json())
print(c.get("/a?limit=zero").status_code)
```
```text
{'list': 'a', 'limit': 2, 'offset': 0}
{'list': 'b', 'limit': 10, 'offset': 5}
422
```

`pagination` declares its own parameters (`limit`, `offset`); FastAPI reads them from the query, validates them (the last call is a 422 without the endpoint or `pagination` running), calls `pagination`, and passes the **return value** to the endpoint. The parameters of dependencies show up in the docs for every endpoint that uses them.

### 9.2 Reuse with a type alias

Make an alias once, `Page = Annotated[dict, Depends(pagination)]`, then write `def list_a(page: Page): ...`.

### 9.3 Sub-dependencies and the dependency tree

A dependency can depend on other dependencies. FastAPI builds a tree and resolves it from the leaves up:

```text
  endpoint  create_task(task, user, db)
                |             |      |
                |       current_user   get_db
                |             |  \
                |      token_from_header  get_db   <- same get_db: computed ONCE per request
                v
          body validated
```

```python run
from typing import Annotated
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
calls = []

def get_db():
    calls.append("get_db")
    return {"users": {"tok-1": "asha"}}

def get_token(authorization: Annotated[str | None, Header()] = None):
    calls.append("get_token")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    return authorization.removeprefix("Bearer ")

def current_user(token: Annotated[str, Depends(get_token)], db: Annotated[dict, Depends(get_db)]):
    calls.append("current_user")
    user = db["users"].get(token)
    if user is None:
        raise HTTPException(401, "Bad token")
    return user

@app.get("/me")
def me(user: Annotated[str, Depends(current_user)], db: Annotated[dict, Depends(get_db)]):
    calls.append("endpoint")
    return {"user": user}

c = TestClient(app)
print(c.get("/me", headers={"Authorization": "Bearer tok-1"}).json(), calls)
calls.clear()
print(c.get("/me").status_code, calls)
```
```text
{'user': 'asha'} ['get_token', 'get_db', 'current_user', 'endpoint']
401 ['get_token']
```

Two observations from `calls`:

- `get_db` appears **once** even though both `current_user` and `me` asked for it. Within one request, FastAPI **caches** a dependency's result (same callable = same value). Use `Depends(get_db, use_cache=False)` to opt out.
- On the failing request, `get_token` raised `HTTPException`, so `current_user` and the endpoint **never ran**. Dependencies are a natural place for guard logic.

### 9.4 Class dependencies

A class is a callable, so it works as a dependency; its `__init__` parameters are read like function parameters:

```python run
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

class Pagination:
    def __init__(self, limit: int = 10, offset: int = 0):
        self.limit, self.offset = limit, offset

    def slice(self, items):
        return items[self.offset:self.offset + self.limit]

@app.get("/numbers")
def numbers(p: Annotated[Pagination, Depends()]):       # Depends() with no argument = use the annotated class
    return p.slice(list(range(100)))

print(TestClient(app).get("/numbers?limit=3&offset=10").json())
```
```text
[10, 11, 12]
```

### 9.5 Dependencies with `yield`: setup and cleanup

A database session must be **opened before** the endpoint and **closed after**, even if the endpoint fails. A dependency written with `yield` does exactly that (compare with `with` and generators, core.12/core.18):

```python run
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
log = []

def get_session():
    log.append("open session")
    session = {"open": True}
    try:
        yield session                    # the endpoint runs here
        log.append("commit")
    except Exception as exc:
        log.append(f"rollback ({type(exc).__name__})")
        raise
    finally:
        session["open"] = False
        log.append("close session")

@app.get("/ok")
def ok(s: Annotated[dict, Depends(get_session)]):
    log.append("endpoint ran")
    return {"open": s["open"]}

@app.get("/fail")
def fail(s: Annotated[dict, Depends(get_session)]):
    raise HTTPException(404, "nope")

c = TestClient(app)
c.get("/ok"); print(log); log.clear()
c.get("/fail"); print(log)
```
```text
['open session', 'endpoint ran', 'commit', 'close session']
['open session', 'rollback (HTTPException)', 'close session']
```

Order: code before `yield` runs before the endpoint; the yielded value is injected; code after `yield` runs after the response has been produced. An exception raised in the endpoint (including `HTTPException`) is thrown **into** the generator at the `yield`, so you can roll back. This is the standard shape of the database dependency in section 11.

### 9.6 `dependency_overrides`: the testing superpower

Because endpoints receive dependencies from outside, a test can replace them. `app.dependency_overrides` maps the original callable to a replacement:

```python run
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

def get_clock():
    import datetime
    return datetime.datetime.now()

@app.get("/year")
def year(now: Annotated[object, Depends(get_clock)]):
    return {"year": now.year}

app.dependency_overrides[get_clock] = lambda: __import__("datetime").datetime(2000, 1, 1)
print(TestClient(app).get("/year").json())
app.dependency_overrides.clear()                  # always clean up after a test
```
```text
{'year': 2000}
```

No monkeypatching, no global state: the same trick swaps a real database for an in-memory one and a real login for a fixed test user (section 20).

### Try it: count the calls

Two endpoints both depend on `get_db`. A request hits only `/a`. How many times does `get_db` run?

<details><summary>Answer</summary>

```python
from typing import Annotated
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
calls = []

def get_db():
    calls.append("get_db")
    return "db"

def repo(db: Annotated[str, Depends(get_db)]):
    return db

@app.get("/a")
def a(db: Annotated[str, Depends(get_db)], r: Annotated[str, Depends(repo)]): return "a"

@app.get("/b")
def b(db: Annotated[str, Depends(get_db)]): return "b"

c = TestClient(app)
c.get("/a"); print(len(calls))
c.get("/a"); print(len(calls))
```

```text
1
2
```

</details>

Once per request: the endpoint and `repo` share one cached result, and `/b` is never resolved. A second request starts a fresh cache, so the counter goes to 2.


## 10. async def versus def

### 10.1 What the event loop does

core.21 taught the idea: one thread, one **event loop**, and coroutines that hand control back at every `await`. FastAPI uses both styles, and the choice of `def` or `async def` for an endpoint changes *where it runs*:

```text
                 async def endpoint                      def endpoint
   runs in:      the event-loop thread itself            a worker thread from a pool (anyio/Starlette)
   while it      loop is FREE at each `await`,           loop stays free: the thread blocks,
   waits:        other requests run                      not the loop
   if you call   BLOCKS THE WHOLE LOOP:                  fine: only that thread waits
   time.sleep /  every other request freezes
   blocking I/O
   use for:      async libraries (httpx.AsyncClient,     blocking libraries (requests, sync DB
                 async DB drivers, asyncio.sleep)        drivers, file reads, CPU-light work)
```

The rule is short: **use `async def` only if everything slow inside it is `await`ed. If you use any blocking call, use plain `def`** and FastAPI will protect the loop for you.

### 10.2 Seeing it

We call the same app with five requests at once using an async client (`httpx.AsyncClient` over `ASGITransport`, in-process). Each endpoint "works" for 0.2 seconds in a different way. We print whether the total time was short (concurrent) or long (serialised), and the thread that ran the code:

```python run
import asyncio, threading, time
import httpx
from fastapi import FastAPI

app = FastAPI()

@app.get("/async-good")
async def async_good():
    await asyncio.sleep(0.2)                       # yields to the loop
    return {"thread": threading.current_thread().name}

@app.get("/async-bad")
async def async_bad():
    time.sleep(0.2)                                # BLOCKS the event loop
    return {"thread": threading.current_thread().name}

@app.get("/sync-ok")
def sync_ok():
    time.sleep(0.2)                                # blocks only a worker thread
    return {"thread": threading.current_thread().name}

async def five_at_once(path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        responses = await asyncio.gather(*[client.get(path) for _ in range(5)])
        elapsed = time.perf_counter() - start
    return elapsed, {r.json()["thread"] for r in responses}

for path in ("/async-good", "/async-bad", "/sync-ok"):
    elapsed, threads = asyncio.run(five_at_once(path))
    verdict = "concurrent (about 0.2s)" if elapsed < 0.6 else "serialised (about 1.0s)"
    print(f"{path:12} {verdict:24} threads={'main' if threads == {'MainThread'} else 'worker pool'}")
```
```text
/async-good  concurrent (about 0.2s)  threads=main
/async-bad   serialised (about 1.0s)  threads=main
/sync-ok     concurrent (about 0.2s)  threads=worker pool
```

Read the three lines:

- `/async-good`: all five waits overlap. Total about 0.2 s, on the main thread.
- `/async-bad`: `time.sleep` inside `async def` froze the loop, so the five requests ran one after another. About 1.0 s. **This is the most common FastAPI performance bug.**
- `/sync-ok`: a plain `def` with a blocking call is fine, because FastAPI runs it in a worker thread, so five run in parallel threads.

(The exact seconds vary by machine, which is why we print a verdict instead of the number. The pool size is limited, 40 threads by default, so extreme load on `def` endpoints queues too.)

### 10.3 Mixing: `run_in_threadpool` and `asyncio.to_thread`

Sometimes an `async def` endpoint must call one blocking function (a hashing routine, an old SDK). Push that call to a thread:

```python run
import asyncio, hashlib
from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.testclient import TestClient

app = FastAPI()

def slow_hash(text: str) -> str:                      # blocking, CPU-bound
    return hashlib.scrypt(text.encode(), salt=b"s" * 16, n=2**14, r=8, p=1).hex()[:16]

@app.get("/hash/{text}")
async def hash_it(text: str):
    digest = await run_in_threadpool(slow_hash, text)       # or: await asyncio.to_thread(slow_hash, text)
    return {"digest": digest}

print(TestClient(app).get("/hash/hello").json())
```
```text
{'digest': 'b80954909b38f4b2'}
```

Remember (core.21): threads help with **waiting** (I/O) and with C code that releases the GIL, such as `hashlib` and `scrypt`. For heavy pure-Python CPU work use a process pool or a task queue, not either kind of endpoint.

## 11. Async database access

swe.03 section 17 introduced async SQLAlchemy. Here it is inside a real app. The pieces are the same as the synchronous ones (engine, session, models), with `await` on every operation that touches the database.

### 11.1 Setup: engine, session factory, lifespan

Three decisions:

- URL scheme `sqlite+aiosqlite://` selects the async driver. (For PostgreSQL it would be `postgresql+asyncpg://`.)
- `async_sessionmaker(..., expire_on_commit=False)`. After `commit()`, SQLAlchemy normally *expires* all loaded attributes, so the next attribute access triggers a lazy reload. In async code that reload is **forbidden** (11.5). Turning expiry off keeps loaded objects readable after commit.
- Tables are created in a **lifespan** function: code that runs once at startup (before `yield`) and once at shutdown (after). It replaces the older `@app.on_event("startup")`.

```python file=blog_demo.py
# blog_demo.py : a tiny async blog API (authors and posts)
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, selectinload
from sqlalchemy.pool import StaticPool

# In-memory SQLite: StaticPool keeps ONE connection, so every session sees the same database.
engine = create_async_engine(
    "sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    author: Mapped[Author] = relationship(back_populates="posts")

class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str

class AuthorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    posts: list[PostOut] = []

class AuthorIn(BaseModel):
    name: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:                    # startup
        await conn.run_sync(Base.metadata.create_all)
    yield                                                 # the app serves requests here
    await engine.dispose()                                # shutdown

app = FastAPI(lifespan=lifespan)

async def get_session():
    async with SessionLocal() as session:                 # opens, and closes on exit
        yield session

Session = Annotated[AsyncSession, Depends(get_session)]

@app.post("/authors", response_model=AuthorOut, status_code=201)
async def create_author(data: AuthorIn, session: Session):
    author = Author(name=data.name)
    session.add(author)
    await session.commit()                                # await every I/O step
    return AuthorOut(id=author.id, name=author.name)

@app.post("/authors/{author_id}/posts", response_model=PostOut, status_code=201)
async def create_post(author_id: int, title: str, session: Session):
    if await session.get(Author, author_id) is None:
        raise HTTPException(404, "Author not found")
    post = Post(title=title, author_id=author_id)
    session.add(post)
    await session.commit()
    return post

@app.get("/authors", response_model=list[AuthorOut])
async def list_authors(
    session: Session,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = select(Author).options(selectinload(Author.posts)).order_by(Author.id).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()

```

### 11.2 Using it

`TestClient` only runs the lifespan if you use it as a context manager (`with`). That is what creates the tables here.

```python run
from fastapi.testclient import TestClient
from blog_demo import app

with TestClient(app) as client:
    print(client.post("/authors", json={"name": "Asha"}).json())
    client.post("/authors", json={"name": "Ben"})
    for title in ("Intro", "Async", "Testing"):
        client.post("/authors/1/posts", params={"title": title})
    print(client.post("/authors/99/posts", params={"title": "x"}).json())
    print(client.get("/authors?limit=1").json())
    print(client.get("/authors?limit=1&offset=1").json())
```
```text
{'id': 1, 'name': 'Asha', 'posts': []}
{'detail': 'Author not found'}
[{'id': 1, 'name': 'Asha', 'posts': [{'id': 1, 'title': 'Intro'}, {'id': 2, 'title': 'Async'}, {'id': 3, 'title': 'Testing'}]}]
[{'id': 2, 'name': 'Ben', 'posts': []}]
```

What to notice:

- `selectinload(Author.posts)` loaded each page's posts with **one extra query** for all authors, instead of one query per author. That is the fix for N+1 from swe.03 section 10, and in async code it is also required (next sections).
- Pagination is `limit`/`offset`. For stable pages always add `order_by`.
- `session.get(Author, id)` is the primary-key lookup shortcut; it returns `None` when missing.

### 11.5 The `MissingGreenlet` trap

Lazy loading means "fetch the related rows the first time you touch the attribute". That happens *inside attribute access*, which is not an `await`, so async SQLAlchemy cannot do it and raises an error that confuses everyone the first time:

```python run
import asyncio
from sqlalchemy import select
from blog_demo import Author, Base, Post, SessionLocal, engine

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with SessionLocal() as s:
        s.add(Author(name="Asha", posts=[Post(title="t")]))
        await s.commit()
    async with SessionLocal() as s:
        author = (await s.execute(select(Author))).scalars().first()
        try:
            print(len(author.posts))                      # lazy load: not allowed
        except Exception as exc:
            print(type(exc).__name__)
            print(str(exc).splitlines()[0])

asyncio.run(main())
```
```text
StatementError
(sqlalchemy.exc.MissingGreenlet) greenlet_spawn has not been called; can't call await_() here. Was IO attempted in an unexpected place?

<sys>:0: RuntimeWarning: coroutine 'Connection.cursor' was never awaited
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
```

Two things in that output need explaining. First, the exception that reaches you is a `StatementError` that *wraps* `MissingGreenlet`; the first line of its message names the real cause. Second, the `RuntimeWarning: coroutine ... was never awaited` is a side effect of the same mistake: the driver tried to start I/O outside `await`, so a coroutine was created and thrown away. Seeing that warning next to a `MissingGreenlet` is normal; fix the first and the second disappears.

The fix is always the same: **load what you will touch, up front**: `selectinload(...)` (collections), `joinedload(...)` (single parents), or an explicit second query. The same error appears when a response model reads `author.posts` that was never loaded, because the Pydantic conversion touches the attribute. Rule of thumb: in async code, decide the loading strategy for every relationship in every query. Setting `lazy="raise"` on a relationship turns accidental lazy loads into an immediate, clear error in *both* sync and async code.

Other async rules:

- **Do not share one `AsyncSession` between concurrent tasks** (`asyncio.gather`). One session = one task.
- Use `async with SessionLocal() as session:` so the connection is released.
- `expire_on_commit=False` is what lets `return post` work after `await session.commit()`; with the default, the `post.id` read would try to refresh lazily and fail.

### 11.6 SQLModel: one class for table and schema

**SQLModel** is built by the author of FastAPI. A class is both a SQLAlchemy table and a Pydantic model. It reduces duplication for simple cases and has the same async story:

```python run
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})

class HeroBase(SQLModel):                       # shared fields: validation only, no table
    name: str = Field(index=True)
    power: int = Field(ge=0, le=100)

class Hero(HeroBase, table=True):               # table=True makes it a database table
    id: int | None = Field(default=None, primary_key=True)
    secret_name: str

class HeroCreate(HeroBase):                     # input: no id
    secret_name: str

class HeroPublic(HeroBase):                     # output: no secret_name
    id: int

@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

Session = Annotated[AsyncSession, Depends(get_session)]

@app.post("/heroes", response_model=HeroPublic, status_code=201)
async def create(data: HeroCreate, session: Session):
    hero = Hero.model_validate(data)
    session.add(hero)
    await session.commit()
    return hero

with TestClient(app) as c:
    print(c.post("/heroes", json={"name": "Spark", "power": 40, "secret_name": "Ria"}).json())
    c.post("/heroes", json={"name": "Titan", "power": 90, "secret_name": "Bo"})
    print(c.post("/heroes", json={"name": "Bad", "power": 500, "secret_name": "x"}).json()["detail"][0]["msg"])
```
```text
{'name': 'Spark', 'power': 40, 'id': 1}
Input should be less than or equal to 100
```

The `HeroBase / Hero / HeroCreate / HeroPublic` pattern is the SQLModel version of section 7.2's input/storage/output split. Use SQLModel when your API shape is close to your tables. Use plain SQLAlchemy + Pydantic (what the project in section 22 does) when you want full SQLAlchemy features, richer relationships, or a hard boundary between database and API models.

## 12. Authentication and authorisation

swe.04 sections 15-17 covered hashing, sessions and ownership with cookies. An API usually has no browser session; the client sends a **token** in the `Authorization` header on every request. Vocabulary: **authentication** answers "who are you?" (401 if unknown); **authorisation** answers "may you do this?" (403 if not).

```text
   POST /auth/login {email, password} --> verify hash --> create signed token --> {"access_token": ...}
   GET  /tasks   Authorization: Bearer <token> --> verify signature + expiry --> user --> endpoint
```

### 12.1 Password hashing with the standard library

Never store passwords; store a salted, slow hash (swe.04 section 15). The standard library provides `hashlib.scrypt` and `hashlib.pbkdf2_hmac`, so we need no new package:

```python file=security_demo.py
# security_demo.py
import base64, hashlib, hmac, os

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(digest).decode()

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_b64, digest_b64 = stored.split("$")
        salt, expected = base64.b64decode(salt_b64), base64.b64decode(digest_b64)
    except ValueError:
        return False
    actual = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return hmac.compare_digest(actual, expected)       # constant-time comparison
```

```python run
from security_demo import hash_password, verify_password

h = hash_password("correct horse")
print(h.split("$")[0], len(h) > 60)
print(verify_password("correct horse", h), verify_password("wrong", h), verify_password("x", "garbage"))
print(hash_password("same") != hash_password("same"))        # random salt: two hashes differ
```
```text
scrypt True
True False False
True
```

`hmac.compare_digest` compares in constant time, so an attacker cannot learn how many leading bytes matched from response timing. Hashing is CPU-heavy by design (about 50 ms); in an `async def` endpoint call it through `run_in_threadpool` (section 10.3) or use a plain `def` endpoint for login.

### 12.2 Tokens with JWT

A **JWT** (JSON Web Token) is three base64 parts: header, payload (claims) and a signature made with a secret key. The server stores nothing; it re-checks the signature on every request. We use PyJWT (`import jwt`). Rules:

- The secret must be **long and random** (at least 32 bytes for HS256). PyJWT warns about shorter keys.
- Always set `exp` (expiry). Claims are *readable by anyone* (only base64), so never put secrets in them.
- Put the user id in `sub`, as a **string** (PyJWT requires it).
- Always pass `algorithms=[...]` when decoding, so an attacker cannot choose `none`.

```python run
import time
import jwt

SECRET = "x" * 16 + "-demo-only-secret-key-at-least-32-bytes-long"       # in real life: from an environment variable
now = int(time.time())

token = jwt.encode({"sub": "42", "role": "member", "iat": now, "exp": now + 900}, SECRET, algorithm="HS256")
print(token.count("."), "dots: header.payload.signature")
print(jwt.decode(token, SECRET, algorithms=["HS256"])["sub"])

expired = jwt.encode({"sub": "42", "exp": now - 10}, SECRET, algorithm="HS256")
for label, bad in (("expired", expired), ("tampered", token[:-3] + "AAA"), ("wrong key", jwt.encode({"sub": "1"}, "y" * 40, algorithm="HS256"))):
    try:
        jwt.decode(bad, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        print(f"{label:10}", type(exc).__name__)
```
```text
2 dots: header.payload.signature
42
expired    ExpiredSignatureError
tampered   InvalidSignatureError
wrong key  InvalidSignatureError
```

### 12.3 `OAuth2PasswordBearer` and `get_current_user`

`OAuth2PasswordBearer` is a dependency that reads `Authorization: Bearer <token>` and returns the token string, or raises `401` with a `WWW-Authenticate` header when it is missing. Its `tokenUrl` tells the interactive docs where the login endpoint is. A second dependency turns the token into a user:

```python file=auth_demo.py
# auth_demo.py : a complete small auth flow (in-memory users)
import time
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from security_demo import hash_password, verify_password

SECRET = "demo-secret-" + "k" * 40            # real apps read this from the environment (section 18)
ALGORITHM = "HS256"

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

USERS = {
    "asha@example.com": {"id": 1, "email": "asha@example.com", "role": "admin", "hash": hash_password("asha-password")},
    "ben@example.com": {"id": 2, "email": "ben@example.com", "role": "member", "hash": hash_password("ben-password")},
}

class Login(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_token(user: dict, minutes: int = 15) -> str:
    now = int(time.time())
    return jwt.encode({"sub": str(user["id"]), "role": user["role"], "iat": now, "exp": now + minutes * 60}, SECRET, algorithm=ALGORITHM)

@app.post("/auth/login", response_model=Token)
def login(data: Login):
    user = USERS.get(data.email)
    # Same error for "no such user" and "wrong password": do not reveal which emails exist.
    if user is None or not verify_password(data.password, user["hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_token(user))

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    credentials_error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise credentials_error
    user = next((u for u in USERS.values() if str(u["id"]) == payload.get("sub")), None)
    if user is None:
        raise credentials_error
    return user

CurrentUser = Annotated[dict, Depends(get_current_user)]

def require_role(*roles: str):
    """A dependency FACTORY: returns a dependency that only lets certain roles in."""
    def checker(user: CurrentUser) -> dict:
        if user["role"] not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Requires role: {', '.join(roles)}")
        return user
    return checker

@app.get("/me")
def me(user: CurrentUser):
    return {"id": user["id"], "email": user["email"], "role": user["role"]}

@app.get("/admin/users")
def list_users(user: Annotated[dict, Depends(require_role("admin"))]):
    return [u["email"] for u in USERS.values()]
```

```python run
from fastapi.testclient import TestClient
from auth_demo import app

c = TestClient(app)

def login(email, password):
    r = c.post("/auth/login", json={"email": email, "password": password})
    return r, {"Authorization": "Bearer " + r.json().get("access_token", "")}

r, _ = login("asha@example.com", "wrong")
print(r.status_code, r.json(), r.headers["www-authenticate"])
_, asha = login("asha@example.com", "asha-password")
_, ben = login("ben@example.com", "ben-password")

print(c.get("/me").status_code, c.get("/me").json())                # no token
print(c.get("/me", headers=asha).json())
print(c.get("/me", headers={"Authorization": "Bearer junk"}).json())
print(c.get("/admin/users", headers=asha).json())
print(c.get("/admin/users", headers=ben).status_code, c.get("/admin/users", headers=ben).json())
```
```text
401 {'detail': 'Incorrect email or password'} Bearer
401 {'detail': 'Not authenticated'}
{'id': 1, 'email': 'asha@example.com', 'role': 'admin'}
{'detail': 'Invalid or expired token'}
['asha@example.com', 'ben@example.com']
403 {'detail': 'Requires role: admin'}
```

The codes tell the story: **401** when the caller is unknown or the token is bad; **403** when the caller is known but not allowed. `require_role("admin")` is a *dependency factory*: a function that builds a dependency. It is also a good place for team permissions, as the project shows.

> **Honest limitation.** The standard OAuth2 "password flow" sends `username` and `password` as a *form*, parsed by `OAuth2PasswordRequestForm`, which needs the `python-multipart` package (not installed here). We used a JSON login body instead. The API works the same for any client, but the **Authorize** button in `/docs` expects the form flow; to log in through `/docs` with this design, call `/auth/login` there and paste the token. With `python-multipart` installed you would replace `Login` by `Depends(OAuth2PasswordRequestForm)`.

### 12.4 Ownership checks

Roles are coarse; most rules are about *this* row. Put the check in a dependency that loads the row, raises `404` if absent and `403` if not allowed. Choose 403 or 404 for foreign rows deliberately: 403 says "exists, not yours", 404 hides that it exists. The project (section 22) uses 404.

### 12.5 Security checklist

Secrets from the environment, never in source control; short-lived access tokens; HTTPS always (swe.02 section 17); rate-limit `/auth/login`; the same message for unknown email and wrong password.


## 13. Middleware and CORS

### 13.1 What middleware is

**Middleware** is code that wraps *every* request: it runs before the request reaches the router and again after the response is built. Use it for things that are not about one endpoint: timing, request ids, logging, security headers, CORS.

```text
   client --> [ middleware A ] --> [ middleware B ] --> router --> endpoint
   client <-- [ middleware A ] <-- [ middleware B ] <-- router <-- endpoint
              (before: top to bottom)      (after: bottom to top)
```

The simplest form is a decorated function. `call_next(request)` runs the rest of the chain and gives you the response:

```python run
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI()

@app.middleware("http")
async def add_request_id_and_timing(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]
    request.state.request_id = request_id               # visible to endpoints
    start = time.perf_counter()
    response = await call_next(request)                 # <- everything else happens here
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response

@app.get("/ping")
def ping(request: Request):
    return {"request_id_seen_by_endpoint": request.state.request_id}

c = TestClient(app)
r = c.get("/ping", headers={"X-Request-ID": "abc123"})
print(r.json(), r.headers["x-request-id"], "x-process-time-ms" in r.headers)
r = c.get("/ping")
print(len(r.headers["x-request-id"]))          # generated ids: random, only the length is stable
```
```text
{'request_id_seen_by_endpoint': 'abc123'} abc123 True
8
```

The timing value itself is machine-specific, so we print only that it exists. Middleware added **last** is the **outermost** (it sees the request first). Order matters, for example CORS should sit outside authentication so that even error responses carry CORS headers.

### 13.2 CORS

**CORS** (Cross-Origin Resource Sharing, swe.04 section 20) is a browser rule: JavaScript from `https://app.example.com` may not read responses from `https://api.example.com` unless the API sends `Access-Control-Allow-Origin` for that origin. The server is not protected by it (curl ignores it); it protects the *user's browser*. FastAPI ships a middleware:

```python run
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],     # an explicit list; avoid "*" in real apps
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
    max_age=600,
)

@app.get("/data")
def data(): return {"ok": True}

c = TestClient(app)
# Simple request from an allowed origin
r = c.get("/data", headers={"Origin": "https://app.example.com"})
print("allowed :", r.headers.get("access-control-allow-origin"))
# Preflight: the browser asks permission first with OPTIONS
r = c.options("/data", headers={
    "Origin": "https://app.example.com",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "authorization",
})
print("preflight:", r.status_code, r.headers["access-control-allow-methods"], "|", r.headers["access-control-max-age"])
```
```text
allowed : https://app.example.com
preflight: 200 GET, POST | 600
```

Remember:

- A browser sends a **preflight** `OPTIONS` request before "non-simple" requests (JSON `Content-Type`, an `Authorization` header). The middleware answers it for you.
- `allow_origins=["*"]` cannot be combined with `allow_credentials=True` in a useful way (browsers refuse). List real origins.
- CORS errors appear in the **browser console**, not as a server error. The server log shows a normal 200.

## 14. Background tasks

Sometimes the client should not wait: sending a welcome email, writing an audit row, resizing an image. `BackgroundTasks` runs a function **after the response has been sent**:

```python run
from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
events = []

def send_welcome(email: str):
    events.append(f"email sent to {email}")           # imagine a slow SMTP call

@app.post("/signup", status_code=201)
def signup(email: str, background: BackgroundTasks):
    events.append("user saved")
    background.add_task(send_welcome, email)          # scheduled, not run yet
    events.append("returning response")
    return {"email": email}

r = TestClient(app).post("/signup", params={"email": "a@b.co"})
print(r.status_code, events)
```
```text
201 ['user saved', 'returning response', 'email sent to a@b.co']
```

The order shows the task ran after the endpoint returned. (The test client waits for background tasks before handing you the response, so you can assert on their effects. A real client receives its response first.)

Limits to respect:

- Background tasks live **inside the server process**. If the process restarts, queued tasks are lost, and there are no retries.
- Failures are invisible to the client (the response is already sent). Log inside the task.
- For anything important, slow or heavy (reports, video, payments) use a real job queue (Celery, RQ, arq) so work survives restarts and can be retried.

## 15. WebSockets

### 15.1 Why WebSockets

HTTP is request-response: the client asks, the server answers. For *real-time updates* (a teammate moved a task and everyone sees it now) the server must push without being asked. Polling ("any news?" every second) wastes requests. A **WebSocket** starts as an HTTP request, then upgrades the same TCP connection (swe.02 section 5) into a persistent two-way channel carrying **messages** in either direction.

```text
   Client                                  Server
     | -- GET /ws  Upgrade: websocket --->  |
     | <-- 101 Switching Protocols -------  |    (handshake: this is the last HTTP)
     | == message ==========================>|    receive_text / receive_json
     | <========================= message == |    send_text / send_json
     | ... connection stays open ...        |
     | -- close -------------------------->  |    WebSocketDisconnect raised on the server
```

### 15.2 An echo endpoint

```python run
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

app = FastAPI()

@app.websocket("/ws/echo")
async def echo(websocket: WebSocket):
    await websocket.accept()                          # complete the handshake
    try:
        while True:
            text = await websocket.receive_text()     # raises WebSocketDisconnect when the client leaves
            await websocket.send_text(f"echo: {text}")
    except WebSocketDisconnect:
        pass                                          # always handle it, or your cleanup code never runs

client = TestClient(app)
with client.websocket_connect("/ws/echo") as ws:
    ws.send_text("hello")
    print(ws.receive_text())
    ws.send_text("again")
    print(ws.receive_text())
```
```text
echo: hello
echo: again
```

A WebSocket endpoint is a function with a `WebSocket` parameter, and it usually contains a loop. Dependencies, path and query parameters work as in HTTP routes (`Depends`, `Query`). The browser side would be `new WebSocket("ws://localhost:8000/ws/echo")`.

### 15.3 A connection manager: broadcasting to a room

One connection is not enough: when user A changes a task, users B and C on the same team must hear about it. The server keeps a **registry** of live connections per room (here, per team) and loops over them to send. This small class is the whole trick:

```text
        user A  --\                                   /--> user A's socket
        user B  ---+--> ConnectionManager["team-7"] --+---> user B's socket     (broadcast)
        user C  --/                                   \--> user C's socket
        user D (team-9) is in a different room and hears nothing
```

```python file=realtime_demo.py
# realtime_demo.py
from collections import defaultdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, room: str, websocket: WebSocket):
        await websocket.accept()
        self.rooms[room].append(websocket)

    def disconnect(self, room: str, websocket: WebSocket):
        self.rooms[room].remove(websocket)
        if not self.rooms[room]:
            del self.rooms[room]                      # do not leak empty rooms

    async def broadcast(self, room: str, message: dict):
        for connection in list(self.rooms.get(room, [])):      # copy: the list may change while we send
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(room, connection)              # dead socket: drop it

manager = ConnectionManager()
app = FastAPI()

@app.websocket("/ws/rooms/{room}")
async def room_socket(websocket: WebSocket, room: str, user: str):
    await manager.connect(room, websocket)
    await manager.broadcast(room, {"event": "joined", "user": user})
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(room, {"event": "message", "user": user, "data": data})
    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
        await manager.broadcast(room, {"event": "left", "user": user})

@app.post("/rooms/{room}/announce")
async def announce(room: str, text: str):
    """An ordinary HTTP endpoint that pushes to WebSocket clients."""
    await manager.broadcast(room, {"event": "announcement", "text": text})
    return {"delivered_to": len(manager.rooms.get(room, []))}
```

```python run
from fastapi.testclient import TestClient
from realtime_demo import app, manager

client = TestClient(app)
with client.websocket_connect("/ws/rooms/team-7?user=asha") as asha:
    print("asha sees:", asha.receive_json())
    with client.websocket_connect("/ws/rooms/team-7?user=ben") as ben:
        print("asha sees:", asha.receive_json())              # ben joined
        print("ben sees :", ben.receive_json())               # his own join
        with client.websocket_connect("/ws/rooms/team-9?user=dina") as dina:
            print("dina sees:", dina.receive_json())
            ben.send_json({"task": 5, "status": "done"})
            print("asha sees:", asha.receive_json())
            print("ben sees :", ben.receive_json())
            print(client.post("/rooms/team-7/announce", params={"text": "standup"}).json())
            print("asha sees:", asha.receive_json())
    print("asha sees:", asha.receive_json())                  # ben left
print("rooms left:", dict(manager.rooms))
```
```text
asha sees: {'event': 'joined', 'user': 'asha'}
asha sees: {'event': 'joined', 'user': 'ben'}
ben sees : {'event': 'joined', 'user': 'ben'}
dina sees: {'event': 'joined', 'user': 'dina'}
asha sees: {'event': 'message', 'user': 'ben', 'data': {'task': 5, 'status': 'done'}}
ben sees : {'event': 'message', 'user': 'ben', 'data': {'task': 5, 'status': 'done'}}
{'delivered_to': 2}
asha sees: {'event': 'announcement', 'text': 'standup'}
asha sees: {'event': 'left', 'user': 'ben'}
rooms left: {}
```

Dina was in another room, so she heard nothing. Notice the HTTP endpoint `announce` pushing to sockets: this is how a normal `POST /tasks/5/done` triggers a real-time update (the project does exactly that).

### 15.4 WebSocket authentication and limits

Browsers cannot set an `Authorization` header on `new WebSocket(...)`, so a token usually travels in the query string (`?token=...`) and you validate it **before** `accept()`; to reject, call `await websocket.close(code=1008)` (policy violation) and return. The project in section 22 does this. Also think about: tokens in URLs end up in logs (use short-lived tickets); a manager held in a Python variable works for **one process only**, so with several workers you need a shared broker (Redis pub/sub); send pings so dead connections are noticed; limit message size.

## 16. File uploads and raw bodies

Browser file uploads use `multipart/form-data`. FastAPI parses it with `File()`, `UploadFile` and `Form()`, which all need the separate package **python-multipart**. It is not installed here, and FastAPI tells you at the moment the route is defined. (It prints the message itself to stderr as well, which is why the text appears twice below.)

```python run error
from fastapi import FastAPI, UploadFile

app = FastAPI()

try:
    @app.post("/upload")
    async def upload(file: UploadFile):
        return {"name": file.filename}
except RuntimeError as exc:
    print(type(exc).__name__, "->", str(exc).splitlines()[0])
```
```text
RuntimeError -> Form data requires "python-multipart" to be installed.

Form data requires "python-multipart" to be installed.
You can install "python-multipart" with:

pip install python-multipart
```

> **Try it on your machine** (after `pip install python-multipart`): declare `async def upload(file: UploadFile)`, read it with `data = await file.read()` (in chunks for big files), and test with `client.post("/upload", files={"file": ("a.txt", b"hello", "text/plain")})`; `file.filename` and `file.content_type` come with it.

For API clients, raw binary uploads need no extra package: the client sends the bytes as the body with `Content-Type: application/octet-stream`. Read them from the request, **and enforce a size limit yourself**, because an unbounded upload can exhaust memory:

```python run
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

app = FastAPI()
MAX_BYTES = 1000

@app.put("/files/{name}")
async def put_file(name: str, request: Request):
    size = 0
    async for chunk in request.stream():                 # read piece by piece
        size += len(chunk)
        if size > MAX_BYTES:
            raise HTTPException(413, f"File larger than {MAX_BYTES} bytes")
    return {"name": name, "bytes": size}

c = TestClient(app)
print(c.put("/files/a.bin", content=b"x" * 500).json())
r = c.put("/files/b.bin", content=b"x" * 5000)
print(r.status_code, r.json())
```
```text
{'name': 'a.bin', 'bytes': 500}
413 {'detail': 'File larger than 1000 bytes'}
```

Also validate the file *type* by content (magic bytes), not by the client-supplied name or `Content-Type`, and never use the client's filename as a path on disk (path traversal, `../../etc/passwd`).

## 17. Routers and project structure

### 17.1 `APIRouter`

One file with 40 endpoints becomes unmanageable. An `APIRouter` is a mini-app that collects routes; you plug it into the main app with a prefix, tags and shared dependencies. It is the FastAPI equivalent of Flask's blueprints (swe.04 section 13):

```python run
from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

def require_key(x_key: Annotated[str | None, Header()] = None):
    if x_key != "k":
        raise HTTPException(401, "Missing key")

users = APIRouter(prefix="/users", tags=["users"])
tasks = APIRouter(prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_key)])

@users.get("/")
def list_users(): return ["asha", "ben"]

@tasks.get("/{task_id}")
def get_task(task_id: int): return {"id": task_id}

app = FastAPI()
app.include_router(users)
app.include_router(tasks, prefix="/api/v1")                 # prefixes add up: /api/v1/tasks/...

c = TestClient(app)
print(c.get("/users/").json(), c.get("/api/v1/tasks/3").status_code, c.get("/api/v1/tasks/3", headers={"X-Key": "k"}).json())
print(sorted(p for p in c.get("/openapi.json").json()["paths"]))
```
```text
['asha', 'ben'] 401 {'id': 3}
['/api/v1/tasks/{task_id}', '/users/']
```

### 17.2 A layout that scales

A structure used by most larger FastAPI projects (the project in section 22 follows it):

The layout used by most larger FastAPI projects (the final tree of section 22 follows it): `app/main.py` (app factory, wiring), `config.py`, `database.py`, `models.py` (tables), `schemas.py` (API shapes), `security.py`, `deps.py` (`Depends` functions), `routers/` (one module per resource), optionally `services/` (business rules), and `tests/` with a `conftest.py`.

Layer rules (same spirit as the layered design from earlier chapters):

- **Routers** translate HTTP to function calls and back: parse, call, return. No SQL there beyond trivial lookups.
- **Services** hold business rules and take a session; they raise domain exceptions, never `HTTPException`.
- **Models** are tables, **schemas** are API shapes; keep them apart (section 7.2).
- **Dependencies** (`deps.py`) are the only place that reaches into the request (headers, tokens).
- `main.py` is wiring only. Imports flow downward: routers import services, schemas, deps; nothing imports routers.

> **Trap: circular imports.** `deps.py` imports `models.py`; if `models.py` imports `deps.py` you get an `ImportError` at startup. Keep the arrows one-way, and import the *app* nowhere except `main.py` and tests.

## 18. Settings from the environment

Configuration (database URL, secret key, token lifetime) must come from the **environment**, not from source code (twelve-factor style, swe.04 section 12). The popular tool is the `pydantic-settings` package; it is **not installed here**, so we do it by hand with a Pydantic model that reads `os.environ`. This also shows how little magic it is:

```python run
import os
from functools import lru_cache
from pydantic import BaseModel, Field, ValidationError

class Settings(BaseModel):
    model_config = {"frozen": True}
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    secret_key: str = Field(min_length=32)                  # no default: a missing secret must fail loudly
    access_token_minutes: int = Field(default=15, ge=1, le=1440)
    debug: bool = False

    @classmethod
    def from_env(cls, environ=os.environ) -> "Settings":
        mapping = {"database_url": "APP_DATABASE_URL", "secret_key": "APP_SECRET_KEY",
                   "access_token_minutes": "APP_ACCESS_TOKEN_MINUTES", "debug": "APP_DEBUG"}
        values = {field: environ[env] for field, env in mapping.items() if env in environ}
        return cls.model_validate(values)                   # env values are strings: Pydantic converts them

@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()

env = {"APP_SECRET_KEY": "s" * 40, "APP_ACCESS_TOKEN_MINUTES": "30", "APP_DEBUG": "true"}
print(Settings.from_env(env))
try:
    Settings.from_env({})
except ValidationError as exc:
    print("startup would fail:", exc.errors()[0]["loc"], exc.errors()[0]["msg"])
```
```text
database_url='sqlite+aiosqlite:///./dev.db' secret_key='ssssssssssssssssssssssssssssssssssssssss' access_token_minutes=30 debug=True
startup would fail: ('secret_key',) Field required
```

Why this design:

- Environment variables are always strings; the model converts `"30"` to `30` and `"true"` to `True`, and **rejects** nonsense at startup, not at 3 a.m. on the first request.
- The secret has **no default**: a forgotten variable stops the app instead of running with a known key.
- `from_env(environ)` takes the mapping as a parameter, so tests pass a plain dict and never touch the real environment.
- `lru_cache` makes `get_settings()` build the object once; it is used as a dependency so tests can override it (`app.dependency_overrides[get_settings] = lambda: test_settings`).

For local development put variables in a `.env` file loaded by your shell or tool, git-ignored, with a committed `.env.example` listing the names with empty values (the same convention as this course's `config.example.toml`).

## 19. OpenAPI and the interactive docs

### 19.1 What gets generated

From your routes and hints FastAPI builds an **OpenAPI** document (a JSON description of your API) at `/openapi.json`, and serves two viewers from it: **Swagger UI** at `/docs` and **ReDoc** at `/redoc`. Any other tool (client generators, API gateways, contract tests) can read the same JSON.

```python file=docs_demo.py
# docs_demo.py
from typing import Annotated
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Task API", version="1.0.0", description="Demo of generated documentation.")

class TaskIn(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [{"title": "Write chapter", "priority": 2}]})
    title: str = Field(min_length=3, description="Short summary shown in lists")
    priority: int = Field(default=3, ge=1, le=5)

class TaskOut(TaskIn):
    id: int

@app.post("/tasks", response_model=TaskOut, status_code=201, tags=["tasks"],
          summary="Create a task", responses={409: {"description": "Duplicate title"}})
def create_task(task: TaskIn):
    """Create a task for the current user.

    The docstring becomes the long description in the docs."""
    return {"id": 1, **task.model_dump()}

@app.get("/tasks/{task_id}", response_model=TaskOut, tags=["tasks"])
def get_task(task_id: Annotated[int, Path(ge=1, description="Task id")],
             verbose: Annotated[bool, Query(description="Include extras")] = False):
    return {"id": task_id, "title": "x" * 3}
```

```python run
import json
from fastapi.testclient import TestClient
from docs_demo import app

spec = TestClient(app).get("/openapi.json").json()
print(spec["openapi"], spec["info"]["title"], spec["info"]["version"])
print(sorted(spec["paths"]))
post = spec["paths"]["/tasks"]["post"]
print(post["tags"], post["summary"], post["requestBody"]["content"]["application/json"]["schema"])
props = spec["components"]["schemas"]["TaskIn"]["properties"]
print(props["title"])
print(props["priority"])
print([p["name"] + ":" + p["in"] for p in spec["paths"]["/tasks/{task_id}"]["get"]["parameters"]])
print(sorted(post["responses"]))
```
```text
3.1.0 Task API 1.0.0
['/tasks', '/tasks/{task_id}']
['tasks'] Create a task {'$ref': '#/components/schemas/TaskIn'}
{'type': 'string', 'minLength': 3, 'title': 'Title', 'description': 'Short summary shown in lists'}
{'type': 'integer', 'maximum': 5.0, 'minimum': 1.0, 'title': 'Priority', 'default': 3}
['task_id:path', 'verbose:query']
['201', '409', '422']
```

Everything you wrote appears in the JSON: the constraints became `minLength`/`minimum`/`maximum`, the docstring is the `description`, the example is shown in the schema, and the validation error shape (`422`) was added to the responses automatically. The spec is not a hand-maintained document that drifts from the code; it is *derived* from it, so it is always accurate.

### 19.2 `/docs` and `/redoc`

```python run
from fastapi.testclient import TestClient
from docs_demo import app

c = TestClient(app)
for path in ("/docs", "/redoc", "/openapi.json"):
    r = c.get(path)
    print(path, r.status_code, r.headers["content-type"].split(";")[0])
print("swagger page loads its JavaScript from:", [w for w in c.get("/docs").text.split('"') if w.startswith("https://") and w.endswith(".js")][0])
```
```text
/docs 200 text/html
/redoc 200 text/html
/openapi.json 200 application/json
swagger page loads its JavaScript from: https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js
```

> **Honest note about offline use.** The server returns the HTML page fine, but that page asks the **browser** to download the Swagger UI JavaScript and CSS from a public CDN (the URL above). With no internet, `/docs` opens as a blank page, while `/openapi.json` still works. The fixes are to vendor the assets and serve them yourself (`get_swagger_ui_html` accepts your own URLs) or simply use `/openapi.json`, or the tests, offline.
>
> **Try it on your machine** (needs `uvicorn` and internet): run the server, open `http://127.0.0.1:8000/docs`, expand `POST /tasks`, press **Try it out**, edit the example body, **Execute**, and read the response code, headers and body. Send `{"title": "x"}` to see your 422 rendered.

### 19.3 Controlling the docs

- `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` hides them (common for internal-only or production). 
- `tags=["tasks"]` groups endpoints; `summary` and docstrings document them; `Field(description=..., examples=[...])` and `json_schema_extra` document models; `responses={404: {...}}` documents extra statuses; `deprecated=True` marks old endpoints.
- `include_in_schema=False` hides a single route.
- Because the spec is data, you can generate a typed client for TypeScript, Kotlin or Python from it with external tools.



## 20. Testing FastAPI apps

swe.04 section 21 taught the Flask test client and pytest fixtures; the ideas carry over unchanged. FastAPI adds three helpers: `TestClient` (sync, in-process), `dependency_overrides` (section 9.6) and, for `async def` tests, an async client over `ASGITransport`.

### 20.1 Fixtures, overrides, parametrised validation tests

We test the auth demo from section 12. The `client` fixture builds a fresh client per test, and the override test replaces the whole login machinery with a fixed user, which is how you test endpoints *without* logging in:

```python file=conftest.py
# conftest.py
import pytest
from fastapi.testclient import TestClient

from auth_demo import app

@pytest.fixture
def client():
    with TestClient(app) as c:                   # "with" also runs startup/shutdown (lifespan)
        yield c
    app.dependency_overrides.clear()             # never leak an override into the next test

@pytest.fixture
def auth(client):
    def _login(email, password):
        r = client.post("/auth/login", json={"email": email, "password": password})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
    return _login

@pytest.fixture
def anyio_backend():
    return "asyncio"                             # the async tests below run on asyncio only
```

```python file=test_auth_demo.py
# test_auth_demo.py
import httpx
import pytest

from auth_demo import app, get_current_user

def test_me_requires_a_token(client):
    r = client.get("/me")
    assert r.status_code == 401, "no Authorization header should be 401, not 403 or 422"
    assert r.headers["www-authenticate"] == "Bearer"

def test_member_cannot_use_admin_route(client, auth):
    r = client.get("/admin/users", headers=auth("ben@example.com", "ben-password"))
    assert r.status_code == 403, "authenticated but not allowed is 403, not 401"

def test_override_skips_login(client):
    app.dependency_overrides[get_current_user] = lambda: {"id": 9, "email": "fake@x.io", "role": "member"}
    assert client.get("/me").json()["email"] == "fake@x.io"       # no token needed

@pytest.mark.anyio
async def test_async_client(anyio_backend):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/auth/login", json={"email": "ben@example.com", "password": "nope"})
    assert r.status_code == 401
```

```bash run
python -m pytest -v -p no:cacheprovider test_auth_demo.py 2>&1 | grep -E "PASSED|FAILED|passed|failed|warning"
```
```text
test_auth_demo.py::test_me_requires_a_token PASSED                                           [ 25%]
test_auth_demo.py::test_member_cannot_use_admin_route PASSED                                 [ 50%]
test_auth_demo.py::test_override_skips_login PASSED                                          [ 75%]
test_auth_demo.py::test_async_client PASSED                                                  [100%]
======================================== 4 passed =========================================
```

Notes:

- Every assert carries a message naming the likely mistake, as in this course's own tests.
- `@pytest.mark.parametrize` runs one test body for many bad inputs: the cheapest way to cover validation rules.
- **Async tests.** `pytest-asyncio` is not installed here, but `anyio` (which FastAPI already depends on) ships a pytest plugin: mark the test `@pytest.mark.anyio` and provide the `anyio_backend` fixture, as above. Without that fixture the plugin also tries the `trio` backend, which is not installed, and the test errors. Prefer the plain `TestClient` unless a test genuinely needs to `await` something (an async database check, concurrent requests).
- `TestClient` runs your async endpoints on its own event loop in a helper thread. If your lifespan creates a database engine (section 11), build the engine *inside* the lifespan and not at import time, so each test starts from a clean state.
- Test the **contract**: status codes, error shapes, which fields are present *and absent* (`assert "password_hash" not in body`).

### 20.2 A test database

Use **in-memory SQLite** with `StaticPool` (section 11) for fast, isolated tests, as the project does; a temp file (`tmp_path`) when you need several connections; and a few integration tests against the real engine (PostgreSQL in a container), because SQLite is more permissive about types and locking (swe.03 section 18).

## 21. Running for real

Everything so far ran in-process. A deployed app needs an ASGI server process. This section is a tutorial only; nothing here was run in this chapter, because `uvicorn` is not installed.

> **Try it on your machine**
>
> ```bash
> pip install uvicorn
> uvicorn app.main:app --reload --port 8000            # development: auto-reload on save
> uvicorn app.main:create_app --factory --port 8000    # when you have an app factory
> ```
>
> Expected: a log line about the server running on `http://127.0.0.1:8000`, then one access-log line per request (`"GET /health HTTP/1.1" 200 OK`). Process ids and timings in the log are machine-specific.

Production notes:

- **Workers.** One uvicorn process uses one CPU core for Python code. Run several: `uvicorn app.main:app --workers 4`, or Gunicorn managing uvicorn workers (`gunicorn -k uvicorn.workers.UvicornWorker -w 4 app.main:app`; the worker class is in the `uvicorn-worker` package in recent versions). Each worker has its **own memory**, so in-process state (our WebSocket manager, caches) is not shared: this is the same limit as in section 15.
- **Reverse proxy.** Put nginx, Caddy or a cloud load balancer in front for TLS, buffering and static files; start uvicorn with `--proxy-headers` so client addresses are correct.
- **Never** use `--reload` in production, and do not bind `0.0.0.0` on a development laptop on public Wi-Fi.
- **Health endpoint.** Add `GET /health` returning `{"status": "ok"}` (optionally checking the database) for load balancers.
- **Docs.** Consider `docs_url=None` for public production APIs.
- Logging, graceful shutdown and migrations (Alembic, swe.03 section 13) work as in the Flask chapter; `create_all` in the lifespan is for development and tests only.


## 22. Project: a task-management API, step by step

We build **TaskFlow**: users register and log in; users create **teams**; the team owner adds members; members create, assign, update and delete **tasks** inside their team; everyone connected to a team receives **real-time updates** over a WebSocket. It uses everything above: Pydantic schemas, async SQLAlchemy, dependency injection, JWT, routers, WebSockets, tests.

The rules (the "business spec" tests will enforce):

- Passwords are hashed; hashes never appear in a response.
- A team is visible only to its members. Everyone else gets `404`, as if it did not exist.
- Only the team **owner** adds members (`403` for a plain member).
- A task belongs to exactly one team; its id must be looked up **inside the team in the URL** (otherwise a user could edit another team's task by guessing ids).
- Members edit tasks; only the team owner or the task's creator deletes one (`403` otherwise).
- Every create, update and delete is broadcast to the team's WebSocket room.

### Step 1: settings and database

`app/config.py` follows section 18: a frozen `Settings` dataclass with `from_env()`, which raises at startup if `APP_SECRET_KEY` is missing or shorter than 32 characters. `app/database.py` has `make_engine(url)` (a shared single connection for in-memory SQLite, as in section 11) and the session dependency. The session factory lives on `app.state`, so each test app gets its own database:

```python
async def get_session(request: Request):
    async with request.app.state.sessionmaker() as session:
        yield session

Session = Annotated[AsyncSession, Depends(get_session)]
```



### Step 2: models (tables)

Four tables. `Membership` is the join table between users and teams and carries the **role**.

```python file=taskapp/app/models.py
# app/models.py
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    password_hash: Mapped[str]

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "team_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    role: Mapped[str] = mapped_column(default="member")          # "owner" or "member"

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    status: Mapped[str] = mapped_column(default="todo")
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
```

### Step 3: schemas (the API shapes)

Separate input and output models (section 7.2). `UserOut` has no hash. `TaskPatch` uses `None` defaults so `exclude_unset` can tell "not sent" from "sent".

```python file=taskapp/app/schemas.py
# app/schemas.py
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

class Status(str, Enum):
    todo = "todo"
    doing = "doing"
    done = "done"

class UserCreate(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    name: str = Field(min_length=1, max_length=60)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def lower_email(cls, v: str) -> str:
        return v.lower()

class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)           # read attributes of ORM objects

class UserOut(Out):
    id: int
    email: str
    name: str

class LoginIn(BaseModel):
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)

class TeamOut(Out):
    id: int
    name: str

class MemberAdd(BaseModel):
    email: str

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    assignee_id: int | None = None

class TaskPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=120)
    status: Status | None = None
    assignee_id: int | None = None

class TaskOut(Out):
    id: int
    title: str
    status: Status
    team_id: int
    creator_id: int
    assignee_id: int | None

class TaskPage(BaseModel):
    items: list[TaskOut]
    total: int
```

### Step 4: security and dependencies

`security.py` is section 12's `hash_password` and `verify_password` unchanged (scrypt, random salt, constant-time compare), plus two token functions that now take the settings instead of a global secret:

```python
def create_token(user_id: int, settings: Settings) -> str:
    now = int(time.time())
    claims = {"sub": str(user_id), "iat": now, "exp": now + settings.token_minutes * 60}
    return jwt.encode(claims, settings.secret_key, algorithm="HS256")

def decode_token(token: str, settings: Settings) -> int | None:     # None for expired, tampered or malformed
    try:
        return int(jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
```

`deps.py` is the heart of authorisation: **small dependencies that stack** (`current_user`, then `team_member`, then `team_owner`).


```python file=taskapp/app/deps.py
# app/deps.py
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.database import Session
from app.models import Membership, User
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_settings(request: Request) -> Settings:
    return request.app.state.settings

async def user_from_token(token: str, session: AsyncSession, settings: Settings) -> User | None:
    """Shared by HTTP and WebSocket code: token -> user or None."""
    user_id = decode_token(token, settings)
    return await session.get(User, user_id) if user_id is not None else None

async def current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: Session, settings: Annotated[Settings, Depends(get_settings)]
) -> User:
    user = await user_from_token(token, session, settings)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"})
    return user

CurrentUser = Annotated[User, Depends(current_user)]

async def find_membership(session: AsyncSession, user_id: int, team_id: int) -> Membership | None:
    stmt = select(Membership).where(Membership.user_id == user_id, Membership.team_id == team_id)
    return await session.scalar(stmt)

async def team_member(team_id: int, user: CurrentUser, session: Session) -> Membership:
    membership = await find_membership(session, user.id, team_id)
    if membership is None:
        raise HTTPException(404, "Team not found")           # 404, not 403: do not reveal that it exists
    return membership

Member = Annotated[Membership, Depends(team_member)]

async def team_owner(membership: Member) -> Membership:
    if membership.role != "owner":
        raise HTTPException(403, "Only the team owner can do this")
    return membership

Owner = Annotated[Membership, Depends(team_owner)]
```

Read the stack: `team_owner` needs `team_member`, which needs `current_user`, which needs the token and a session. An endpoint that declares `Owner` gets all those checks, in order, from one word.

### Step 5: real-time manager and routers

`app/realtime.py` holds the `ConnectionManager` of section 15.3 unchanged, a `get_manager(request)` dependency that returns `request.app.state.manager`, and `team_room(team_id)` which builds names like `team-3`. The routers hold only HTTP logic.


```python file=taskapp/app/routers/auth.py
# app/routers/auth.py
from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from app.database import Session
from app.deps import Settings, get_settings
from app.models import User
from app.schemas import LoginIn, TokenOut, UserCreate, UserOut
from app.security import create_token, hash_password, verify_password
from fastapi import Depends
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserCreate, session: Session):
    if await session.scalar(select(User).where(User.email == data.email)):
        raise HTTPException(409, "Email already registered")
    hashed = await run_in_threadpool(hash_password, data.password)       # CPU-heavy: keep off the loop
    user = User(email=data.email, name=data.name, password_hash=hashed)
    session.add(user)
    await session.commit()
    return user                                                           # UserOut drops the hash

@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, session: Session, settings: Annotated[Settings, Depends(get_settings)]):
    user = await session.scalar(select(User).where(User.email == data.email.lower()))
    ok = user is not None and await run_in_threadpool(verify_password, data.password, user.password_hash)
    if not ok:
        raise HTTPException(401, "Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    return TokenOut(access_token=create_token(user.id, settings))
```

```python file=taskapp/app/routers/teams.py
# app/routers/teams.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.database import Session
from app.deps import CurrentUser, Owner
from app.models import Membership, Team, User
from app.schemas import MemberAdd, TeamCreate, TeamOut, UserOut

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("", response_model=TeamOut, status_code=201)
async def create_team(data: TeamCreate, user: CurrentUser, session: Session):
    team = Team(name=data.name)
    session.add(team)
    await session.flush()                                        # assigns team.id without committing yet
    session.add(Membership(user_id=user.id, team_id=team.id, role="owner"))
    await session.commit()                                       # team + owner row: one transaction
    return team

@router.get("", response_model=list[TeamOut])
async def my_teams(user: CurrentUser, session: Session):
    stmt = select(Team).join(Membership).where(Membership.user_id == user.id).order_by(Team.id)
    return (await session.scalars(stmt)).all()

@router.post("/{team_id}/members", response_model=UserOut, status_code=201)
async def add_member(team_id: int, data: MemberAdd, owner: Owner, session: Session):
    new_user = await session.scalar(select(User).where(User.email == data.email.lower()))
    if new_user is None:
        raise HTTPException(404, "No user with that email")
    if await session.scalar(select(Membership).where(Membership.user_id == new_user.id, Membership.team_id == team_id)):
        raise HTTPException(409, "Already a member")
    session.add(Membership(user_id=new_user.id, team_id=team_id))
    await session.commit()
    return new_user
```

```python file=taskapp/app/routers/tasks.py
# app/routers/tasks.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select

from app.database import Session
from app.deps import CurrentUser, Member, find_membership
from app.models import Task
from app.realtime import ConnectionManager, get_manager, team_room
from app.schemas import Status, TaskCreate, TaskOut, TaskPage, TaskPatch

router = APIRouter(prefix="/teams/{team_id}/tasks", tags=["tasks"])
Manager = Annotated[ConnectionManager, Depends(get_manager)]

async def load_task(session, team_id: int, task_id: int) -> Task:
    """Look the task up INSIDE the team from the URL: a task id from another team is a 404."""
    task = await session.scalar(select(Task).where(Task.id == task_id, Task.team_id == team_id))
    if task is None:
        raise HTTPException(404, "Task not found")
    return task

async def check_assignee(session, team_id: int, assignee_id: int | None):
    if assignee_id is not None and await find_membership(session, assignee_id, team_id) is None:
        raise HTTPException(422, "assignee_id must belong to a member of this team")

@router.post("", response_model=TaskOut, status_code=201)
async def create_task(team_id: int, data: TaskCreate, member: Member, user: CurrentUser, session: Session, manager: Manager):
    await check_assignee(session, team_id, data.assignee_id)
    task = Task(title=data.title, team_id=team_id, creator_id=user.id, assignee_id=data.assignee_id)
    session.add(task)
    await session.commit()
    out = TaskOut.model_validate(task)
    await manager.broadcast(team_room(team_id), {"event": "task.created", "task": out.model_dump(mode="json")})
    return out

@router.get("", response_model=TaskPage)
async def list_tasks(
    team_id: int, member: Member, session: Session,
    status: Status | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    where = [Task.team_id == team_id] + ([Task.status == status.value] if status else [])
    total = await session.scalar(select(func.count()).select_from(Task).where(*where))
    rows = await session.scalars(select(Task).where(*where).order_by(Task.id).limit(limit).offset(offset))
    return {"items": rows.all(), "total": total}

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(team_id: int, task_id: int, data: TaskPatch, member: Member, session: Session, manager: Manager):
    task = await load_task(session, team_id, task_id)
    changes = data.model_dump(exclude_unset=True)                # only what the client sent
    if "assignee_id" in changes:
        await check_assignee(session, team_id, changes["assignee_id"])
    for field, value in changes.items():
        setattr(task, field, value.value if isinstance(value, Status) else value)
    await session.commit()
    out = TaskOut.model_validate(task)
    await manager.broadcast(team_room(team_id), {"event": "task.updated", "task": out.model_dump(mode="json")})
    return out

@router.delete("/{task_id}", status_code=204)
async def delete_task(team_id: int, task_id: int, member: Member, user: CurrentUser, session: Session, manager: Manager):
    task = await load_task(session, team_id, task_id)
    if member.role != "owner" and task.creator_id != user.id:
        raise HTTPException(403, "Only the team owner or the task's creator can delete it")
    await session.delete(task)
    await session.commit()
    await manager.broadcast(team_room(team_id), {"event": "task.deleted", "task_id": task_id})
    return Response(status_code=204)
```

### Step 6: the WebSocket route and the app factory

The socket validates the token **and** the membership before accepting. It opens a short session just for the check, so it does not hold a database connection for the lifetime of the socket.

```python file=taskapp/app/routers/ws.py
# app/routers/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.deps import find_membership, user_from_token
from app.realtime import team_room

router = APIRouter(tags=["realtime"])

@router.websocket("/ws/teams/{team_id}")
async def team_socket(websocket: WebSocket, team_id: int, token: str = ""):
    state = websocket.app.state
    async with state.sessionmaker() as session:                  # short-lived: closed before we start listening
        user = await user_from_token(token, session, state.settings)
        allowed = user is not None and await find_membership(session, user.id, team_id) is not None
    if not allowed:
        await websocket.close(code=1008)                         # policy violation: never accepted
        return
    room = team_room(team_id)
    await state.manager.connect(room, websocket)
    try:
        while True:
            await websocket.receive_text()                       # ignore client chatter; keep the socket open
    except WebSocketDisconnect:
        state.manager.disconnect(room, websocket)
```

```python file=taskapp/app/main.py
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import Settings
from app.database import make_engine, make_sessionmaker
from app.models import Base
from app.realtime import ConnectionManager
from app.routers import auth, tasks, teams, ws

def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        engine = make_engine(settings.database_url)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)        # development/tests; use Alembic in production
        app.state.settings = settings
        app.state.sessionmaker = make_sessionmaker(engine)
        app.state.manager = ConnectionManager()
        yield
        await engine.dispose()

    app = FastAPI(title="TaskFlow", version="1.0.0", lifespan=lifespan)
    for module in (auth, teams, tasks, ws):
        app.include_router(module.router)

    @app.get("/health", tags=["meta"])
    async def health():
        return {"status": "ok"}

    return app
```

Run with the factory pattern: `uvicorn app.main:create_app --factory` (with `APP_SECRET_KEY` set in the environment). The routers directory needs an empty `__init__.py`.

### Step 7: the tests

`conftest.py` builds a **fresh app with a fresh in-memory database per test**. `signup` is a helper that registers and logs in, returning headers and the user id. The tests are the business spec from the start of the section.

```python file=taskapp/pytest.ini
[pytest]
pythonpath = .
testpaths = tests
```

```python file=taskapp/tests/conftest.py
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

@pytest.fixture
def client():
    settings = Settings(database_url="sqlite+aiosqlite://", secret_key="t" * 40)     # in-memory
    with TestClient(create_app(settings)) as c:
        yield c

@pytest.fixture
def signup(client):
    def _signup(name):
        email = f"{name}@example.com"
        user = client.post("/auth/register", json={"email": email, "name": name, "password": "password123"}).json()
        token = client.post("/auth/login", json={"email": email, "password": "password123"}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}, user["id"], token
    return _signup

@pytest.fixture
def team(client, signup):
    """Asha owns a team that Ben has joined. Returns (team_id, asha, ben, cara) where cara is an outsider."""
    asha, ben, cara = signup("asha"), signup("ben"), signup("cara")
    team_id = client.post("/teams", json={"name": "Core"}, headers=asha[0]).json()["id"]
    client.post(f"/teams/{team_id}/members", json={"email": "ben@example.com"}, headers=asha[0])
    return team_id, asha, ben, cara
```

```python file=taskapp/tests/test_taskflow.py
# tests/test_taskflow.py
import pytest
from starlette.websockets import WebSocketDisconnect

def test_register_never_returns_the_hash(client):
    r = client.post("/auth/register", json={"email": "A@Example.com", "name": "A", "password": "password123"})
    assert r.status_code == 201
    assert set(r.json()) == {"id", "email", "name"}, "response must expose only id, email, name (no password_hash)"
    assert r.json()["email"] == "a@example.com", "emails should be normalised to lower case"

def test_bad_registration_is_422(client):
    body = {"email": "a@example.com", "name": "A", "password": "short"}
    assert client.post("/auth/register", json=body).status_code == 422, "passwords under 8 characters are invalid"

def test_wrong_password_and_missing_token_are_401(client, signup):
    signup("asha")
    assert client.post("/auth/login", json={"email": "asha@example.com", "password": "nope-nope"}).status_code == 401
    assert client.get("/teams").status_code == 401, "no token must be 401"

def test_outsider_sees_404_not_403(client, team):
    team_id, asha, ben, cara = team
    assert client.get(f"/teams/{team_id}/tasks", headers=cara[0]).status_code == 404, "hide teams from non-members"

def test_only_owner_adds_members(client, team):
    team_id, asha, ben, cara = team
    r = client.post(f"/teams/{team_id}/members", json={"email": "cara@example.com"}, headers=ben[0])
    assert r.status_code == 403, "a plain member must not add members"

def test_task_lifecycle_and_pagination(client, team):
    team_id, asha, ben, cara = team
    url = f"/teams/{team_id}/tasks"
    for i in range(5):
        assert client.post(url, json={"title": f"task {i}"}, headers=ben[0]).status_code == 201
    page = client.get(url, params={"limit": 2, "offset": 2}, headers=asha[0]).json()
    assert page["total"] == 5 and [t["title"] for t in page["items"]] == ["task 2", "task 3"]
    first = page["items"][0]["id"]
    r = client.patch(f"{url}/{first}", json={"status": "done"}, headers=asha[0])
    assert r.json()["status"] == "done" and r.json()["title"] == "task 2", "PATCH must keep fields it did not receive"
    assert client.get(url, params={"status": "done"}, headers=asha[0]).json()["total"] == 1
    assert client.patch(f"{url}/{first}", json={"status": "weird"}, headers=asha[0]).status_code == 422

def test_task_ids_do_not_cross_teams(client, team):
    team_id, asha, ben, cara = team
    task_id = client.post(f"/teams/{team_id}/tasks", json={"title": "secret"}, headers=asha[0]).json()["id"]
    other = client.post("/teams", json={"name": "Cara's"}, headers=cara[0]).json()["id"]
    r = client.patch(f"/teams/{other}/tasks/{task_id}", json={"title": "hacked"}, headers=cara[0])
    assert r.status_code == 404, "a task id must only be reachable through its own team"

def test_delete_rules(client, team):
    team_id, asha, ben, cara = team
    url = f"/teams/{team_id}/tasks"
    ashas = client.post(url, json={"title": "a"}, headers=asha[0]).json()["id"]
    bens = client.post(url, json={"title": "b"}, headers=ben[0]).json()["id"]
    assert client.delete(f"{url}/{ashas}", headers=ben[0]).status_code == 403, "member deleting someone else's task"
    assert client.delete(f"{url}/{bens}", headers=ben[0]).status_code == 204, "creator may delete"
    assert client.delete(f"{url}/{ashas}", headers=asha[0]).status_code == 204, "owner may delete"

def test_realtime_updates(client, team):
    team_id, asha, ben, cara = team
    with client.websocket_connect(f"/ws/teams/{team_id}?token={asha[2]}") as ws:
        task = client.post(f"/teams/{team_id}/tasks", json={"title": "ship"}, headers=ben[0]).json()
        assert ws.receive_json() == {"event": "task.created", "task": task}
        client.patch(f"/teams/{team_id}/tasks/{task['id']}", json={"status": "doing"}, headers=ben[0])
        assert ws.receive_json()["task"]["status"] == "doing"
        client.delete(f"/teams/{team_id}/tasks/{task['id']}", headers=ben[0])
        assert ws.receive_json() == {"event": "task.deleted", "task_id": task["id"]}

def test_websocket_rejects_outsiders_and_bad_tokens(client, team):
    team_id, asha, ben, cara = team
    for token in (cara[2], "garbage", ""):
        with pytest.raises(WebSocketDisconnect) as info:
            with client.websocket_connect(f"/ws/teams/{team_id}?token={token}"):
                pass
        assert info.value.code == 1008
```

```bash run
touch taskapp/app/__init__.py taskapp/app/routers/__init__.py taskapp/tests/__init__.py
cd taskapp && python -m pytest -q -p no:cacheprovider 2>&1 | tail -3
```
```text
..........                                                                                   [100%]
10 passed
```

All green with no warnings. If a test fails on your machine, read the assertion message: each one names the likely mistake.

### Step 8: what you built

```bash run
cd taskapp && find . -name "*.py" -o -name "*.ini" | grep -v -e __pycache__ -e __init__ | sort | sed 's|^\./|  |' | paste -sd' ' | fold -s -w 90
python - <<'PY'
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app
spec = TestClient(create_app(Settings(database_url="sqlite+aiosqlite://", secret_key="t"*40))).get("/openapi.json").json()
print("; ".join(f"{','.join(m.upper() for m in ops)} {path}" for path, ops in sorted(spec["paths"].items())))
PY
```
```text
  app/config.py   app/database.py   app/deps.py   app/main.py   app/models.py
app/realtime.py   app/routers/auth.py   app/routers/tasks.py   app/routers/teams.py
app/routers/ws.py   app/schemas.py   app/security.py   pytest.ini   tests/conftest.py
tests/test_taskflow.py
POST /auth/login; POST /auth/register; GET /health; GET,POST /teams; POST /teams/{team_id}/members; POST,GET /teams/{team_id}/tasks; PATCH,DELETE /teams/{team_id}/tasks/{task_id}
```

Ideas to extend it (good practice problems): refresh tokens; `selectinload` plus a `GET /teams/{id}` returning members; an Alembic migration instead of `create_all`; cursor pagination; request-id middleware; Redis pub/sub so several workers share rooms; rate limiting on `/auth/login`.

## 23. Flask, FastAPI and Django compared

| | Flask | FastAPI | Django |
|---|---|---|---|
| Style | micro-framework, bring your own parts | API-first, type-driven | full-stack, "batteries included" |
| Protocol | WSGI (async limited) | ASGI, async first | WSGI and ASGI |
| Validation | by hand or extensions | built in (Pydantic) | forms/serializers (DRF) |
| Docs | extensions | automatic OpenAPI | extensions (DRF) |
| ORM | none (SQLAlchemy usual) | none (SQLAlchemy/SQLModel usual) | built-in ORM, migrations, admin |
| Auth, admin, templates | extensions | you build it (templates available) | built in |
| WebSockets | extensions | built in | Channels add-on |
| Best for | small apps, learning, custom stacks | JSON APIs, microservices, real-time | content sites, admin-heavy apps, fast CRUD |

Choose by the job: a JSON API consumed by a front end or mobile app favours FastAPI; a site with admin screens, user accounts and forms favours Django; Flask fits when you want to choose every part. The concepts you learned (HTTP, validation, DI, ORM sessions, tokens) transfer between all three.

## 24. Common traps

1. **Blocking call inside `async def`** (`time.sleep`, `requests`, a sync DB driver). Everything freezes. Use `def`, `await` an async library, or `run_in_threadpool` (section 10).
2. **Returning the database model or reusing the input model for output.** Leaks `password_hash` and internal fields. Always declare a `response_model` (7.2).
3. **`MissingGreenlet`** on a relationship in async code. Load it up front with `selectinload`/`joinedload` (11.5).
4. **Forgetting `expire_on_commit=False`** and then reading attributes after `commit()` in async code.
5. **Forgetting `with TestClient(app) as client`** when the app uses a lifespan: the tables are never created, so every test fails with "no such table".
6. **Forgetting `return v`** in a `field_validator`: the field silently becomes `None` (5.5).
7. **PATCH that overwrites unsent fields** because `exclude_unset=True` was not used (7.5).
8. **`int | None` thought of as optional.** Without `= None` it is required (5.2).
11. **`dependency_overrides` left set** after a test; clear it in the fixture (9.6, 20.1).
12. **`allow_origins=["*"]` with credentials**, or thinking CORS protects the server. It protects the browser user (13.2).
13. **JWT without `exp`**, a short or hard-coded secret, or `decode` without `algorithms=[...]` (12.2).
15. **Looking a task up by id alone** instead of "id within the team in the URL": a classic insecure direct object reference (22).
16. **Sharing one `AsyncSession` between concurrent tasks**, or keeping a session open for the whole life of a WebSocket.
17. **WebSocket state in a module variable with several worker processes.** Each process sees only its own clients (15, 21).
19. **`--reload` or `create_all` in production**; use a real server config and migrations (21).
20. **Assuming `/docs` works offline**: the page loads its JavaScript from a CDN (19.2).

## 25. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| `422` with `loc: ["body", ...]` | the JSON does not match the model | section 6 |
| `422` with `loc: ["query", ...]` | a missing or invalid query parameter | 3.1 |
| `422` after adding a second body parameter | the body now needs one key per parameter name | 4.2 |
| `500` plus `ResponseValidationError` | the returned value does not fit `response_model` | 7.1 |
| `405` | path exists, method does not | 6.1 |
| `401` vs `403` confusion | unknown caller vs not allowed | 12.3 |
| `MissingGreenlet` | lazy load in async code | 11.5 |
| `no such table` in tests | lifespan not run: use `with TestClient(...)` | 20.1 |
| `Form data requires "python-multipart"` | multipart package not installed | 16 |
| CORS error in the browser, 200 in the log | origin not allowed | 13.2 |
| `/docs` blank offline | CDN assets unreachable | 19.2 |
| everything slow under load | blocking call inside `async def` | 10.2 |

## 26. Summary

- **ASGI** is the async contract `app(scope, receive, send)`; uvicorn serves it, Starlette is the toolkit, Pydantic validates, FastAPI joins them.
- Parameters come from the **signature** (path, query, body, `Header`, `Cookie`), constrained with `Annotated`, `Query`, `Path`, `Field`.
- **Pydantic v2** checks hints at runtime: constraints, validators, lax versus strict, nested and discriminated unions, `model_dump`, `from_attributes`, aliases.
- **Validation happens before your function runs.** A **422** means the data broke the declared rules; its body lists every problem as `type`, `loc`, `msg`, `input`.
- Separate **input, storage and output** models; `response_model` keeps secrets in. `HTTPException` and handlers shape errors.
- **Dependency injection** (`Depends`, `yield`, per-request cache, `dependency_overrides`) carries sessions, users and permissions, and makes testing easy.
- `async def` only for awaited work, `def` for blocking work. Async SQLAlchemy needs eager loading, `expire_on_commit=False` and a lifespan.
- Auth: slow salted hashes, JWT with `exp` and a long secret, `401` versus `403`, ownership checks in dependencies.
- Middleware, CORS, background tasks, WebSockets with a connection manager, routers, environment settings, generated OpenAPI docs.
- Test with `TestClient`, fixtures, in-memory SQLite and `dependency_overrides`. Structure big apps as `routers / schemas / models / deps`, built by an app factory.

Next: the 50 problems for this module practise each section: reading 422 bodies, writing validators, building dependencies, async CRUD, auth, WebSockets and tests.

