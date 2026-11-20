## Approach

```python
def is_preflight():
    return (request.method == "OPTIONS" and "Origin" in request.headers
            and "Access-Control-Request-Method" in request.headers)


@app.before_request
def answer_preflight():
    if request.path.startswith("/api/") and is_preflight():
        return make_response("", 204)


@app.after_request
def add_cors_headers(response):
    if not request.path.startswith("/api/"):
        return response
    response.headers.add("Vary", "Origin")
    origin = request.headers.get("Origin")
    if origin and origin in app.config["CORS_ORIGINS"]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        if is_preflight():
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response.headers["Access-Control-Max-Age"] = "600"
    return response
```

Example: the browser, before it sends a `POST` with JSON from `https://app.example`, first sends `OPTIONS /api/posts` with `Origin` and `Access-Control-Request-Method: POST`. The answer says "yes, this origin, these methods, for ten minutes (`Max-Age`)". Only then does the browser send the real `POST`.

Why the exact match? `"https://app.example.evil.com".startswith("https://app.example")` is true. A wildcard `*` is refused by browsers when credentials (cookies) are involved, and echoing *any* origin back is the same as `*` with credentials: every website could then read your logged-in users' data.

**Vary: Origin** tells shared caches that the answer depends on the `Origin` request header; without it a CDN could serve an answer with `Allow-Origin: https://one.example` to a request from `https://two.example`.

CORS is a **browser** rule. `curl`, scripts and attackers' servers ignore it completely, so it never replaces authentication or authorisation.

## Complexity

`O(number of allowed origins)` per request.

## Another way

The `flask-cors` extension does this with more options. Or avoid CORS: serve the front end and the API from the **same origin** (one domain, the proxy routing `/api/` to Flask).

## Not covered

`Access-Control-Expose-Headers` (so JavaScript can read custom response headers) and dynamic origins from a database.
